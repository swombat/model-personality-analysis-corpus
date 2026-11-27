"""Three-root isolated successor; inherited authorization, offline checks first."""
import sys
sys.dont_write_bytecode = True
import fcntl, hashlib, importlib, importlib.util, json, shutil, sqlite3
from pathlib import Path
from gemma2_short17_targeted import sha, manifest, write

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/"continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127"
ORIGINAL = ROOT/"continuation_batch_v13_qwen1-5-32b-chat"
OLD = ROOT/"remaining_recovery_colab-qwen1-5-32b-chat"
DEST = ROOT/"qwen32_three_targeted_20261127"
HARNESS = ROOT.parent/"colab-publication-intake/scripts/capture_harness"
MODEL = "qwen1-5-32b-chat-colab-vllm-bf16-r0997b012"
IDS = [MODEL+"/bv1/"+s for s in ("MID_2", "MID_22", "SHORT_14")]

class InfrastructureStop(BaseException):
    pass

def main():
    with (ROOT/"state/host-supervisor.lock").open() as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not (ROOT.parent/"corpus-ops/STOP").exists()
        if sys.argv[1:] == ["--resume-initialized"]:
            auth = json.loads((DEST/"three-authorization.json").read_text())
            assert not (DEST/"three-preflight.json").exists()
            assert not (DEST/"terminal.json").exists()
            assert all(manifest(Path(p))==m for p,m in auth["source_manifest"].items())
            with sqlite3.connect(DEST/"state.sqlite") as db:
                assert db.execute("select * from targeted_repairs").fetchall() == [tuple(r) for r in auth["inherited_ledger"]]
                assert not db.execute("select 1 from events where id in (?,?,?) and event='bv1_targeted_repair_started'",IDS).fetchall()
            execute(auth["source_manifest"])
            return
        assert not DEST.exists(), "Never reset/refill an existing lane"
        before = {str(p): manifest(p) for p in (SOURCE, ORIGINAL, OLD)}
        ready = json.loads((SOURCE/"ready.json").read_text())
        assert json.loads((SOURCE/"terminal.json").read_text())["bv1_done"] == 122
        assert all(sha(HARNESS/n) == h for n,h in ready["harness_hashes"].items())
        # Re-evaluate every saved original answer for these roots, with the
        # approved v1.3 validator, without entering any generation path.
        code = SOURCE/"offline_validator"
        module = importlib.util.spec_from_file_location("qwen32_saved_validator", code/"luna_v1_3.py")
        validator = importlib.util.module_from_spec(module)
        module.loader.exec_module(validator)
        audit = json.loads((ROOT/"offline-three-eligible-audit-0944.json").read_text())["qwen1-5-32b-chat"]
        checks = []
        for job in IDS:
            sid = job.split("/")[-1]
            src = ROOT/"raw/data/traces_freeflow"/("freeflow_"+MODEL)/(sid+".json")
            attempts = list((SOURCE/"phase/freeflow_bv1_luna_v1/attempt_responses").glob("*_BV1_"+sid+"/*.json"))
            assert {sha(p) for p in attempts} == {a["sha256"] for a in audit[job]}
            for p in attempts:
                rec = json.loads(p.read_text())
                assert rec["source_sha256"] == sha(src)
                transport = validator.transport_valid(rec["http_status"], rec["response"])
                valid, reason = validator.valid_output(rec["response"]["choices"][0]["message"]["content"], json.loads(src.read_text())["result"])
                checks.append(dict(id=job,path=str(p),sha256=sha(p),transport_valid=transport,valid=valid,reason=reason))
                assert transport, "Saved transport ambiguity"
                assert not valid, "Saved valid answer requires offline adoption, not generation"
        shutil.copytree(SOURCE, DEST, ignore=shutil.ignore_patterns("state.sqlite*", "repair.lock"))
        (DEST/"terminal.json").rename(DEST/"inherited_offline_terminal.json")
        with sqlite3.connect(f"file:{SOURCE}/state.sqlite?mode=ro", uri=True) as src, sqlite3.connect(DEST/"state.sqlite") as db:
            src.backup(db)
            def move(s):
                return s.replace(str(SOURCE),str(DEST)).replace(str(ORIGINAL),str(DEST)).replace(str(OLD),str(DEST))
            spec = json.loads(move((SOURCE/"spec.json").read_text()))
            cfg = json.loads(move((SOURCE/"config.json").read_text()))
            (DEST/"config.json").write_text(json.dumps(cfg,indent=2)+"\n")
            spec["input_hashes"][str(DEST/"config.json")] = sha(DEST/"config.json")
            (DEST/"spec.json").write_text(json.dumps(spec,indent=2)+"\n")
            assert all(sha(p)==h for p,h in spec["input_hashes"].items())
            assert all(sha(DEST/n)==h for n,h in ready["bv1_code_hashes"].items())
            for job, receipts in db.execute("select id,receipts from jobs where state='done'").fetchall():
                receipts = json.loads(move(receipts))
                assert all(sha(p)==h for p,h in receipts.items()), job
                db.execute("update jobs set receipts=? where id=?",(json.dumps(receipts),job))
            db.execute("update meta set v=? where k='spec'",(hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest(),))
            assert db.execute("select count(*) from jobs where id like '%/bv1/%' and state='done'").fetchone()[0] == 122
            assert {r[0] for r in db.execute("select id from jobs where id like '%/bv1/%' and state!='done'")} == set(IDS)
            ledger = db.execute("select * from targeted_repairs").fetchall()
            assert not any(r[1] in IDS for r in ledger), "Prior spend requires review"
            assert not db.execute("select 1 from events where id in (?,?,?) and event='bv1_targeted_repair_started'",IDS).fetchall()
        write(DEST/"three-authorization.json",dict(ids=IDS,authorization=ready["authorization"],limit=ready["limit"],inherited_ledger=ledger,source_manifest=before,saved_checks=checks,scheduler_enabled=False))
        execute(before)

