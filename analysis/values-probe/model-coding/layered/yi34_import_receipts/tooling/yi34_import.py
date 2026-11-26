#!/usr/bin/env python3
"""Offline original Yi 34B mixed recovery inventory; no publication authority."""
import csv
import json
import sqlite3
from contextlib import closing
from pathlib import Path
import q2514_import as common
import gemma7_stage as predecessor

HOME = Path(__file__).resolve().parent
QUEUE = HOME.parent / "colab-batch-queue"
STATE = QUEUE / "state/finish-yi-34b-chat"
FORK = QUEUE / "remaining_recovery_colab-yi-34b-chat"
RETRY = QUEUE / "state/yi34-layer-a-v1"
ORIGINAL = QUEUE / "state/colab-yi-34b-chat"
LABEL = "yi-34b-chat-colab-vllm-bf16-rcf02cb50"
SLUG = "yi-34b-chat"
SAMPLES = {"LONG_4", "MID_2", "MID_9", "MID_14", "OPEN_15"}
SPEC_SHA = "52557b93f5e242f6542a751a49b5c62106cf98bdaf139eab667a3c60974dc0fe"
FORK_SHA = "a033e33f8af247560c405cb38c7730106b7b00c39e0788c1f4d05799fe1ba12e"
need, read, digest, load = common.need, common.read, common.digest, common.load
variant = predecessor.variant


