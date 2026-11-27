"""Qwen2 1.5B only: receipt-first isolated synthesis and local integration."""
import sys
sys.dont_write_bytecode=True
import json, os, shutil, socket, sqlite3, hashlib
from pathlib import Path
import qwen18_values_authorized as common
from gemma2_values_through_report import put
from gemma2_short17_targeted import sha, manifest
from audit_short_readings import short_check
b=common.b
SOURCE=b.ROOT/"qwen2_eight_targeted_20261127"
DEST=b.ROOT/"qwen2_final_20261127b"

def main():
    with b.lock():
        contract=b.load(b.ROOT/"contract.json")
        common.qa.preflight(contract,armed=True)
        assert not (b.ROOT.parent/"corpus-ops/STOP").exists()
        resume=DEST.exists()
        if resume:
            assert b.load(DEST/"STOPPED.json")["error"]=="evaluation path outside repository"
            assert not (DEST/"PRECALL.json").exists()
        old=b.load(SOURCE/"config.json")
        assert old["model"]=="Qwen/Qwen2-1.5B-Instruct"
        assert b.load(SOURCE/"terminal.json")["bv1_done"]==125
        src=sqlite3.connect(f"file:{SOURCE}/state.sqlite?mode=ro",uri=True)
        rows=src.execute("select id,state,attempts,receipts from jobs").fetchall()
        pending=[r for r in rows if r[1]!="done"]
        assert {r[0].split("/")[-1] for r in pending}=={"synthesis","queue-ready"}
        assert all(r[2]==0 for r in pending)
        verified=0
        for id,state,attempts,rec in rows:
            if state=="done":
                assert rec
                for p,h in json.loads(rec).items():
                    assert sha(p)==h,(id,p)
                    verified+=1
        frozen={str(p):manifest(p) for p in (SOURCE,b.ROOT/"raw")}
        if not resume:
            DEST.mkdir()
            put(DEST/"source-receipts-verified.json",dict(receipts=verified,jobs=len(rows)-2,
                terminal_sha256=sha(SOURCE/"terminal.json"),frozen=frozen))
        root=DEST/"analysis"
        if not resume:
            shutil.copytree(b.WORKTREE,root,ignore=shutil.ignore_patterns(".git","__pycache__"))
            shutil.copytree(SOURCE/"analysis",root,dirs_exist_ok=True)
        phase=root/"analysis/values-probe/model-coding/layered/capture_qwen2_final_20261127"
        if not resume:shutil.copytree(SOURCE/"phase",phase)
        for rel in ("analysis/values-probe/final/scripts/integrate_capture_values.py",
                    "website/scripts/generate_data.py","website/src/generated/models.json",
                    "internal/scripts/analysis-scripts/_corpus_paths.py",
                    "internal/scripts/analysis-scripts/values_probe_extract.py"):
            p=root/rel;data=b.git(b.ANALYSIS,"show",contract["analysis_commit"]+":"+rel)
            assert not p.exists() or p.read_bytes()==data
            p.parent.mkdir(parents=True,exist_ok=True)
            if not p.exists():p.write_bytes(data)
        c=dict(old,analysis_root=str(root),phase=str(phase))
        if not resume:put(DEST/"config.json",c)
        spec=b.load(SOURCE/"spec.json")
        tasks={t["id"]:t for t in spec["tasks"]}
        if not resume:put(DEST/"inherited-spec.json",spec)
        db=sqlite3.connect(DEST/"state.sqlite")
        if not resume:src.backup(db)
        src.close()
        w=b.verified_worker(contract)
        w.validate_source_config(c)
        for probe in ("freeflow","values"):
            for sid in w.identities(probe):w.read_trace(c,probe,sid)
        original=w.bv1;check=short_check()
        offline={}
        for id,state,attempts,rec in rows:
            if "/bv1/" not in id:continue
            paths=[Path(p) for p in json.loads(rec)]
            reading=next((p for p in paths if p.name=="reading.md"),None)
            if reading:
                attempt=next(p for p in paths if p.name in {"generation_attempt.json","original_attempt.json"})
                offline[id.split("/")[-1]]=(reading,attempt)
        def read(config,ph,sid,validate=False,**kw):
            assert validate,"no essays"
            if sid not in offline:return original(config,ph,sid,True,**kw)
            reading,attempt=offline[sid];rec=b.load(attempt)
            source,digest=w.read_trace(config,"freeflow",sid)
            text=reading.read_text()
            assert rec["source_sha256"]==digest
            assert rec["response"]["choices"][0]["message"]["content"]==text
            assert rec["http_status"]==200 and rec["response"]["choices"][0]["finish_reason"]=="stop"
            assert check(text,source["result"],None,None) in {"sentence","pass_short"}
            arm=rec["arm"]
            copied=root/"offline_readings"/(sid+".md")
            copied.parent.mkdir(exist_ok=True)
            if not copied.exists():shutil.copyfile(reading,copied)
            assert sha(copied)==sha(reading)
            reading=copied
            bp=w.bv1_paths(config,ph,arm)[2]/(sid+".json")
            binding=dict(source_sha256=digest,output_sha256=sha(reading),evaluator_arm=arm)
            if bp.exists():
                assert all(b.load(bp)[k]==v for k,v in binding.items())
            else:put(bp,binding)
            return dict(pid=c["id_prefix"]+"_BV1_"+sid,model=c["model"],cell=c["label"],
                condition=source["condition"],provider=c["provider"],sample_id=c["label"]+"/"+sid+".json",
                word_count=len(source["result"].split()),source=str(w.trace_path(c,"freeflow",sid)),
                outpath=str(reading),text=source["result"],evaluator_arm=arm)
        w.bv1=read
        sockets=(socket.socket.connect,socket.socket.connect_ex,socket.create_connection)
        socket.socket.connect=socket.socket.connect_ex=socket.create_connection=common.forbidden
        try:
            assert w.bv1_ready_fields(c,phase)["bv1"]==125
            for f in (w.assemble_values,w.adjudicate,w.values_report):f(c,phase,True)
            if not resume:
                put(DEST/"offline-validation.json",dict(bv1=125,values=120,model_calls=0,
                    original_generation_arms_preserved=True,offline_samples=sorted(offline)))
        finally:socket.socket.connect,socket.socket.connect_ex,socket.create_connection=sockets
        loader=w.module
        def module(name,path):
            m=loader(name,path)
            if name=="capture_assembly":
                inner=m.module
                def load(n,p):
                    obj=inner(n,p)
                    if n=="phase35_aggregate":
                        def once(prompt,max_completion_tokens=4500,timeout=420):
                            assert not (DEST/"PRECALL.json").exists()
                            assert not (b.ROOT.parent/"corpus-ops/STOP").exists()
                            payload=dict(model="openai/gpt-5.4",provider=dict(only=["OpenAI"],allow_fallbacks=False),
                                messages=[dict(role="system",content=obj.SYSTEM),dict(role="user",content=prompt)],
                                max_tokens=max_completion_tokens,temperature=0.2)
                            put(DEST/"PRECALL.json",dict(request_sha256=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(),
                                maximum_requests=1,automatic_retry=False,status="dispatch_may_have_occurred"))
                            import httpx
                            response=httpx.post("https://openrouter.ai/api/v1/chat/completions",json=payload,
                                timeout=timeout,follow_redirects=False,headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"]})
                            with (DEST/"synthesis-response.body").open("xb") as f:
                                f.write(response.content);f.flush();os.fsync(f.fileno())
                            put(DEST/"synthesis-response-receipt.json",dict(status=response.status_code,sha256=sha(DEST/"synthesis-response.body")))
                            data=response.json();choice=(data.get("choices") or [{}])[0]
                            assert response.status_code==200 and data.get("provider")=="OpenAI"
                            assert data.get("model")==payload["model"] and choice.get("finish_reason")=="stop"
                            text=choice.get("message",{}).get("content") or ""
                            assert text.strip()
                            return text,data.get("usage",{})
                        obj.api_call=once
                    return obj
                m.module=load
            return m
        w.module=module
        os.environ.update(PERSONALITY_CELL_AGG_ROUTE="openrouter-openai",PERSONALITY_CELL_AGG_MODEL="gpt-5.4",
            COLAB_QUEUE_ARM=b.load(b.STATE/"active-arm.json")["nonce"])
        try:
            for suffix,func in (("synthesis",w.synthesis),("queue-ready",w.ready)):
                id=c["label"]+"/"+suffix
                used=db.execute("select attempts from jobs where id=?",(id,)).fetchone()[0]
                if resume and suffix=="synthesis":
                    assert used==1 and not (DEST/"PRECALL.json").exists()
                    put(DEST/"predispatch-local-path-repair.json",dict(existing_attempt=1,new_attempts=0,
                        reason="copy verified readings inside isolated repository; prior failure before dispatch"))
                else:
                    assert used<tasks[id]["max_attempts"]
                    put(DEST/(suffix+"-charged.json"),dict(task=id,attempt=used+1,max_attempts=tasks[id]["max_attempts"]))
                    db.execute("update jobs set attempts=attempts+1 where id=?",(id,));db.commit()
                if suffix=="queue-ready":socket.socket.connect=socket.socket.connect_ex=socket.create_connection=common.forbidden
                func(c,phase,False);func(c,phase,True)
                paths=([root/f"analysis/freeflow/personality-model-cards/cards/{c['slug']}.md",
                        root/f"analysis/freeflow/personality-model-profiles/profiles/{c['slug']}.md"] if suffix=="synthesis"
                       else [phase/"VALUES_CARD.json",phase/"CARD_READY.json",phase/"ANALYSIS_READY.json",
                             phase/f"release_candidate/reports/{c['slug']}.md"])
                receipts={str(p):sha(p) for p in paths}
                put(DEST/(suffix+"-verified.json"),dict(receipts=receipts,production_validation=True))
                db.execute("update jobs set state='done',receipts=?,reason='isolated local integration' where id=?",(json.dumps(receipts),id));db.commit()
            assert all(manifest(Path(p))==m for p,m in frozen.items())
            receipts={}
            for suffix in ("synthesis","queue-ready"):receipts.update(b.load(DEST/(suffix+"-verified.json"))["receipts"])
            put(DEST/"terminal.json",dict(state="integrated_card_ready_awaiting_publication",bv1=125,values=120,
                synthesis_requests=1,new_essays=0,duplicate_judgments=0,source_unchanged=True,
                original_generation_arms_preserved=True,inherited_attempt_limits_preserved=True,
                remote_writes=False,publication=False,receipts=receipts))
            print(DEST/"terminal.json",sha(DEST/"terminal.json"),flush=True)
        except BaseException as exc:
            put(DEST/("RESUME_STOPPED.json" if resume else "STOPPED.json"),dict(error=str(exc),automatic_retry=False,dispatch_may_have_occurred=(DEST/"PRECALL.json").exists()))
            raise
        finally:
            socket.socket.connect,socket.socket.connect_ex,socket.create_connection=sockets
            db.close()

if __name__=="__main__":main()
