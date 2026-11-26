#!/usr/bin/env python3
"""Offline, model-specific complete evidence inventory for original Gemma 7B."""
import csv
import json
import sqlite3
from contextlib import closing
from pathlib import Path
import gemma7_stage as planner

HOME, QUEUE, STATE, FORK = planner.HOME, planner.QUEUE, planner.FINISH, planner.FORK
LABEL, SLUG = planner.LABEL, planner.SLUG
read, load, digest, need = planner.read, planner.load, planner.digest, planner.need
SPEC_SHA = "f107991695b08f349b1210736f09a4e60c4dd52eaaf984cd13bcf4a782d6fb3a"


def inspect():
    # Planner verifies raw inventory, original receipts, exact targeted response,
    # request/sidecar/bindings and isolated recovery authorization.
    plan = planner.inspect(SPEC_SHA)
    need(digest(read(STATE / "spec.json")) == SPEC_SHA, "finish spec drift")
    c, old = load(STATE / "config.json"), load(FORK / "config.json")
    root, phase = Path(c["analysis_root"]), Path(c["phase"])
    oldroot, oldphase = Path(old["analysis_root"]), Path(old["phase"])
    need(root == QUEUE / "analysis-worktree" and phase.is_relative_to(root),
         "finish roots")
    spec, tasks, rows = planner.common.snapshot(STATE)
    need(len(rows) == 10 and all(r[1] == "done" for r in rows), "ten terminal jobs required")
    need(load(STATE / "terminal.json") == {"engine_result": "complete"}, "terminal incomplete")
    entries = {e["destination"]: e for e in plan["evidence_entries"]}

    def add(src, repository="analysis", destination=None, expected=None):
        src = Path(src)
        data = read(src)
        need(expected is None or digest(data) == expected, "adopted receipt hash: " + str(src))
        base = {"analysis": root, "raw": QUEUE / "raw", "evidence": QUEUE}[repository]
        rel = Path(destination) if destination else src.relative_to(base)
        need(not rel.is_absolute() and ".." not in rel.parts, "unsafe destination")
        key = repository + "/" + str(rel)
        e = dict(source=str(src), destination=key, sha256=digest(data), bytes=len(data))
        need(key not in entries or entries[key] == e, "destination collision")
        entries[key] = e
        return data

    # Every successful fork output must have a byte-identical adopted copy.
    for jid, state, attempts, receipt in plan["task_snapshots"]["fork"]:
        if state != "done":
            continue
        for filename, sha in json.loads(receipt).items():
            src = Path(filename)
            if src.is_relative_to(oldphase):
                add(phase / src.relative_to(oldphase), expected=sha)
            elif src.is_relative_to(oldroot):
                add(root / src.relative_to(oldroot), expected=sha)
            elif src.is_relative_to(QUEUE / "raw"):
                add(src, "raw", expected=sha)
            else:
                need(False, "unscoped fork output")
    verified = plan["isolated_values_recovery"]
    add(QUEUE / "state/qa-holds/colab-gemma-7b-it.json", "evidence",
        expected=verified["parent_hold_sha256"])
    add(phase / "samples/G1_27/layer_a/glm-4-7.jsonl", expected=verified["sha256"])
    outputs = {}
    for sid, sha in c["source_adoption"]["sha256"]["freeflow"].items():
        targeted = sid in planner.SAMPLES
        arm = planner.variant.ARM if targeted else planner.variant.V1
        out = root / "analysis/freeflow/personality-eval-bv1/arms" / arm / "outputs" / LABEL / (sid + ".md")
        data = add(out)
        binding = load(phase / ("bv1_bindings_luna_v1_targeted" if targeted else "bv1_bindings_luna_v1") / (sid + ".json"))
        need(binding == dict(source_sha256=sha, output_sha256=digest(data), evaluator_arm=arm),
             "final essay binding")
        originals = phase / "freeflow_bv1_luna_v1/attempt_responses" / (c["id_prefix"] + "_BV1_" + sid)
        need(bool(list(originals.glob("*.json"))), "original essay attempts absent")
        outputs[LABEL + "/" + sid + ".json"] = str(out)
    manifest = list(csv.DictReader(read(phase / "freeflow_bv1_luna_v1/sample_manifest.tsv").decode().splitlines(), delimiter="\t"))
    need(len(manifest) == 125 and {r["sample_id"]: r["output_file"] for r in manifest} == outputs,
         "final mixed-arm manifest")
    ready = load(phase / "QUEUE_ANALYSIS_READY.json")
    need(ready["state"] == "analysis_only_awaiting_review" and ready["model"] == SLUG
         and ready["source_adoption"] == c["source_adoption"]
         and ready["raw_counts"] == {"freeflow": 125, "values": 120}
         and ready["bv1"] == {"bv1": 125, "bv1_variant_arms": dict.fromkeys(planner.SAMPLES, planner.variant.ARM)}
         and all(ready[k] is False for k in ("publication_complete", "website_touched", "site_integration_performed")),
         "readiness mismatch")
    # Complete final phase plus original immutable phase/attempts, not just planner's subset.
    for directory, repo, destbase in (
        (phase, "analysis", None),
        (oldphase, "evidence", None),
        (planner.RETRY, "evidence", None),
    ):
        for src in sorted(directory.rglob("*")):
            need(not src.is_symlink(), "evidence symlink")
            if src.is_file():
                add(src, repo)
    for directory in (STATE, FORK):
        for name in ("config.json", "spec.json"):
            add(directory / name, "evidence")
    original = QUEUE / "state/colab-gemma-7b-it"
    auth = load(planner.RETRY / "authorization.json")
    add(original / "models" / (LABEL + ".json"), "evidence", expected=auth["original_config_sha256"])
    add(original / "spec.json", "evidence", expected=auth["original_spec_sha256"])
    snapshots_original = planner.common.snapshot(original)[2]
    hold = load(QUEUE / "state/qa-holds/colab-gemma-7b-it.json")
    with closing(sqlite3.connect(f"file:{original}/state.sqlite?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        held_rows = db.execute(
            "SELECT id,state,attempts,next_at,pid,started,reason,receipts FROM jobs ORDER BY id").fetchall()
    need(digest(json.dumps(held_rows).encode()) == hold["rows_sha256"], "original held rows changed")
    for failure in hold["failures"]:
        for log in failure["logs"]:
            add(log["path"], "evidence", expected=log["sha256"])
    add(STATE / "terminal.json", "evidence")
    for name in ("aggregate.md", "packet.md", "packet.metadata.json"):
        add(root / "analysis/freeflow/personality-aggregates" / LABEL / name)
    # Export coherent transactions, never copy a live sqlite database.
    snapshots = {name: planner.common.snapshot(directory)[2]
                 for name, directory in (("fork", FORK), ("finish", STATE))}
    need(snapshots == plan["task_snapshots"], "queue state changed during inspection")
    snapshots["original"] = snapshots_original
    snapshots["original_hold_full_rows"] = held_rows
    return dict(import_complete=True, blockers=[], label=LABEL,
                task_snapshots=snapshots, verified_essay_count=125,
                variant_samples=sorted(planner.SAMPLES), isolated_values_recovery=verified,
                entries=sorted(entries.values(), key=lambda e: e["destination"]))


if __name__ == "__main__":
    print(json.dumps(inspect(), indent=2))
