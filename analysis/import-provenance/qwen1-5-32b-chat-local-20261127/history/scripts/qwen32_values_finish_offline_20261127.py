"""Finalize saved synthesis and integration, with every network path disabled."""
import sys
sys.dont_write_bytecode = True
import qwen32_values_authorized_20261127 as adaptation

text = adaptation.text
start = text.index('        assert not DEST.exists()')
end = text.index('        original=w.bv1',start)
text = text[:start]+'''        assert DEST.exists() and not (DEST/"terminal.json").exists()
        authorization=b.load(DEST/"authorization.json")
        frozen=authorization["frozen"]
        assert all(manifest(Path(p))==m for p,m in frozen.items())
        analysis=DEST/"analysis"
        c=b.load(DEST/"config.json")
        phase=Path(c["phase"])
        spec=b.load(DEST/"spec.json")
        put(DEST/"pre-path-correction-spec.json",spec)
        corrections={}
        for task in spec["tasks"]:
            for i,out in enumerate(task["outputs"]):
                if out.startswith(str(b.WORKTREE)+"/"):
                    replacement=str(analysis)+out[len(str(b.WORKTREE)):]
                    corrections[out]=replacement
                    task["outputs"][i]=replacement
        assert corrections and all(Path(p).is_relative_to(analysis) for p in corrections.values())
        (DEST/"spec.json").write_text(json.dumps(spec,indent=2)+"\\n")
        put(DEST/"local-path-correction.json",dict(corrections=corrections,network_calls=0,
            reason="stale compiled output paths only; no task budgets or commands changed"))
        db=sqlite3.connect(DEST/"state.sqlite")
        db.execute("update meta set v=? where k='spec'",(hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest(),))
        db.commit()
        tasks={t["id"]:t for t in spec["tasks"]}
        w=b.verified_worker(contract)
        socket.socket.connect=socket.socket.connect_ex=socket.create_connection=forbidden
''' + text[end:]
start = text.index('        sockets=(socket.socket.connect')
text = text[:start]+'''        # Original and targeted outputs are validation-only; offline adoptions
        # retain their generation arm and separate v1.3 validation evidence.
        evidence=[]
        for sid in w.identities("freeflow"):
            row=w.bv1(c,phase,sid,True)
            assert not row.get("ineligible")
            evidence.append(dict(sample=sid,arm=row["evaluator_arm"],output_sha256=sha(row["outpath"])))
        put(DEST/"final-offline-provenance.json",dict(verified=125,evidence=evidence,model_calls=0))
        response=b.load(DEST/"synthesis-response-receipt.json")
        assert sha(DEST/"synthesis-response.body")==response["sha256"] and response["status"]==200
        data=b.load(DEST/"synthesis-response.body")
        assert data["provider"]=="OpenAI" and data["model"]=="openai/gpt-5.4"
        assert data["choices"][0]["finish_reason"]=="stop"
        synth=MODEL+"/synthesis"
        assert db.execute("select attempts from jobs where id=?",(synth,)).fetchone()==(1,)
        w.synthesis(c,phase,True)
        receipts={p:sha(p) for p in tasks[synth]["outputs"]}
        put(DEST/"saved-synthesis-finalized.json",dict(receipts=receipts,model_calls=0,original_dispatch_count=1))
        db.execute("update jobs set state='done',reason='saved synthesis production validated; local output paths corrected',receipts=? where id=?",(json.dumps(receipts),synth))
        db.commit()
        job=MODEL+"/queue-ready"
        used=db.execute("select attempts from jobs where id=?",(job,)).fetchone()[0]
        assert used==0 and tasks[job]["max_attempts"]==1
        put(DEST/"integration-charged.json",dict(job=job,attempt=1,maximum=1,network_calls=0))
        db.execute("update jobs set attempts=attempts+1 where id=?",(job,));db.commit()
        w.ready(c,phase,False);w.ready(c,phase,True)
        receipts={p:sha(p) for p in tasks[job]["outputs"]}
        db.execute("update jobs set state='done',reason='offline integration production validated',receipts=? where id=?",(json.dumps(receipts),job));db.commit()
        assert not db.execute("select id from jobs where state!='done'").fetchall()
        for (r,) in db.execute("select receipts from jobs"):
            assert all(sha(p)==h for p,h in json.loads(r).items())
        assert all(manifest(Path(p))==m for p,m in frozen.items())
        paths=[analysis/"analysis/freeflow/personality-model-cards/cards/qwen1-5-32b-chat.md",
               analysis/"analysis/freeflow/personality-model-profiles/profiles/qwen1-5-32b-chat.md",
               phase/"VALUES_CARD.json",phase/"CARD_READY.json",phase/"ANALYSIS_READY.json",
               phase/"release_candidate/reports/qwen1-5-32b-chat.md"]
        put(DEST/"terminal.json",dict(state="integrated_card_ready_awaiting_publication",bv1=125,values=120,
            source_unchanged=True,publication=False,finalization_model_calls=0,
            receipts={str(p):sha(p) for p in paths},spec_sha256=sha(DEST/"spec.json"),
            synthesis_response_sha256=sha(DEST/"synthesis-response.body"),
            provenance_sha256=sha(DEST/"final-offline-provenance.json")))
        db.close()
'''
namespace=dict(__name__="qwen32_offline_finalizer",__file__=__file__)
exec(compile(text,__file__+"[offline]","exec"),namespace)
if __name__=="__main__":
    namespace["main"]()
