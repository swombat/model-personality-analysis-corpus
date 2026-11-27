"""Offline adoption of saved original readings. No queue or generation calls."""
import sys
sys.dont_write_bytecode = True
import adopt_qwen14_offline as a


def adopt(label):
    root = a.ROOT
    short, marker, _ = label.partition("-colab-vllm-")
    assert marker and "/" not in label
    source = root / ("remaining_recovery_colab-" + short)
    dest = root / ("continuation_batch_v13_" + short)
    assert not dest.exists()
    orig = a.manifest(source)
    candidates = root / "state/replay-20261126-16-candidate" / label
    assert candidates.is_dir()
    a.shutil.copytree(source, dest, ignore=a.shutil.ignore_patterns("state.sqlite*"))
    with a.sqlite3.connect(f"file:{source}/state.sqlite?mode=ro", uri=True) as original, a.sqlite3.connect(dest/"state.sqlite") as db:
        original.backup(db)
    code = dest/"offline_validator"
    code.mkdir()
    for name in ("luna_v1_3.py", "luna_v1.py", "run_full_bv1.py"):
        (code/name).write_bytes(a.subprocess.check_output(["git","-C",str(a.REPO),"show",f"{a.COMMIT}:analysis/freeflow/personality-eval-bv1/{name}"]))
    spec = a.importlib.util.spec_from_file_location("batch_v13",code/"luna_v1_3.py")
    v = a.importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    v.BV.api_call = a.forbidden
    checked = []
    with a.sqlite3.connect(dest/"state.sqlite") as db:
        for c in sorted(candidates.iterdir()):
            sid = c.name
            job = f"{label}/bv1/{sid}"
            proof = a.load(c/"receipt.json")
            assert proof["job"] == job
            src = root/"raw/data/traces_freeflow"/("freeflow_"+label)/(sid+".json")
            att = root/proof["path"]
            rec = a.load(att)
            output = c/"reading.md"
            text = output.read_text()
            assert a.sha(src) == proof["source_sha256"] == rec["source_sha256"]
            assert a.sha(att) == proof["sha256"] and a.sha(output) == proof["result_sha256"]
            assert rec["arm"] == proof["arm"] and rec["response"]["choices"][0]["message"]["content"] == text
            assert v.transport_valid(rec["http_status"],rec["response"])
            source_text = a.load(src)["result"]
            short_rule = proof["candidate"] == "pass_short"
            if short_rule:
                import audit_short_readings as audit
                assert audit.short_check()(text,source_text,None,None) == "pass_short"
            else:
                assert proof["candidate"] == "sentence"
                assert v.valid_output(text,source_text) == (True,"")
            assert db.execute("select state from jobs where id=?",(job,)).fetchone() == ("blocked",)
            take = dest/"offline_adoption"/sid
            take.mkdir(parents=True)
            for p,name in ((att,"original_attempt.json"),(output,"reading.md"),(c/"receipt.json","selection.json")):
                a.shutil.copyfile(p,take/name)
            binding = dict(source_sha256=a.sha(src),output_sha256=a.sha(output),evaluator_arm=rec["arm"],generation_attempt_sha256=a.sha(att),validator=v.VALIDATOR,validator_commit=a.COMMIT,validator_code_sha256=v.code_sha256(),original_qa_pass=rec["qa_pass"],original_qa_reason=rec["qa_reason"],revalidation_pass=True,model_calls=0)
            if short_rule:
                candidate_code = root.parent/"colab-bv1-v1.3-candidate/analysis/freeflow/personality-eval-bv1"
                saved = dest/"offline_short_validator"
                saved.mkdir(exist_ok=True)
                for p in (root/"audit_short_readings.py",root/"replay_v13_candidates.py",*(candidate_code/n for n in ("luna_v1_3.py","luna_v1.py","run_full_bv1.py"))):
                    a.shutil.copyfile(p,saved/p.name)
                binding.update(validator="offline-short-source-30-word-rule",validator_code_sha256=a.manifest(saved))
                del binding["validator_commit"]
            path = dest/"phase/bv1_bindings_v13_revalidation"/(sid+".json")
            a.write(path,binding)
            receipts = {str(p):a.sha(p) for p in (path,take/"reading.md",take/"original_attempt.json",take/"selection.json")}
            db.execute("update jobs set state='done',reason=?,receipts=? where id=?",("offline-v1.3-revalidation; generation arm unchanged",a.json.dumps(receipts),job))
            db.execute("insert into events values(strftime('%s','now'),?,?,?)",(job,"offline_v13_adopted",a.json.dumps(binding)))
            checked.append(sid)
        count = db.execute("select count(*) from jobs where id like '%/bv1/%' and state='done'").fetchone()[0]
    assert orig == a.manifest(source)
    a.write(dest/"result.json",dict(model=label,adopted=checked,bv1_done=count,source_unchanged=True,model_calls=0,scheduler_enabled=False))
    print(short, checked, count, flush=True)


if __name__ == "__main__":
    for label in sys.argv[1:]:
        adopt(label)
