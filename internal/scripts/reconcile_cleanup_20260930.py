#!/usr/bin/env python3
"""Validate and receipt the explicit September 30 publication interventions.

No inference, no attempt resets. Run only with these local historical run
directories present. Takes the supervisor lock and preserves old receipts in
both SQLite events and the portable audit record.
"""
import fcntl
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT.parent / "model-personality-corpus-v2"
PLANS = [
    ("20260923-space-bunny",
        "space-bunny-alpha-or-pin-stealth",
        ["values-report", "values-integrated", "synthesis", "ready"],
    ),
    ("20260922-glm53-long-repair",
        "glm-5-3-or-pin-z-ai-20260825", ["synthesis", "repair-ready"],
    ),
    ("20260922-xiaomi25", "mimo-v2-5-pro-or-pin-xiaomi", ["ready"]),
    ("20260923-bonsai-qwen-medium", "qwen3-8-27b-or-pin-deepinfra-medium",
     ["values-integrated", "synthesis", "ready"]),
    ("20260923-bonsai-qwen-medium", "ternary-bonsai-2-27b-or-pin-darkbloom-medium",
     ["values-integrated", "synthesis", "ready"]),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    audit = ROOT / "internal/methodology/cleanup-20260930/reconciliation.json"
    records = json.loads(audit.read_text()) if audit.exists() else []
    for run, label, names in PLANS:
        directory = RAW / "logs/capture-harness" / run
        state = directory / "state"
        spec = json.loads((directory / "spec.json").read_text())
        tasks = {t["id"]: t for t in spec["tasks"]}
        with (state / "supervisor.lock").open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            db = sqlite3.connect(state / "state.sqlite", timeout=30)
            try:
                for name in names:
                    id = f"{label}/{name}"
                    task = tasks[id]
                    assert all(db.execute("SELECT state FROM jobs WHERE id=?", (d,)).fetchone()[0]
                               == "done" for d in task["deps"]), id
                    old = db.execute("SELECT state,attempts,receipts FROM jobs WHERE id=?", (id,)).fetchone()
                    assert old[0] in ("done", "blocked", "pending"), old
                    subprocess.run(task["validate"], cwd=RAW, check=True, timeout=task["timeout"])
                    receipts = {str(Path(p).resolve()): digest(p) for p in task["outputs"]}
                    if old[0] == "done" and json.loads(old[2] or "{}") == receipts:
                        continue
                    detail = {"authorization": "Daniel cleanup request 2026-09-30",
                              "run": run, "id": id, "old_state": old[0],
                              "attempts_preserved": old[1],
                              "old_receipts": json.loads(old[2] or "{}"),
                              "validated_receipts": receipts,
                              "reason": "Explicit publication-policy / fresh aggregate intervention; no recoding"}
                    with db:
                        db.execute("INSERT INTO events VALUES(?,?,?,?)",
                                   (time.time(), id, "validated_publication_reconciliation", json.dumps(detail)))
                        db.execute("UPDATE jobs SET state='done',reason=NULL,receipts=?,pid=NULL WHERE id=?",
                                   (json.dumps(receipts), id))
                    records.append(detail)
                    audit.parent.mkdir(parents=True, exist_ok=True)
                    audit.write_text(json.dumps(records, indent=2) + "\n")
            finally:
                db.close()
    # Refresh status only after every model in each run is reconciled: Engine
    # construction checks all sibling receipts and otherwise invalidates their
    # descendants midway through a multi-model publication update.
    sys.path.insert(0, str(RAW / "scripts/capture_harness"))
    from engine import Engine
    for run in dict.fromkeys(run for run, _, _ in PLANS):
        directory = RAW / "logs/capture-harness" / run
        state = directory / "state"
        spec = json.loads((directory / "spec.json").read_text())
        engine = Engine(spec, state)
        try:
            engine.status()
        finally:
            engine.db.close()
            engine.lock.close()
    print("Validated reconciliation complete; original attempts retained.")


if __name__ == "__main__":
    main()
