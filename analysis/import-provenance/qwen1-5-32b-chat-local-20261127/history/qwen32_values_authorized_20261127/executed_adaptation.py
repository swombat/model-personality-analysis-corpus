"""Single-use Qwen1.8 CTRL3_2 continuation; inherited budgets, durable transport."""
import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, os, shutil, socket, sqlite3, subprocess
from pathlib import Path
import qa_short_continuation as qa
from gemma2_values_through_report import put
from gemma2_short17_targeted import manifest, sha

b = qa.base
SOURCE = b.ROOT/"qwen32_three_targeted_20261127"
DEST = b.ROOT/"qwen32_values_authorized_20261127"
MODEL = "qwen1-5-32b-chat-colab-vllm-bf16-r0997b012"

def forbidden(*a, **k):
    raise RuntimeError("offline: network forbidden")

def main():
    with b.lock():
        contract = b.load(b.ROOT/"contract.json")
        qa.preflight(contract, armed=True)
        assert not (b.ROOT.parent/"corpus-ops/STOP").exists()
        assert not DEST.exists(), "never reset/reenter a used lane"
        preflight = b.load(SOURCE/"terminal.json")
        assert preflight["bv1_done"] == 125 and preflight["error"] is None
        frozen = {str(p):manifest(p) for p in (SOURCE,b.ROOT/"raw",b.ROOT/"continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127",b.ROOT/"continuation_batch_v13_qwen1-5-32b-chat",b.ROOT/"remaining_recovery_colab-qwen1-5-32b-chat")}
        DEST.mkdir()
        put(DEST/"adaptation.json",dict(parent=str(parent),parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),
            adapter=str(Path(__file__)),adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            executed_sha256=hashlib.sha256(ADAPTED_SOURCE.encode()).hexdigest(),
            capture_child_sha256=sha(b.ROOT/"gemma2_values_capture_child.py")))
        (DEST/"executed_adaptation.py").write_text(ADAPTED_SOURCE)
        analysis = DEST/"analysis"
        shutil.copytree(b.WORKTREE, analysis, ignore=shutil.ignore_patterns(".git","__pycache__"))
        shutil.copytree(SOURCE/"analysis", analysis, dirs_exist_ok=True)
        phase = analysis/"analysis/values-probe/model-coding/layered/capture_qwen32_final_20261127"
        assert not phase.exists()
        shutil.copytree(SOURCE/"phase",phase)
        for rel in ("analysis/values-probe/final/scripts/integrate_capture_values.py",
                    "website/scripts/generate_data.py","website/src/generated/models.json",
                    "internal/scripts/analysis-scripts/_corpus_paths.py",
                    "internal/scripts/analysis-scripts/values_probe_extract.py"):
            p=analysis/rel
            data=b.git(b.ANALYSIS,"show",contract["analysis_commit"]+":"+rel)
            assert not p.exists() or p.read_bytes()==data
            p.parent.mkdir(parents=True,exist_ok=True)
            if not p.exists(): p.write_bytes(data)
        c=dict(b.load(SOURCE/"config.json"),analysis_root=str(analysis),phase=str(phase))
        put(DEST/"config.json",c)
        def move(s):
            return s.replace(str(SOURCE/"analysis"),str(analysis)).replace(str(SOURCE/"phase"),str(phase)).replace(str(SOURCE/"config.json"),str(DEST/"config.json"))
        spec=json.loads(move((SOURCE/"spec.json").read_text()))
        spec["input_hashes"][str(DEST/"config.json")]=sha(DEST/"config.json")
        put(DEST/"spec.json",spec)
        db=sqlite3.connect(DEST/"state.sqlite")
        with sqlite3.connect(f"file:{SOURCE}/state.sqlite?mode=ro",uri=True) as src: src.backup(db)
        for id,receipts in db.execute("select id,receipts from jobs where state='done'").fetchall():
            assert all(sha(p)==h for p,h in json.loads(receipts).items()),id
            moved=json.loads(move(receipts))
            assert all(sha(p)==h for p,h in moved.items()),id
            db.execute("update jobs set receipts=? where id=?",(json.dumps(moved),id))
        assert db.execute("select count(*) from jobs where id like '%/bv1/%' and state='done'").fetchone()==(125,)
        db.execute("update meta set v=? where k='spec'",(hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest(),))
        db.commit()
        tasks={t["id"]:t for t in spec["tasks"]}
        work={id for (id,) in db.execute("select id from jobs where state!='done'")}
        allowed={"a","ac","p","pc","values","adjudicate","values_report","synthesis","queue_ready"}
        assert len(work)==11
        assert all(tasks[id]["command"][3] in allowed for id in work)
        assert all("/CTRL3_2/" in id or id.endswith("/CTRL3_2") for id in work if tasks[id]["command"][3] in {"a","ac","p","pc"})
        put(DEST/"authorization.json",dict(
            scope="Qwen1.5 32B CTRL3_2 all originally configured coding layers and consensus; downstream report/synthesis/local integration",
            authorization="2026-11-27 explicit user clarification; inherited per-root budgets; no other samples, remote writes, posts or delegation",
            jobs=sorted(work),inherited=[list(r) for r in db.execute("select id,state,attempts,reason from jobs where state!='done'")],
            frozen=frozen,preflight_sha256=sha(SOURCE/"terminal.json"),
            rule="one dispatch per identical request; save before parse; stop on failure or ambiguous transport"))
        w=b.verified_worker(contract)
        w.validate_source_config(c)
        for probe in ("freeflow","values"):
            for sid in w.identities(probe): w.read_trace(c,probe,sid)
        original=w.bv1
        code=SOURCE/"offline_validator"
        sp=importlib.util.spec_from_file_location("qwen32_offline_v13",code/"luna_v1_3.py")
        validator=importlib.util.module_from_spec(sp);sp.loader.exec_module(validator)
        validator.BV.api_call=forbidden
        adopted_ids={"LONG_2","MID_7","MID_9","MID_19","MID_23","LONG_5","LONG_21"}
        def read(config,ph,sid,validate=False,**kw):
            assert validate, "essay generation forbidden"
            if sid not in adopted_ids: return original(config,ph,sid,True,**kw)
            src,digest=w.read_trace(config,"freeflow",sid)
            adopted=SOURCE/("offline_adoption" if sid=="LONG_2" else "offline_six_adoption")/sid
            attempt=adopted/"original_attempt.json"
            saved=adopted/"reading.md"
            rec=b.load(attempt)
            if sid=="LONG_2":
                selection=b.load(adopted/"selection.json")
                assert sha(attempt)==selection["sha256"]
                assert sha(saved)==selection["result_sha256"]
                assert digest==selection["source_sha256"]
                arm=selection["arm"]
            else:
                binding=b.load(adopted/"revalidation.json")
                assert sha(attempt)==binding["generation_attempt_sha256"]
                assert sha(saved)==binding["output_sha256"]
                assert digest==binding["source_sha256"]
                assert validator.code_sha256()==binding["validator_code_sha256"]
                arm=binding["evaluator_arm"]
            assert rec["arm"]==arm and rec["source_sha256"]==digest
            assert rec["response"]["choices"][0]["message"]["content"]==saved.read_text()
            assert validator.transport_valid(rec["http_status"],rec["response"])
            assert validator.valid_output(saved.read_text(),src["result"])==(True,"")
            out=analysis/"offline_adoption"/(sid+".md");out.parent.mkdir(exist_ok=True)
            if not out.exists():shutil.copyfile(saved,out)
            assert sha(out)==sha(saved)
            bp=w.bv1_paths(config,ph,arm)[2]/(sid+".json")
            binding=dict(source_sha256=digest,output_sha256=sha(out),evaluator_arm=arm)
            if not bp.exists():put(bp,binding)
            return dict(pid=config["id_prefix"]+"_BV1_"+sid,model=config["model"],cell=config["label"],
                        condition=src["condition"],provider=config["provider"],sample_id=config["label"]+"/"+sid+".json",
                        word_count=len(src["result"].split()),source=str(w.trace_path(config,"freeflow",sid)),
                        outpath=str(out),text=src["result"],evaluator_arm=arm)
        w.bv1=read
        sockets=(socket.socket.connect,socket.socket.connect_ex,socket.create_connection)
        socket.socket.connect=socket.socket.connect_ex=socket.create_connection=forbidden
        try:
            evidence=[]
            for sid in w.identities("freeflow"):
                row=w.bv1(c,phase,sid,True)
                assert not row.get("ineligible")
                evidence.append(dict(sample=sid,generation_arm=row["evaluator_arm"],
                    output=row["outpath"],output_sha256=sha(row["outpath"]),
                    source_sha256=sha(row["source"]),separate_v13_revalidation=sid in adopted_ids))
            assert len(evidence)==125 and w.bv1_ready_fields(c,phase)["bv1"]==125
            put(DEST/"offline-validation.json",dict(verified=125,samples=evidence,model_calls=0))
        finally: socket.socket.connect,socket.socket.connect_ex,socket.create_connection=sockets
        current={}
        def run(*args):
            assert Path(args[0]).resolve().is_relative_to(analysis)
            folder=current["folder"]/"transport";folder.mkdir(exist_ok=True)
            subprocess.run([sys.executable,"-B",str(b.ROOT/"gemma2_values_capture_child.py"),
                            str(folder),str(current["maximum"]),*map(str,args)],
                           check=True,timeout=current["timeout"])
        w.run=run
        os.environ.update(PERSONALITY_CELL_AGG_ROUTE="openrouter-openai",PERSONALITY_CELL_AGG_MODEL="gpt-5.4",
                          COLAB_QUEUE_ARM=b.load(b.STATE/"active-arm.json")["nonce"])
        loader=w.module
        def module(name,path):
            m=loader(name,path)
            if name=="capture_assembly":
                inner=m.module
                def load(n,p):
                    obj=inner(n,p)
                    if n=="phase35_aggregate":
                        def once(prompt,max_completion_tokens=4500,timeout=420):
                            assert not (b.ROOT.parent/"corpus-ops/STOP").exists()
                            payload=dict(model="openai/gpt-5.4",provider=dict(only=["OpenAI"],allow_fallbacks=False),
                                messages=[dict(role="system",content=obj.SYSTEM),dict(role="user",content=prompt)],
                                max_tokens=max_completion_tokens,temperature=0.2)
                            put(DEST/"PRECALL.json",dict(route="openrouter-openai",model="gpt-5.4",maximum_requests=1,
                                packet_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                                request_sha256=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(),
                                status="dispatch_may_have_occurred",automatic_retry=False))
                            import httpx
                            response=httpx.post("https://openrouter.ai/api/v1/chat/completions",json=payload,
                                timeout=timeout,follow_redirects=False,headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"],
                                "Content-Type":"application/json","HTTP-Referer":"https://danieltenner.com","X-Title":"qwen32-one-synthesis"})
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
        completed={}
        try:
            while work:
                eligible=sorted(id for id in work if all(db.execute("select state from jobs where id=?",(dep,)).fetchone()[0]=="done" for dep in tasks[id]["deps"]))
                assert eligible,"dependency deadlock"
                for id in eligible:
                    assert not (b.ROOT.parent/"corpus-ops/STOP").exists()
                    t=tasks[id];cmd=t["command"];action=cmd[3]
                    used=db.execute("select attempts from jobs where id=?",(id,)).fetchone()[0]
                    assert used<t["max_attempts"],"inherited budget exhausted"
                    folder=DEST/("job-"+hashlib.sha256(id.encode()).hexdigest()[:20]);folder.mkdir()
                    maximum=1
                    if action=="adjudicate":
                        maximum=3*sum(r.get("collapsed_primary_label_support",0)<2 for r in w.jsonl(phase/"posture_collapsed/consensus.jsonl"))
                    current.update(folder=folder,maximum=maximum,timeout=t["timeout"])
                    put(folder/"charged.json",dict(task=id,attempt=used+1,max_attempts=t["max_attempts"],transport_maximum=maximum))
                    db.execute("update jobs set attempts=attempts+1 where id=?",(id,));db.commit()
                    def invoke(validate):
                        if action in {"a","ac","p","pc"}:
                            sid=cmd[cmd.index("--sample")+1]
                            coder=cmd[cmd.index("--coder")+1] if "--coder" in cmd else None
                            w.values_stage(c,phase,sid,action,coder,validate)
                        elif action=="values":w.assemble_values(c,phase,validate)
                        elif action=="queue_ready":w.ready(c,phase,validate)
                        else:getattr(w,action)(c,phase,validate)
                    if action=="queue_ready":socket.socket.connect=socket.socket.connect_ex=socket.create_connection=forbidden
                    invoke(False);invoke(True)
                    receipts={p:sha(p) for p in t["outputs"]}
                    put(folder/"verified.json",dict(task=id,receipts=receipts,production_validation=True))
                    db.execute("update jobs set state='done',reason='isolated authorized continuation; production validated',receipts=? where id=?",(json.dumps(receipts),id));db.commit()
                    completed[id]=receipts;work.remove(id)
                    print("DONE",id,flush=True)
            assert all(manifest(Path(p))==m for p,m in frozen.items())
            paths=[analysis/"analysis/freeflow/personality-model-cards/cards/qwen1-5-32b-chat.md",
                   analysis/"analysis/freeflow/personality-model-profiles/profiles/qwen1-5-32b-chat.md",
                   phase/"VALUES_CARD.json",phase/"CARD_READY.json",phase/"ANALYSIS_READY.json",
                   phase/"release_candidate/reports/qwen1-5-32b-chat.md"]
            put(DEST/"terminal.json",dict(state="integrated_card_ready_awaiting_publication",bv1=125,values=120,
                source_unchanged=True,publication=False,completed=completed,receipts={str(p):sha(p) for p in paths}))
        except BaseException as exc:
            put(DEST/"STOPPED.json",dict(error=str(exc),completed=completed,remaining=sorted(work),
                dispatch_may_have_occurred=True,automatic_retry=False))
            raise
        finally:
            socket.socket.connect,socket.socket.connect_ex,socket.create_connection=sockets
            db.close()

if __name__=="__main__":main()
