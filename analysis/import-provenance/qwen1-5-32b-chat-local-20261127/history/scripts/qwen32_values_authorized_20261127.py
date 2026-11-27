"""Model/sample adaptation of the completed 1.8B durable values lane.

The parent implementation is preserved; substitutions are explicit and bounded.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
parent = ROOT/"qwen18_values_authorized.py"
text = parent.read_text()
replacements = {
    'qwen18_four_targeted_20261127': 'qwen32_three_targeted_20261127',
    'qwen18_values_authorized_20261127b': 'qwen32_values_authorized_20261127',
    'qwen1-5-1-8b-chat-colab-vllm-bf16-re482ee3f': 'qwen1-5-32b-chat-colab-vllm-bf16-r0997b012',
    'qwen1-5-1-8b-chat': 'qwen1-5-32b-chat',
    'capture_qwen18_final_20261127': 'capture_qwen32_final_20261127',
    'Qwen1.5 1.8B G1_7': 'Qwen1.5 32B CTRL3_2',
    'G1_7': 'CTRL3_2',
    'qwen18-one-synthesis': 'qwen32-one-synthesis',
}
for old,new in replacements.items():
    assert old in text, old
    text = text.replace(old,new)
text = text.replace(
    'preflight = b.load(b.ROOT/"qwen18_values_downstream_20261127/terminal.json")\n'
    '        assert preflight["model_calls"] == 0 and preflight["bv1_complete"] == 125',
    'preflight = b.load(SOURCE/"terminal.json")\n'
    '        assert preflight["bv1_done"] == 125 and preflight["error"] is None')
text = text.replace('b.ROOT/"qwen18_values_downstream_20261127"', 'b.ROOT/"continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127"')
text = text.replace('sha(b.ROOT/"qwen18_values_downstream_20261127/terminal.json")', 'sha(SOURCE/"terminal.json")')
start = text.index('        adoption=SOURCE/"open8_offline_adoption"')
end = text.index('        w.bv1=read',start)
text = text[:start]+'''        code=SOURCE/"offline_validator"
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
''' + text[end:]
text = text.replace('sid in {"OPEN_8","MID_15"}', 'sid in adopted_ids')
text = text.replace(
    '(SOURCE,b.ROOT/"raw",b.ROOT/"continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127")',
    '(SOURCE,b.ROOT/"raw",b.ROOT/"continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127",'
    'b.ROOT/"continuation_batch_v13_qwen1-5-32b-chat",b.ROOT/"remaining_recovery_colab-qwen1-5-32b-chat")')
# Record exact adaptation and transport precedent hashes inside the new lane.
text = text.replace('        DEST.mkdir()', '''        DEST.mkdir()
        put(DEST/"adaptation.json",dict(parent=str(parent),parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),
            adapter=str(Path(__file__)),adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            executed_sha256=hashlib.sha256(ADAPTED_SOURCE.encode()).hexdigest(),
            capture_child_sha256=sha(b.ROOT/"gemma2_values_capture_child.py")))
        (DEST/"executed_adaptation.py").write_text(ADAPTED_SOURCE)''')
namespace = dict(__name__="qwen32_adapted", __file__=str(Path(__file__).resolve()),
                 parent=parent, ADAPTED_SOURCE=text)
exec(compile(text,str(parent)+"[32B-adaptation]","exec"),namespace)
if __name__=="__main__":
    namespace["main"]()
