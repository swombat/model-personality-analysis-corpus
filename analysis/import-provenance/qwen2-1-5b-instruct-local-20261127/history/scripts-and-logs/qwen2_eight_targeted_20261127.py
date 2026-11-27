"""Scoped Qwen2 (not 2.5) essay-only successor; offline replay before retries."""
import sys
sys.dont_write_bytecode = True
import fcntl, hashlib, importlib, json, shutil, sqlite3, time
from pathlib import Path
from gemma2_short17_targeted import sha, manifest
from replay_v13_candidates import module
from audit_short_readings import short_check

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/"continuation_batch_v13_qwen2-1-5b-instruct_offline_short_20261127"
ORIGINAL = ROOT/"continuation_batch_v13_qwen2-1-5b-instruct"
OLD = ROOT/"remaining_recovery_colab-qwen2-1-5b-instruct"
DEST = ROOT/"qwen2_eight_targeted_20261127"
HARNESS = ROOT.parent/"colab-publication-intake/scripts/capture_harness"
MODEL = "qwen2-1-5b-instruct-colab-vllm-bf16-r2ebb13f1"
IDS = json.loads((SOURCE/"terminal.json").read_text())["remaining_ids"]
CHECK = short_check()
def write(p,obj):
    p.write_text(json.dumps(obj,indent=2)+"\n")
class InfrastructureStop(BaseException): pass

def inspect_attempt(p, job):
    rec = json.loads(p.read_text())
    sid = job.split("/")[-1]
    src = ROOT/"raw/data/traces_freeflow"/("freeflow_"+MODEL)/(sid+".json")
    sample = json.loads(src.read_text())
    name = "luna_v1_targeted" if "targeted" in rec["arm"] else "luna_v1"
    v = module(SOURCE/"analysis/analysis/freeflow/personality-eval-bv1"/(name+".py"))
    if not v.BV.PROMPT_PATH.exists():
        v.BV.PROMPT_PATH = ROOT/"analysis-worktree"/v.BV.PROMPT_PATH.relative_to(OLD/"analysis")
    assert rec["arm"] == v.ARM
    assert rec["source_sha256"] == sha(src)
    assert rec["sample_id"] == MODEL+"/"+sid+".json"
    assert rec["request"] == v.payload(dict(text=sample["result"],condition=sample["condition"]))
    assert v.transport_valid(rec["http_status"],rec["response"]), "Ambiguous saved transport"
    text = rec["response"]["choices"][0]["message"]["content"]
    result = CHECK(text,sample["result"],None,None)
    return dict(job=job,path=str(p),sha256=sha(p),source=str(src),
                source_sha256=sha(src),result=result,transport_valid=True), text

def adopt(db, job, p, proof, text):
    out = DEST/"accepted_offline"/job.split("/")[-1]
    out.mkdir(parents=True,exist_ok=False)
    (out/"reading.md").write_text(text)
    shutil.copyfile(p,out/"generation_attempt.json")
    proof.update(output_sha256=sha(out/"reading.md"),model_calls=0,
                 validator="approved-short-or-strict-offline",generation_arm=json.loads(p.read_text())["arm"])
    write(out/"validation.json",proof)
    receipts = {str(q):sha(q) for q in out.iterdir()}
    with db:
        assert db.execute("update jobs set state='done',reason=?,receipts=?,pid=NULL where id=? and state='blocked'",
            ("offline accepted saved response; original generation arm preserved",json.dumps(receipts),job)).rowcount == 1
        db.execute("insert into events values(?,?,?,?)",(time.time(),job,"offline_accepted",json.dumps(proof)))

