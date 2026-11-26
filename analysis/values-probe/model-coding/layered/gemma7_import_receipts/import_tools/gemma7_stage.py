#!/usr/bin/env python3
"""Read-only Gemma 7B IT handoff planner. No integration or publication commands."""
import argparse
import csv
import io
import json
from pathlib import Path
import sqlite3
import sys

sys.dont_write_bytecode = True
import q2514_import as common
import recovered_stage as variant

HOME = Path(__file__).resolve().parent
QUEUE = HOME.parent / "colab-batch-queue"
FORK = QUEUE / "remaining_recovery_colab-gemma-7b-it"
FINISH = QUEUE / "state/finish-gemma-7b-it"
RETRY = QUEUE / "state/gemma7-values-recovery-v1"
LABEL = "gemma-7b-it-colab-vllm-bf16-r9c5798d2"
SLUG = "gemma-7b-it"
SAMPLES = {"MID_5", "VARY_9"}
FORK_SHA = "40b467a3dba5683d9ce9e38292670c47584a15e89ee0af1ddce390c9fb93b096"
need, read, digest, load = common.need, common.read, common.digest, common.load


def check_variant(output, binding, sidecar, attempt, source_hash, sid, prefix):
    """Reuse Gemma predecessor's exact byte and provenance checks."""
    original = variant.LABEL
    variant.LABEL = LABEL
    try:
        variant.binding(binding, attempt, output, source_hash, sid)
        ref = sidecar["attempt_record"]
        need(len(Path(ref).parts) == 2 and Path(ref).parts[0] == prefix + "_BV1_" + sid
             and Path(ref).name.removesuffix(".json").isdigit(), "unsafe attempt reference")
        variant.verify_sidecar(sidecar, ref, attempt, output, source_hash, sid)
    finally:
        variant.LABEL = original


