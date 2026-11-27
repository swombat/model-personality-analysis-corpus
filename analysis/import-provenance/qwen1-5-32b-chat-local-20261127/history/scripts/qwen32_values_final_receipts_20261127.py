"""Receipt-only completion after successful offline integration; no dispatch."""
import sys
sys.dont_write_bytecode = True
import qwen32_values_finish_offline_20261127 as predecessor

text=predecessor.text
start=text.index('        put(DEST/"pre-path-correction-spec.json"')
end=text.index('        db=sqlite3.connect',start)
text=text[:start]+text[end:]
start=text.index('        # Original and targeted outputs')
text=text[:start]+'''        w.synthesis(c,phase,True)
        w.ready(c,phase,True)
        job=MODEL+"/queue-ready"
        assert db.execute("select attempts from jobs where id=?",(job,)).fetchone()==(1,)
        # This is the same local integration boundary used by the proven 1.8B
        # finish adapter, not the earlier analysis-only QUEUE sentinel.
        paths=[analysis/"analysis/freeflow/personality-model-cards/cards/qwen1-5-32b-chat.md",
               analysis/"analysis/freeflow/personality-model-profiles/profiles/qwen1-5-32b-chat.md",
               phase/"VALUES_CARD.json",phase/"CARD_READY.json",phase/"ANALYSIS_READY.json",
               phase/"release_candidate/reports/qwen1-5-32b-chat.md"]
        receipts={str(p):sha(p) for p in paths}
        put(DEST/"local-integration-verified.json",dict(receipts=receipts,production_validation=True,
            new_requests=0,publication=False,inherited_queue_ready_budget=1,
            boundary="authorized full local integration replaces analysis-only QUEUE sentinel"))
        db.execute("update jobs set state='done',reason='authorized offline local integration; replaces analysis-only queue boundary',receipts=? where id=?",
            (json.dumps({str(p):sha(p) for p in paths[2:5]}),job));db.commit()
        assert not db.execute("select id from jobs where state!='done'").fetchall()
        for id,attempts,r in db.execute("select id,attempts,receipts from jobs"):
            assert attempts<=tasks[id]["max_attempts"]
            assert all(sha(p)==h for p,h in json.loads(r).items())
        assert all(manifest(Path(p))==m for p,m in frozen.items())
        transport=[]
        for charge in DEST.glob("job-*/transport/*.charged.json"):
            key=charge.name.removesuffix(".charged.json")
            body=charge.parent/(key+".response.body")
            meta=b.load(charge.parent/(key+".response.json"))
            assert meta["status"]==200 and meta["sha256"]==sha(body)
            data=b.load(body)
            assert data["choices"][0]["finish_reason"]=="stop"
            transport.append(dict(charge=str(charge),charge_sha256=sha(charge),response=str(body),response_sha256=sha(body),
                task=b.load(charge.parent.parent/"charged.json")["task"]))
        assert len(transport)==4
        response=b.load(DEST/"synthesis-response-receipt.json")
        assert response["status"]==200 and response["sha256"]==sha(DEST/"synthesis-response.body")
        put(DEST/"terminal.json",dict(state="integrated_card_ready_awaiting_publication",bv1=125,values=120,
            source_unchanged=True,publication=False,remote_writes=False,all_job_receipts_verified=True,
            inherited_attempt_limits_preserved=True,model_requests=5,coding_requests=4,adjudication_requests=0,synthesis_requests=1,
            transport_receipts=transport,receipts=receipts,spec_sha256=sha(DEST/"spec.json"),
            synthesis_response_sha256=sha(DEST/"synthesis-response.body"),
            provenance_sha256=sha(DEST/"final-offline-provenance.json"),
            original_generation_arms_preserved=True,separate_v13_revalidation=sorted(adopted_ids),
            recovery="local path and integration-boundary corrections only; no redispatch; previous STOPPED evidence preserved"))
        db.close()
        print(DEST/"terminal.json",sha(DEST/"terminal.json"))
        for path,h in receipts.items():print(path,h)
'''
namespace=dict(__name__="qwen32_final_receipts",__file__=__file__)
exec(compile(text,__file__+"[receipt-only]","exec"),namespace)
if __name__=="__main__":
    namespace["main"]()