def execute(before):
        ready = json.loads((SOURCE/"ready.json").read_text())
        sys.path.insert(0,str(HARNESS))
        worker = importlib.import_module("worker")
        worker.RAW = ROOT/"raw"
        original = worker.bv1
        def guarded(*args,**kwargs):
            if (ROOT.parent/"corpus-ops/STOP").exists():
                raise InfrastructureStop("STOP")
            try:
                return original(*args,**kwargs)
            except Exception as exc:
                if str(exc).startswith("BV1-Luna targeted QA: ") and "transport_finish_provider_or_model" not in str(exc):
                    raise
                raise InfrastructureStop(str(exc)) from exc
        worker.bv1 = guarded
        targeted = importlib.import_module("apply_bv1_targeted")
        write(DEST/"three-preflight.json",targeted.apply(DEST/"spec.json",DEST,IDS,ready["authorization"],ready["limit"],check_only=True))
        results, error = [], None
        try:
            for job in IDS:
                results.extend(targeted.apply(DEST/"spec.json",DEST,[job],ready["authorization"],ready["limit"]))
        except BaseException as exc:
            error = str(exc)
            raise
        finally:
            unchanged = all(manifest(Path(p))==m for p,m in before.items())
            with sqlite3.connect(DEST/"state.sqlite") as db:
                rows = db.execute("select id,state,reason,receipts from jobs where id in (?,?,?)",IDS).fetchall()
                spent = db.execute("select * from targeted_repairs").fetchall()
                done = db.execute("select count(*) from jobs where id like '%/bv1/%' and state='done'").fetchone()[0]
                for _,state,_,receipts in rows:
                    if state=="done":
                        assert all(sha(p)==h for p,h in json.loads(receipts).items())
            write(DEST/"terminal.json",dict(results=results,error=error,rows=rows,ledger=spent,bv1_done=done,bv1_total=125,source_unchanged=unchanged,downstream_run=False,published=False))
            assert unchanged
            print(json.dumps(dict(path=str(DEST),bv1_done=done,error=error,ledger=spent)),flush=True)

if __name__ == "__main__":
    main()
