"""Single-use Qwen2.5 continuation adapted from receipt-first Qwen2 precedent."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib

precedent = Path(__file__).with_name("qwen2_final_20261127.py")
code = precedent.read_text()
code = code.replace('qwen2_eight_targeted_20261127', 'qwen25_eight_targeted_20261127')
code = code.replace('qwen2_final_20261127b', 'qwen25_final_20261127')
code = code.replace('capture_qwen2_final_20261127', 'capture_qwen25_final_20261127')
code = code.replace('Qwen/Qwen2-1.5B-Instruct', 'Qwen/Qwen2.5-1.5B-Instruct')
code = code.replace('resume=DEST.exists()', 'assert not DEST.exists(), "fresh isolated lane required"\n        resume=False')
code = code.replace('w.bv1=read', '''w.bv1=read
        put(DEST/"adapter-provenance.json",dict(
            precedent=str(precedent),precedent_sha256=hashlib.sha256(precedent.read_bytes()).hexdigest(),
            adapter=str(Path(__file__)),adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            caveat="Task-local validation/path adapter, not a mainline validator change; inherited generation arms and separate offline short-rule receipts retained."))
        evidence=[]
        for sid in w.identities("freeflow"):
            row=w.bv1(c,phase,sid,True)
            assert not row.get("ineligible")
            evidence.append(dict(sample=sid,generation_arm=row["evaluator_arm"],
                source_sha256=sha(row["source"]),output=row["outpath"],
                output_sha256=sha(row["outpath"]),offline_adopted=sid in offline))
        assert len(evidence)==125 and len({r["sample"] for r in evidence})==125
        put(DEST/"essay-provenance.json",dict(samples=evidence,model_calls=0))''')
exec(compile(code, str(precedent), "exec"))