def inspect(finish_sha=None):
    entries, blockers, snapshots = {}, [], {}

    def add(src, repository, destination=None, expected=None):
        src = Path(src)
        data = read(src)
        need(expected is None or digest(data) == expected, "hash mismatch: " + str(src))
        root = {"analysis": QUEUE / "analysis-worktree", "raw": QUEUE / "raw",
                "evidence": QUEUE}[repository]
        rel = Path(destination) if destination else src.relative_to(root)
        need(not rel.is_absolute() and ".." not in rel.parts, "unsafe destination")
        key = repository + "/" + str(rel)
        e = dict(source=str(src), destination=key, sha256=digest(data), bytes=len(data))
        need(key not in entries or entries[key] == e, "destination collision")
        entries[key] = e
        return data

    c = load(FORK / "config.json")
    oldroot, oldphase = Path(c["analysis_root"]), Path(c["phase"])
    need(c["label"] == LABEL and c["slug"] == SLUG and c["model"] == "google/gemma-7b-it"
         and oldroot == FORK / "analysis" and oldphase == FORK / "phase", "model/roots drift")
    need(digest(read(FORK / "spec.json")) == FORK_SHA, "fork spec drift")
    for probe, count in (("freeflow", 125), ("values", 120)):
        hashes = c["source_adoption"]["sha256"][probe]
        need(len(hashes) == c["source_adoption"]["counts"][probe] == count, "raw count")
        directory = QUEUE / "raw/data" / ("traces_" + probe) / (
            ("freeflow_" if probe == "freeflow" else "") + LABEL)
        need({p.stem for p in directory.glob("*.json")} == set(hashes), "raw inventory")
        for sid, sha in hashes.items():
            add(directory / (sid + ".json"), "raw", expected=sha)

    # Check fork receipts without pretending blocked values have completed.
    spec, tasks, rows = common.snapshot(FORK)
    need(len(rows) == 1336, "fork task inventory")
    need(spec["input_hashes"].get(str(FORK / "config.json")) ==
         digest(read(FORK / "config.json")), "fork config binding")
    snapshots["fork"] = rows
    for jid, state, attempts, receipts in rows:
        task = tasks[jid]
        need(task["model"] == LABEL and 0 <= attempts <= task["max_attempts"], "foreign task")
        if state != "done":
            continue
        receipt = json.loads(receipts or "{}")
        sid = jid.rsplit("/", 1)[-1]
        targeted = "/bv1/" in jid and sid in SAMPLES
        if targeted:
            out = oldroot / "analysis/freeflow/personality-eval-bv1/arms" / variant.ARM / "outputs" / LABEL / (sid + ".md")
            expected = {str(out), str(out) + ".provenance.json",
                        str(oldphase / "bv1_bindings_luna_v1_targeted" / (sid + ".json"))}
        else:
            expected = set(task["outputs"])
        need(bool(receipt) and set(receipt) == expected, "receipt set: " + jid)
        for filename, sha in receipt.items():
            need(digest(read(filename)) == sha, "fork receipt hash: " + filename)
    free = c["source_adoption"]["sha256"]["freeflow"]
    manifest_path = oldphase / "freeflow_bv1_luna_v1/sample_manifest.tsv"
    manifest = (list(csv.DictReader(io.StringIO(read(manifest_path).decode()), delimiter="\t"))
                if manifest_path.exists() else None)
    outputs = {}
    for sid, sha in free.items():
        targeted = sid in SAMPLES
        arm = variant.ARM if targeted else variant.V1
        out = oldroot / "analysis/freeflow/personality-eval-bv1/arms" / arm / "outputs" / LABEL / (sid + ".md")
        data = read(out)
        binding = load(oldphase / ("bv1_bindings_luna_v1_targeted" if targeted else "bv1_bindings_luna_v1") / (sid + ".json"))
        need(binding == dict(source_sha256=sha, output_sha256=digest(data), evaluator_arm=arm), "essay binding")
        if targeted:
            prov = load(Path(str(out) + ".provenance.json"))
            ref = Path(prov["attempt_record"])
            need(len(ref.parts) == 2 and ".." not in ref.parts and not ref.is_absolute(), "attempt path")
            attempt = load(oldphase / "freeflow_bv1_luna_v1_targeted/attempt_responses" / ref)
            check_variant(data, binding, prov, attempt, sha, sid, c["id_prefix"])
        outputs[LABEL + "/" + sid + ".json"] = str(out)
    if manifest is None:
        blockers.append("fork essay sample_manifest.tsv absent; finish must produce mixed-arm manifest")
    else:
        need(len(manifest) == 125 and {r["sample_id"]: r["output_file"] for r in manifest} == outputs, "essay manifest")
    # Successful isolated values recovery is separate evidence, not a done fork job.
    verified = load(RETRY / "verified.json")
    need(verified["task"] == LABEL + "/a/G1_27/glm-4-7"
         and verified["state"] == "verified" and verified["production_validation"] is True
         and verified["original_receipts_unchanged"] is True
         and verified["publication_complete"] is False, "values recovery receipt")
    auth = load(RETRY / "authorization.json")
    need(auth["task"] == verified["task"] and auth["parent_hold_sha256"] == verified["parent_hold_sha256"]
         and auth["publication_authorized"] is False and 1 <= verified["attempt"] <= auth["max_attempts"] == 2,
         "values authorization")
    retry_output = Path(verified["output"])
    need(retry_output.is_relative_to(QUEUE / "analysis-worktree/analysis/values-probe/model-coding/layered")
         and retry_output.parts[-4:] == ("samples", "G1_27", "layer_a", "glm-4-7.jsonl"), "retry output scope")
    add(retry_output, "analysis", expected=verified["sha256"])
    for src in sorted(RETRY.rglob("*")):
        if src.is_file():
            add(src, "evidence")
    for src in sorted(retry_output.parents[3].rglob("*")):
        if src.is_file():
            add(src, "analysis")
    if not FINISH.exists():
        blockers.append("state/finish-gemma-7b-it absent: downstream values, synthesis and readiness not attested")
    else:
        # Deliberately fail closed: a future producer contract must be reviewed.
        actual = digest(read(FINISH / "spec.json"))
        fc = load(FINISH / "config.json")
        need(fc["label"] == LABEL and fc["model"] == "google/gemma-7b-it"
             and fc["source_adoption"] == c["source_adoption"], "finish model/source drift")
        fspec, ftasks, frows = common.snapshot(FINISH)
        snapshots["finish"] = frows
        need(fspec["input_hashes"].get(str(FINISH / "config.json")) ==
             digest(read(FINISH / "config.json")), "finish config binding")
        for jid, state, attempts, receipts in frows:
            task = ftasks[jid]
            need(task["model"] == LABEL and 0 <= attempts <= task["max_attempts"], "finish task")
            if state != "done":
                blockers.append("finish nonterminal: " + jid + ": " + state)
                continue
            receipt = json.loads(receipts or "{}")
            need(bool(receipt) and set(receipt) == set(task["outputs"]), "finish receipt set")
            for filename, sha in receipt.items():
                add(filename, "analysis", expected=sha)
        if not (FINISH / "terminal.json").exists():
            blockers.append("finish terminal.json absent")
        else:
            need(load(FINISH / "terminal.json") == {"engine_result": "complete"}, "finish terminal")
        for name in ("config.json", "spec.json"):
            add(FINISH / name, "evidence")
        blockers.append("finish producer contract requires owner integration review; observed spec SHA256=" + actual)
        if finish_sha != actual:
            blockers.append("finish specification is not explicitly pinned")
    blockers.append("No downstream integration/publication authority; this is a preparation-only handoff")
    return dict(schema="gemma7-prepublication-plan-v1", label=LABEL, import_complete=False,
                publication_authorized=False, blockers=blockers,
                variant_samples=sorted(SAMPLES), evaluator_variant=variant.ARM,
                verified_essay_count=125, isolated_values_recovery=verified,
                fork_counts={s: sum(r[1] == s for r in rows) for s in sorted({r[1] for r in rows})},
                evidence_entries=sorted(entries.values(), key=lambda e: e["destination"]),
                task_snapshots=snapshots,
                scope="Read-only partial evidence plan; no bundle copy, git, merge, site writes or posting")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--finish-spec-sha256", help="Owner-reviewed future spec pin; does not authorize integration")
    a = p.parse_args()
    try:
        result = inspect(a.finish_spec_sha256)
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as exc:
        result = dict(import_complete=False, publication_authorized=False, error=str(exc))
    print(json.dumps(result, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