def main():
    with (ROOT/"state/host-supervisor.lock").open() as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not DEST.exists()
        assert not (ROOT.parent/"corpus-ops/STOP").exists()
        assert len(IDS)==8 and all(j.startswith(MODEL+"/bv1/") for j in IDS)
        before = {str(p):manifest(p) for p in (SOURCE,ORIGINAL,OLD)}
        ready = json.loads((SOURCE/"ready.json").read_text())
        assert all(sha(HARNESS/n)==h for n,h in ready["harness_hashes"].items())
        checks, valid = [], {}
        # Include every saved attempt across ancestral lanes, deduplicating bytes.
        for job in IDS:
            sid = job.split("/")[-1]
            seen = set()
            for lane in (SOURCE,ORIGINAL,OLD):
                for p in sorted((lane/"phase").glob("freeflow_bv1_*/attempt_responses/*_BV1_"+sid+"/*.json")):
                    if sha(p) in seen: continue
                    seen.add(sha(p))
                    proof,text = inspect_attempt(p,job)
                    checks.append(proof)
                    if proof["result"] in ("sentence","pass_short"):
                        valid.setdefault(job,(p,proof,text))
            assert seen, job
        shutil.copytree(SOURCE,DEST,ignore=shutil.ignore_patterns("state.sqlite*","repair.lock"))
        (DEST/"terminal.json").rename(DEST/"inherited_offline_terminal.json")
        def move(s):
            for p in (SOURCE,ORIGINAL,OLD): s=s.replace(str(p),str(DEST))
            return s
        with sqlite3.connect(f"file:{SOURCE}/state.sqlite?mode=ro",uri=True) as src, sqlite3.connect(DEST/"state.sqlite") as db:
            src.backup(db)
            spec=json.loads(move((SOURCE/"spec.json").read_text()))
            cfg=json.loads(move((SOURCE/"config.json").read_text()))
            write(DEST/"config.json",cfg)
            spec["input_hashes"][str(DEST/"config.json")]=sha(DEST/"config.json")
            write(DEST/"spec.json",spec)
            assert all(sha(p)==h for p,h in spec["input_hashes"].items())
            for job,r in db.execute("select id,receipts from jobs where state='done'").fetchall():
                r=json.loads(move(r))
                assert all(sha(p)==h for p,h in r.items())
                db.execute("update jobs set receipts=? where id=?",(json.dumps(r),job))
            db.execute("update meta set v=? where k='spec'",(hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest(),))
            ledger=db.execute("select * from targeted_repairs").fetchall()
            assert {r[0] for r in db.execute("select id from jobs where id like '%/bv1/%' and state!='done'")}==set(IDS)
            db.commit()
            write(DEST/"eight-authorization.json",dict(ids=IDS,saved_checks=checks,inherited_ledger=ledger,
                source_manifest=before,authorization=ready["authorization"],limit=ready["limit"]))
            for job,args in valid.items(): adopt(db,job,*args)
        sys.path.insert(0,str(HARNESS))
        worker=importlib.import_module("worker")
        worker.RAW=ROOT/"raw"
        original=worker.bv1
        def guard(c,phase,sid,*args,**kw):
            if (ROOT.parent/"corpus-ops/STOP").exists(): raise InfrastructureStop("STOP")
            try: return original(c,phase,sid,*args,**kw)
            except Exception as exc:
                if not str(exc).startswith("BV1-Luna targeted QA: ") or "transport_finish_provider_or_model" in str(exc):
                    raise InfrastructureStop(str(exc)) from exc
                # Prevent apply's internal retry before accepted offline checks.
                raise InfrastructureStop("QA_REQUIRES_OFFLINE_REVIEW: "+str(exc)) from exc
        worker.bv1=guard
        targeted=importlib.import_module("apply_bv1_targeted")
        results,error=[],None
        try:
            for job in IDS:
                while True:
                    with sqlite3.connect(DEST/"state.sqlite") as db:
                        if db.execute("select state from jobs where id=?",(job,)).fetchone()[0]=="done": break
                        row=db.execute("select used,allowance from targeted_repairs where authorization=? and id=?",(ready["authorization"],job)).fetchone()
                        if row and row[0]>=row[1]: break
                    try:
                        results.extend(targeted.apply(DEST/"spec.json",DEST,[job],ready["authorization"],ready["limit"]))
                        break
                    except InfrastructureStop as exc:
                        if not str(exc).startswith("QA_REQUIRES_OFFLINE_REVIEW:"): raise
                        paths=sorted((DEST/"phase/freeflow_bv1_luna_v1_targeted/attempt_responses").glob("*_BV1_"+job.split("/")[-1]+"/*.json"))
                        assert paths
                        p=paths[-1]
                        proof,text=inspect_attempt(p,job)
                        checks.append(proof)
                        write(DEST/"targeted-offline-checks.json",checks)
                        if proof["result"] in ("sentence","pass_short"):
                            with sqlite3.connect(DEST/"state.sqlite") as db: adopt(db,job,p,proof,text)
                            break
        except BaseException as exc:
            error=str(exc)
        finally:
            with sqlite3.connect(DEST/"state.sqlite") as db:
                rows=db.execute("select id,state,reason,receipts from jobs where id like '%/bv1/%'").fetchall()
                for _,state,_,r in rows:
                    if state=="done": assert all(sha(p)==h for p,h in json.loads(r).items())
                spent=db.execute("select * from targeted_repairs").fetchall()
            unchanged=all(manifest(Path(p))==m for p,m in before.items())
            result=dict(terminal_path=str(DEST/"terminal.json"),bv1_done=sum(r[1]=="done" for r in rows),
                bv1_total=125,remaining_ids=[r[0] for r in rows if r[1]!="done"],ledger=spent,
                inherited_ledger=ledger,saved_and_targeted_checks=checks,results=results,error=error,
                source_unchanged=unchanged,downstream_run=False,published=False,scheduler_enabled=False)
            write(DEST/"terminal.json",result)
            assert unchanged
            print(json.dumps(result),flush=True)
if __name__=="__main__": main()
