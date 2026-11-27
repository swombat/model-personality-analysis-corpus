"""One-shot offline adoption; all writes confined to a new successor."""
import sys
sys.dont_write_bytecode = True
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import time

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / "continuation_batch_v13_qwen1-5-32b-chat"
DEST = ROOT / "continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127"
COMMIT = "0736983b404300033ce20858c64870b17f68d269"


def forbidden(*a, **kw):
    raise RuntimeError("offline task: network/model calls forbidden")


socket.socket.connect = socket.socket.connect_ex = forbidden
socket.create_connection = forbidden


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def manifest(p):
    assert not any(q.is_symlink() for q in p.rglob("*"))
    return {str(q.relative_to(p)): sha(q) for q in sorted(p.rglob("*")) if q.is_file()}


def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


def main():
    with (ROOT / "state/host-supervisor.lock").open() as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not (ROOT.parent / "corpus-ops/STOP").exists()
        assert not DEST.exists()
        frozen_paths = [ORIGINAL, ROOT / "remaining_recovery_colab-qwen1-5-32b-chat"]
        frozen = {str(p): manifest(p) for p in frozen_paths}
        assert (ORIGINAL / "state.sqlite-wal").stat().st_size == 0
        audit_path = ROOT / "offline-three-eligible-audit-0944.json"
        audit_hash = sha(audit_path)
        audit = json.loads(audit_path.read_text())["qwen1-5-32b-chat"]
        selected = {k: v for k, v in audit.items() if any(a["valid"] for a in v)}
        assert {k.split("/")[-1] for k in selected} == {
            "MID_7", "MID_9", "MID_19", "MID_23", "LONG_5", "LONG_21"}
        shutil.copytree(ORIGINAL, DEST)
        evidence = DEST / "offline_six_adoption"
        evidence.mkdir()
        shutil.copyfile(__file__, evidence / "adoption_script.py")
        shutil.copyfile(audit_path, evidence / "original_audit.json")
        write(evidence / "frozen_original_manifests.json", frozen)
        code = evidence / "validator"
        code.mkdir()
        for name in ("luna_v1_3.py", "luna_v1.py", "run_full_bv1.py"):
            data = subprocess.check_output(["git", "-C",
                str(ROOT.parent / "model-personality-analysis-corpus"), "show",
                f"{COMMIT}:analysis/freeflow/personality-eval-bv1/{name}"])
            (code / name).write_bytes(data)
            assert data == (ORIGINAL / "offline_validator" / name).read_bytes()
        spec = importlib.util.spec_from_file_location("qwen32_offline_validator", code / "luna_v1_3.py")
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        validator.BV.api_call = forbidden
        db = sqlite3.connect(DEST / "state.sqlite")
        before_jobs = {r[0]: r for r in db.execute("select * from jobs")}
        before_tables = {t: db.execute(f"select * from {t}").fetchall()
                         for t in ("meta", "targeted_repairs")}
        assert sum("/bv1/" in k and r[1] == "done" for k, r in before_jobs.items()) == 116
        existing_receipts = {}
        for row in before_jobs.values():
            if row[1] == "done":
                for p, h in json.loads(row[-1]).items():
                    assert sha(p) == h
                    existing_receipts[p] = h
        checks, adopted, source_hashes = [], [], {}
        for job, attempts in selected.items():
            sample = job.split("/")[-1]
            source = ROOT / "raw/data/traces_freeflow" / ("freeflow_" + job.split("/")[0]) / (sample + ".json")
            source_hashes[str(source)] = sha(source)
            valid = []
            for a in sorted(attempts, key=lambda a: Path(a["path"]).name):
                p = Path(a["path"])
                assert sha(p) == a["sha256"]
                record = json.loads(p.read_text())
                assert record["source_sha256"] == sha(source)
                assert record["arm"] == "bv1-luna-v1-20260929"
                text = record["response"]["choices"][0]["message"]["content"]
                transport = validator.transport_valid(record["http_status"], record["response"])
                ok, reason = validator.valid_output(text, json.loads(source.read_text())["result"])
                assert ok == a["valid"] and reason == a["reason"]
                checks.append(dict(job=job, attempt=str(p), attempt_sha256=sha(p),
                                   transport_valid=transport, valid=ok, reason=reason))
                if transport and ok:
                    valid.append((p, record, text))
            assert valid and before_jobs[job][1] == "blocked"
            p, record, text = valid[0]
            out = evidence / sample
            out.mkdir()
            output = out / "reading.md"
            output.write_bytes(text.encode("utf-8"))
            shutil.copyfile(p, out / "original_attempt.json")
            binding = dict(job=job, source=str(source), source_sha256=sha(source),
                output_sha256=sha(output), generation_attempt=str(p),
                generation_attempt_sha256=sha(p), evaluator_arm=record["arm"],
                original_qa_pass=record["qa_pass"], original_qa_reason=record["qa_reason"],
                validator=validator.VALIDATOR, validator_commit=COMMIT,
                validator_code_sha256=validator.code_sha256(),
                validator_files_sha256={q.name: sha(q) for q in code.glob("*.py")},
                revalidation_pass=True, model_calls=0)
            write(out / "revalidation.json", binding)
            receipt = {str(q): sha(q) for q in (output, out / "original_attempt.json", out / "revalidation.json")}
            assert db.execute("update jobs set state='done',reason=?,receipts=? where id=? and state='blocked'",
                ("offline-v1.3-revalidation; original generation arm unchanged",
                 json.dumps(receipt), job)).rowcount == 1
            db.execute("insert into events values(?,?,?,?)",
                (time.time(), job, "offline_v13_adopted", json.dumps(binding)))
            adopted.append(binding)
        db.commit()
        after_jobs = {r[0]: r for r in db.execute("select * from jobs")}
        for k, row in before_jobs.items():
            if k in selected:
                assert after_jobs[k][2:6] == row[2:6]
            else:
                assert after_jobs[k] == row
        for t, rows in before_tables.items():
            assert db.execute(f"select * from {t}").fetchall() == rows
        done = [k for k, r in after_jobs.items() if "/bv1/" in k and r[1] == "done"]
        remaining = sorted(k for k, r in after_jobs.items() if "/bv1/" in k and r[1] != "done")
        assert len(done) == 122 and len(remaining) == 3
        for row in after_jobs.values():
            if row[1] == "done":
                assert all(sha(p) == h for p, h in json.loads(row[-1]).items())
        db.close()
        assert all(sha(p) == h for p, h in existing_receipts.items())
        assert all(sha(p) == h for p, h in source_hashes.items())
        assert sha(audit_path) == audit_hash
        assert all(manifest(Path(p)) == m for p, m in frozen.items())
        # Every copied original file except the successor database is byte-preserved.
        for rel, h in frozen[str(ORIGINAL)].items():
            if not rel.startswith("state.sqlite"):
                assert sha(DEST / rel) == h
        result = dict(terminal_path=str(DEST), parent=str(ORIGINAL),
            bv1_done=122, bv1_total=125, remaining_ids=remaining,
            adopted=adopted, checks=checks, model_calls=0, audit_sha256=audit_hash,
            frozen_originals_unchanged=True, counters_unchanged=True,
            existing_receipts_verified=True, source_hashes=source_hashes,
            scheduler_enabled=False, automatic_resume_supported=False,
            downstream_run=False, published=False)
        write(DEST / "terminal.json", result)
        print(json.dumps({k: result[k] for k in
            ("terminal_path", "bv1_done", "bv1_total", "remaining_ids", "model_calls")}, indent=2))


if __name__ == "__main__":
    main()
