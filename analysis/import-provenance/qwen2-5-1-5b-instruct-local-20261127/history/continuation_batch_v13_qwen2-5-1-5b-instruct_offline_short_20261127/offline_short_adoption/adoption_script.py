"""Adopt exactly the saved short-source screen; no generation or remote writes."""
import sys
sys.dont_write_bytecode = True
import fcntl
import json
import shutil
import sqlite3
import time
from pathlib import Path
import qwen32_six_offline_20261127 as precedent
import audit_short_readings as audit
from replay_v13_candidates import module

ROOT = Path(__file__).resolve().parent
sha, manifest, write = precedent.sha, precedent.manifest, precedent.write


def main():
    with (ROOT / "state/host-supervisor.lock").open() as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not (ROOT.parent / "corpus-ops/STOP").exists()
        screen = ROOT / "short-source-screen-0952.json"
        screen_hash = sha(screen)
        selected = json.loads(screen.read_text())
        assert {m: len(v) for m, v in selected.items()} == {
            "qwen2-1-5b-instruct": 14, "qwen2-5-1-5b-instruct": 28}
        candidate = ROOT.parent / "colab-bv1-v1.3-candidate/analysis/freeflow/personality-eval-bv1"
        codepaths = [ROOT / n for n in ("audit_short_readings.py", "replay_v13_candidates.py",
                     "adopt_batch_v13.py", "qwen32_six_offline_20261127.py")]
        codepaths += [candidate / n for n in ("luna_v1_3.py", "luna_v1.py", "run_full_bv1.py")]
        provenance = {str(p): sha(p) for p in codepaths}
        check = audit.short_check()
        prepared = []
        # Validate all 42 before creating either successor.
        for model, items in selected.items():
            parent = ROOT / ("continuation_batch_v13_" + model)
            dest = ROOT / (parent.name + "_offline_short_20261127")
            assert not dest.exists()
            frozen = {str(p): manifest(p) for p in
                      (parent, ROOT / ("remaining_recovery_colab-" + model))}
            verified = []
            for job, proof in items.items():
                label, stage, sid = job.split("/")
                assert stage == "bv1"
                source = ROOT / "raw/data/traces_freeflow" / ("freeflow_" + label) / (sid + ".json")
                sample = json.loads(source.read_text())
                attempt = Path(proof["attempt"])
                assert attempt.is_relative_to(parent)
                assert sha(attempt) == proof["sha256"]
                rec = json.loads(attempt.read_text())
                assert sha(source) == proof["source_sha256"] == rec["source_sha256"]
                base = parent / "analysis/analysis/freeflow/personality-eval-bv1"
                original = module(base / "luna_v1.py")
                original.BV.api_call = precedent.forbidden
                prompt = original.BV.PROMPT_PATH
                if not prompt.exists():
                    original.BV.PROMPT_PATH = ROOT / "analysis-worktree" / prompt.relative_to(parent / "analysis")
                assert (rec["arm"], rec["sample_id"], rec["request"]) == (
                    original.ARM, label + "/" + sid + ".json",
                    original.payload(dict(text=sample["result"], condition=sample["condition"])))
                assert original.transport_valid(rec["http_status"], rec["response"])
                text = rec["response"]["choices"][0]["message"]["content"]
                assert original.valid_output(text, sample["result"]) == (rec["qa_pass"], rec["qa_reason"])
                assert check(text, sample["result"], None, None) == "pass_short"
                verified.append((job, source, attempt, rec, text, {
                    str(p): sha(p) for p in [base / "luna_v1.py", base / "run_full_bv1.py",
                                             original.BV.PROMPT_PATH]}))
            prepared.append((parent, dest, frozen, verified))
        for parent, dest, frozen, verified in prepared:
            assert not (parent / "state.sqlite-wal").exists() or (parent / "state.sqlite-wal").stat().st_size == 0
            shutil.copytree(parent, dest)
            evidence = dest / "offline_short_adoption"
            evidence.mkdir()
            shutil.copyfile(__file__, evidence / "adoption_script.py")
            shutil.copyfile(screen, evidence / "original_screen.json")
            write(evidence / "frozen_original_manifests.json", frozen)
            for p in codepaths:
                sub = "candidate" if p.parent == candidate else "precedent"
                target = evidence / "validator" / sub / p.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, target)
            db = sqlite3.connect(dest / "state.sqlite")
            before = {r[0]: r for r in db.execute("select * from jobs")}
            tables = {r[0] for r in db.execute("select name from sqlite_master where type='table'")}
            other = {t: db.execute(f'SELECT * FROM "{t}"').fetchall()
                     for t in tables - {"jobs", "events"}}
            old_events = db.execute("select * from events").fetchall()
            adopted = []
            for job, source, attempt, rec, text, original_code in verified:
                assert before[job][1] == "blocked"
                out = evidence / job.split("/")[-1]
                out.mkdir()
                (out / "reading.md").write_bytes(text.encode("utf-8"))
                shutil.copyfile(attempt, out / "original_attempt.json")
                binding = dict(job=job, source=str(source), source_sha256=sha(source),
                    generation_attempt=str(attempt), generation_attempt_sha256=sha(attempt),
                    output_sha256=sha(out / "reading.md"), evaluator_arm=rec["arm"],
                    original_qa_pass=rec["qa_pass"], original_qa_reason=rec["qa_reason"],
                    original_validator_files_sha256=original_code,
                    validator="offline-short-source-30-word-rule",
                    validator_files_sha256=provenance, request_verified=True,
                    transport_valid=True, revalidation_result="pass_short", model_calls=0)
                write(out / "revalidation.json", binding)
                receipts = {str(p): sha(p) for p in out.iterdir()}
                assert db.execute("update jobs set state='done',reason=?,receipts=? where id=? and state='blocked'",
                    ("offline-short-source-30-word-rule; original generation arm unchanged",
                     json.dumps(receipts), job)).rowcount == 1
                db.execute("insert into events values(?,?,?,?)",
                    (time.time(), job, "offline_short_adopted", json.dumps(binding)))
                adopted.append(binding)
            db.commit()
            after = {r[0]: r for r in db.execute("select * from jobs")}
            chosen = {v[0] for v in verified}
            for job, row in before.items():
                assert after[job][2:6] == row[2:6]
                if job not in chosen:
                    assert after[job] == row
            for t, rows in other.items():
                assert db.execute(f'SELECT * FROM "{t}"').fetchall() == rows
            assert db.execute("select * from events").fetchall()[:len(old_events)] == old_events
            for row in after.values():
                if row[1] == "done":
                    assert all(sha(p) == h for p, h in json.loads(row[-1]).items())
            done = sum("/bv1/" in k and r[1] == "done" for k, r in after.items())
            remaining = sorted(k for k, r in after.items() if "/bv1/" in k and r[1] != "done")
            assert done == 117 and len(remaining) == 8
            db.close()
            assert all(manifest(Path(p)) == m for p, m in frozen.items())
            assert all(sha(dest / rel) == h for rel, h in frozen[str(parent)].items()
                       if not rel.startswith("state.sqlite"))
            assert sha(screen) == screen_hash
            assert all(sha(p) == h for p, h in provenance.items())
            result = dict(terminal_path=str(dest), parent=str(parent), bv1_done=done,
                bv1_total=125, remaining_ids=remaining, adopted=adopted,
                screen_sha256=screen_hash, model_calls=0, frozen_originals_unchanged=True,
                counters_unchanged=True, inputs_unchanged=True, existing_receipts_verified=True,
                scheduler_enabled=False, automatic_resume_supported=False,
                downstream_run=False, published=False)
            write(dest / "terminal.json", result)
            print(json.dumps({k: result[k] for k in
                ("terminal_path", "bv1_done", "bv1_total", "remaining_ids", "model_calls")}, indent=2))


if __name__ == "__main__":
    main()