def inspect():
    c, old = load(STATE / "config.json"), load(FORK / "config.json")
    root, phase = Path(c["analysis_root"]), Path(c["phase"])
    oldroot, oldphase = Path(old["analysis_root"]), Path(old["phase"])
    need(root == QUEUE / "analysis-worktree" and phase.is_relative_to(root), "finish roots")
    need(oldroot == FORK / "analysis" and oldphase == FORK / "phase", "fork roots")
    for config in (c, old):
        need(config["label"] == LABEL and config["slug"] == SLUG
             and config["model"] == "01-ai/Yi-34B-Chat", "model drift")
    need(c["source_adoption"] == old["source_adoption"], "adoption drift")
    entries, snapshots = {}, {}

    def add(src, repository="analysis", expected=None):
        src = Path(src)
        data = read(src)
        need(expected is None or digest(data) == expected, "receipt hash: " + str(src))
        base = {"analysis": root, "raw": QUEUE / "raw", "evidence": QUEUE}[repository]
        rel = src.relative_to(base)
        need(not rel.is_absolute() and ".." not in rel.parts, "unsafe destination")
        key = repository + "/" + str(rel)
        e = dict(source=str(src), destination=key, sha256=digest(data), bytes=len(data))
        need(key not in entries or entries[key] == e, "destination collision")
        entries[key] = e
        return data

    for probe, count in (("freeflow", 125), ("values", 120)):
        hashes = c["source_adoption"]["sha256"][probe]
        directory = QUEUE / "raw/data" / ("traces_" + probe) / (
            ("freeflow_" if probe == "freeflow" else "") + LABEL)
        need(len(hashes) == c["source_adoption"]["counts"][probe] == count, "raw count")
        need({p.stem for p in directory.glob("*.json")} == set(hashes), "raw inventory")
        for sid, sha in hashes.items():
            add(directory / (sid + ".json"), "raw", sha)

    for name, directory, pin in (("fork", FORK, FORK_SHA), ("finish", STATE, SPEC_SHA)):
        need(digest(read(directory / "spec.json")) == pin, "spec drift")
        spec, tasks, rows = common.snapshot(directory)
        snapshots[name] = rows
        need(spec["input_hashes"][str(directory / "config.json")] ==
             digest(read(directory / "config.json")), "config binding")
        need(len(rows) == (1336 if name == "fork" else 10), "job inventory")
        if name == "finish":
            need(all(r[1] == "done" for r in rows), "nonterminal finish")
        for jid, state, attempts, receipts in rows:
            task = tasks[jid]
            need(task["model"] == LABEL and 0 <= attempts <= task["max_attempts"], "task drift")
            if state != "done":
                continue
            receipt = json.loads(receipts or "{}")
            sid = jid.rsplit("/", 1)[-1]
            if name == "fork" and "/bv1/" in jid and sid in SAMPLES:
                out = oldroot / "analysis/freeflow/personality-eval-bv1/arms" / variant.ARM / "outputs" / LABEL / (sid + ".md")
                expected = {str(out), str(out) + ".provenance.json",
                            str(oldphase / "bv1_bindings_luna_v1_targeted" / (sid + ".json"))}
            else:
                expected = set(task["outputs"])
            need(bool(receipt) and set(receipt) == expected, "receipt set: " + jid)
            for filename, sha in receipt.items():
                src = Path(filename)
                need(digest(read(src)) == sha, "original receipt hash")
                if name == "fork":
                    if src.is_relative_to(oldphase):
                        add(phase / src.relative_to(oldphase), expected=sha)
                    elif src.is_relative_to(oldroot):
                        add(root / src.relative_to(oldroot), expected=sha)
                    elif src.is_relative_to(QUEUE / "raw"):
                        add(src, "raw", sha)
                    else:
                        need(False, "unscoped receipt")
                else:
                    add(src, expected=sha)
    need(load(STATE / "terminal.json") == {"engine_result": "complete"}, "terminal")
    outputs = {}
    need({p.stem for p in (phase / "bv1_bindings_luna_v1_targeted").glob("*.json")} == SAMPLES,
         "targeted inventory")
    for sid, sha in c["source_adoption"]["sha256"]["freeflow"].items():
        targeted = sid in SAMPLES
        arm = variant.ARM if targeted else variant.V1
        out = root / "analysis/freeflow/personality-eval-bv1/arms" / arm / "outputs" / LABEL / (sid + ".md")
        data = add(out)
        binding = load(phase / ("bv1_bindings_luna_v1_targeted" if targeted else "bv1_bindings_luna_v1") / (sid + ".json"))
        need(binding == dict(source_sha256=sha, output_sha256=digest(data), evaluator_arm=arm), "essay binding")
        need(bool(list((phase / "freeflow_bv1_luna_v1/attempt_responses" /
                        (c["id_prefix"] + "_BV1_" + sid)).glob("*.json"))), "original attempts absent")
        if targeted:
            sidecar = load(Path(str(out) + ".provenance.json"))
            ref = Path(sidecar["attempt_record"])
            need(len(ref.parts) == 2 and ".." not in ref.parts and not ref.is_absolute(), "attempt path")
            attempt = load(phase / "freeflow_bv1_luna_v1_targeted/attempt_responses" / ref)
            previous = predecessor.LABEL
            predecessor.LABEL = LABEL
            try:
                predecessor.check_variant(data, binding, sidecar, attempt, sha, sid, c["id_prefix"])
            finally:
                predecessor.LABEL = previous
        outputs[LABEL + "/" + sid + ".json"] = str(out)
    manifest = list(csv.DictReader(read(phase / "freeflow_bv1_luna_v1/sample_manifest.tsv").decode().splitlines(), delimiter="\t"))
    need(len(manifest) == 125 and {r["sample_id"]: r["output_file"] for r in manifest} == outputs, "mixed manifest")
    verified = load(RETRY / "verified.json")
    holdpath = QUEUE / "state/qa-holds/colab-yi-34b-chat.json"
    add(holdpath, "evidence", verified["parent_hold_sha256"])
    need(verified["task"] == LABEL + "/a/G3_25/kimi-k2-6"
         and verified["attempt"] == 1 and verified["production_validation"] is True, "retry receipt")
    need(load(RETRY / "dispatch.json") == dict(max_requests=1, task=verified["task"]), "retry dispatch")
    need(load(STATE / "values-recovery-receipt.json") == verified, "adopted retry receipt")
    retryphase = Path(load(RETRY / "config.json")["phase"])
    retryout = Path(verified["output"])
    need(retryphase.is_relative_to(root) and retryout == retryphase / "samples/G3_25/layer_a/kimi-k2-6.jsonl", "retry scope")
    add(retryout, expected=verified["sha256"])
    add(phase / "samples/G3_25/layer_a/kimi-k2-6.jsonl", expected=verified["sha256"])
    hold = load(holdpath)
    need(digest(read(ORIGINAL / "spec.json")) == hold["spec_sha256"], "original spec")
    original_config = ORIGINAL / "models" / (LABEL + ".json")
    need(digest(read(original_config)) ==
         load(ORIGINAL / "spec.json")["input_hashes"][str(original_config)], "original config binding")
    with closing(sqlite3.connect(f"file:{ORIGINAL}/state.sqlite?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        held = db.execute("SELECT id,state,attempts,next_at,pid,started,reason,receipts FROM jobs ORDER BY id").fetchall()
    need(digest(json.dumps(held).encode()) == hold["rows_sha256"], "held rows changed")
    snapshots["original_hold_full_rows"] = held
    snapshots["original"] = common.snapshot(ORIGINAL)[2]
    for failure in hold["failures"]:
        for log in failure["logs"]:
            add(log["path"], "evidence", log["sha256"])
    ready = load(phase / "QUEUE_ANALYSIS_READY.json")
    need(ready["state"] == "analysis_only_awaiting_review" and ready["model"] == SLUG
         and ready["source_adoption"] == c["source_adoption"]
         and ready["raw_counts"] == {"freeflow": 125, "values": 120}
         and ready["bv1"] == {"bv1": 125, "bv1_variant_arms": dict.fromkeys(SAMPLES, variant.ARM)}
         and all(ready[k] is False for k in ("publication_complete", "website_touched", "site_integration_performed")), "readiness")
    for directory, repo in ((phase, "analysis"), (retryphase, "analysis"),
                            (oldphase, "evidence"), (RETRY, "evidence")):
        for src in sorted(directory.rglob("*")):
            need(not src.is_symlink(), "evidence symlink")
            if src.is_file():
                add(src, repo)
    for directory in (STATE, FORK):
        for name in ("config.json", "spec.json"):
            add(directory / name, "evidence")
    for name in ("terminal.json", "values-recovery-receipt.json"):
        add(STATE / name, "evidence")
    add(ORIGINAL / "spec.json", "evidence")
    add(ORIGINAL / "models" / (LABEL + ".json"), "evidence")
    for name in ("aggregate.md", "packet.md", "packet.metadata.json"):
        add(root / "analysis/freeflow/personality-aggregates" / LABEL / name)
    for name, directory in (("fork", FORK), ("finish", STATE), ("original", ORIGINAL)):
        need(common.snapshot(directory)[2] == snapshots[name], "queue changed during inspection")
    return dict(import_complete=True, blockers=[], label=LABEL,
                task_snapshots=snapshots, verified_essay_count=125,
                variant_samples=sorted(SAMPLES), isolated_values_recovery=verified,
                entries=sorted(entries.values(), key=lambda e: e["destination"]))


if __name__ == "__main__":
    print(json.dumps(inspect(), indent=2))
