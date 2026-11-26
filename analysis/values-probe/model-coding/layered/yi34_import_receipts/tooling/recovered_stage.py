#!/usr/bin/env python3
"""Offline Gemma recovered-variant inspection. Never publish or relabel."""
import argparse
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path

import stage as base

HOME = Path(__file__).resolve().parent
QUEUE = HOME.parent / "colab-batch-queue"
STATE = QUEUE / "state/gemma-targeted-fork-v2"
LABEL = "gemma-2-2b-it-colab-vllm-bf16-r299a8560"
SLUG = "gemma-2-2b-it"
ARM = "bv1-luna-v1-targeted-20261016"
SAMPLES = {"LONG_1", "LONG_8", "MID_6", "MID_9", "OPEN_4"}
NOTE = "a468a4f9f8d50f32617ab745facf605658ac4a9b66ddab11052d4158b3dc27ea"
ROOT = QUEUE / "analysis-worktree"
PHASE = ROOT / base.LAYERED / (
    "recovery_complete_v2_capture_overnight-20261125-gemma-2-2b-it_" + LABEL)
V1 = "bv1-luna-v1-20260929"
ARMS = ROOT / "analysis/freeflow/personality-eval-bv1/arms"
AUTH = "colab-gemma2-2b-JNwZVV-v1"
RETRY_STATE = STATE.with_name("gemma-values-recovery-v1")
RETRY_PHASE = PHASE.with_name(PHASE.name.replace("recovery_complete_v2_", "recovery_v1_"))
RETRIES = {"CTRL1_4": "kimi-k2-6", "CTRL2_1": "glm-4-7"}


def paths(sid, targeted):
    out = ARMS / (ARM if targeted else V1) / "outputs" / LABEL / (sid + ".md")
    bind = PHASE / ("bv1_bindings_luna_v1_targeted" if targeted else "bv1_bindings_luna_v1") / (sid + ".json")
    return out, Path(str(out) + ".provenance.json"), bind


def expected_receipts(jid, original):
    if jid in {LABEL + "/bv1/" + sid for sid in SAMPLES}:
        sid = jid.rsplit("/", 1)[1]
        if original != [str(paths(sid, False)[0])]:
            raise ValueError("unexpected original BV1 spec")
        return set(map(str, paths(sid, True)))
    return set(original)


def checked(path, root):
    path, root = Path(path), Path(root)
    if not path.is_relative_to(root) or ".." in path.parts:
        raise ValueError("outside scope: " + str(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("symlink input: " + str(path))
    return path.read_bytes()


def binding(binding_record, attempt, output, source_hash, sample):
    if binding_record != dict(source_sha256=source_hash,
                              output_sha256=base.digest(output),
                              evaluator_arm=ARM):
        raise ValueError("variant binding mismatch: " + sample)
    expected = dict(arm=ARM, evidence_rule="sentence",
                    repair_note_sha256=NOTE, sample_id=f"{LABEL}/{sample}.json",
                    source_sha256=source_hash, http_status=200, qa_pass=True,
                    qa_reason="")
    if any(attempt.get(k) != v for k, v in expected.items()):
        raise ValueError("variant attempt provenance mismatch: " + sample)
    content = attempt["response"]["choices"][0]["message"]["content"]
    if output != (content.strip() + "\n").encode():
        raise ValueError("variant response/output mismatch: " + sample)


def verify_sidecar(prov, record, attempt, output, sha, sid):
    expected = dict(arm=ARM, evidence_rule="sentence", repair_note_sha256=NOTE,
                    sample_id=f"{LABEL}/{sid}.json", source_sha256=sha,
                    request_sha256=base.digest(json.dumps(attempt["request"], sort_keys=True).encode()),
                    output_sha256=base.digest(output), attempt_record=record)
    if prov != expected:
        raise ValueError("variant provenance mismatch: " + sid)


def manifest():
    config_bytes = checked(STATE / "config.json", STATE)
    c = json.loads(config_bytes)
    if (c["label"] != LABEL or c["slug"] != SLUG
            or Path(c["analysis_root"]) != ROOT or Path(c["phase"]) != PHASE
            or c["bv1_evaluator"] != "bv1-luna-v1-20260929"):
        raise ValueError("outside recovered Gemma profile")
    spec_bytes = checked(STATE / "spec.json", STATE)
    spec = json.loads(spec_bytes)
    if base.digest(spec_bytes) != "7cc9d712e077ccc187836ed5ea389bf720d2c19b4511c06499773a9ea540569b":
        raise ValueError("unexpected fork specification")
    if spec["input_hashes"].get(str(STATE / "config.json")) != base.digest(config_bytes):
        raise ValueError("spec/config binding mismatch")
    blockers, missing, entries = [], [], {}

    def add(repo, src, dest, expected=None):
        base.safe_destination(dest)
        root = {"analysis": ROOT, "raw": QUEUE / "raw", "evidence": STATE,
                "retry_evidence": RETRY_STATE}[repo]
        src = Path(src)
        if not src.exists():
            missing.append(str(src))
            return
        data = checked(src, root)
        sha = base.digest(data)
        if expected is not None and sha != expected:
            raise ValueError("hash mismatch: " + str(src))
        key = (repo, dest)
        entry = dict(repository=repo, source=str(src), destination=dest,
                     sha256=sha, bytes=len(data))
        if key in entries and entries[key] != entry:
            raise ValueError("destination collision")
        entries[key] = entry

    # Use the complete Phi import contract, not a hand-selected subset.
    phi_bytes = checked(HOME / "phi-medium/manifest.json", HOME)
    if base.digest(phi_bytes) != "808749f478a57d9247d947db78dd5a0a52c7b2b288e1287fcebf91d594d56c76":
        raise ValueError("unexpected Phi contract")
    phi = json.loads(phi_bytes)
    if not phi["import_complete"] or phi["missing"] or phi["blockers"]:
        raise ValueError("Phi contract is incomplete")
    phi_label, phi_slug = phi["label"], "phi-3-medium-4k-instruct"
    phi_phase = "capture_overnight-20261125-" + phi_slug + "_" + phi_label
    deferred = [str((PHASE / Path(d).name).relative_to(ROOT)) for d in phi["deferred_integration"]]
    inapplicable = {p for sid in SAMPLES for p in paths(sid, False)[::2]}
    for e in phi["entries"]:
        if e["repository"] != "analysis" or "/attempt_responses/" in e["destination"]:
            continue
        dest = e["destination"].replace(phi_phase, PHASE.name).replace(
            phi_label, LABEL).replace(phi_slug, SLUG)
        if ROOT / dest in inapplicable:
            if (ROOT / dest).exists() or (ROOT / dest).is_symlink():
                raise ValueError("ambiguous v1 and targeted output: " + dest)
            continue
        if Path(dest).name in base.POST_INTEGRATION:
            deferred.append(dest)
        else:
            add("analysis", ROOT / dest, dest)
    for probe, count in (("freeflow", 125), ("values", 120)):
        hashes = c["source_adoption"]["sha256"][probe]
        if len(hashes) != count or c["source_adoption"]["counts"][probe] != count:
            raise ValueError("raw counts mismatch")
        directory = (QUEUE / "raw/data" / ("traces_" + probe)
                     / (("freeflow_" if probe == "freeflow" else "") + LABEL))
        if {p.stem for p in directory.glob("*.json")} != set(hashes):
            raise ValueError("raw sample set mismatch")
        for sid, sha in hashes.items():
            src = directory / (sid + ".json")
            add("raw", src, str(src.relative_to(QUEUE / "raw")), sha)

    # Read SQLite only; a transaction gives a coherent snapshot including WAL.
    db = sqlite3.connect(f"file:{STATE / 'state.sqlite'}?mode=ro", uri=True)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        jobs = db.execute("SELECT id,state,attempts,receipts FROM jobs").fetchall()
        meta = dict(db.execute("SELECT k,v FROM meta"))
        repairs = db.execute("SELECT authorization,id,used,allowance FROM targeted_repairs ORDER BY id").fetchall()
        events = db.execute("SELECT id,event,details FROM events WHERE event LIKE 'bv1_targeted_repair_%' ORDER BY rowid").fetchall()
    finally:
        db.close()
    if meta.get("spec") != base.digest(json.dumps(spec, sort_keys=True).encode()):
        raise ValueError("database/spec binding mismatch")
    tasks = {t["id"]: t for t in spec["tasks"]}
    if len(tasks) != len(spec["tasks"]) or set(tasks) != {j[0] for j in jobs}:
        raise ValueError("task set mismatch")
    for jid, state, attempts, receipts in jobs:
        task = tasks[jid]
        if task["model"] != LABEL:
            raise ValueError("foreign task")
        if state != "done":
            blockers.append(f"nonterminal task: {jid}: {state}")
            continue
        receipt = json.loads(receipts or "{}")
        if set(receipt) != expected_receipts(jid, task["outputs"]) or not 0 <= attempts <= task["max_attempts"]:
            raise ValueError("task receipt/attempt mismatch: " + jid)
        for src, sha in receipt.items():
            path = Path(src)
            repo = "raw" if path.is_relative_to(QUEUE / "raw") else "analysis"
            root = QUEUE / "raw" if repo == "raw" else ROOT
            if repo == "analysis" and not (path.is_relative_to(PHASE) or LABEL in path.parts
                    or (jid == LABEL + "/synthesis" and path in {
                        ROOT / "analysis/freeflow/personality-model-cards/cards" / (SLUG + ".md"),
                        ROOT / "analysis/freeflow/personality-model-profiles/profiles" / (SLUG + ".md")})):
                raise ValueError("foreign output")
            add(repo, path, str(path.relative_to(root)), sha)

    # Preserve every phase artifact, including original and variant attempts.
    failures = {PHASE / "samples" / sid / "layer_a" / (coder + ".failed.jsonl")
                for sid, coder in RETRIES.items()}
    for src in sorted(PHASE.rglob("*")):
        if src.is_symlink():
            raise ValueError("symlink phase artifact")
        if src.is_file():
            bits = src.relative_to(PHASE).parts
            is_attempt = (len(bits) == 4 and bits[0] in {"freeflow_bv1_luna_v1", "freeflow_bv1_luna_v1_targeted"}
                          and bits[1] == "attempt_responses" and re.fullmatch(r"[0-9]+\.json", bits[3])
                          and bits[2] in {c["id_prefix"] + "_BV1_" + sid for sid in
                              (SAMPLES if bits[0].endswith("_targeted") else c["source_adoption"]["sha256"]["freeflow"])})
            if ("analysis", str(src.relative_to(ROOT))) not in entries and not is_attempt and src not in failures:
                raise ValueError("unrecognized phase artifact: " + str(src))
            add("analysis", src, str(src.relative_to(ROOT)))
    bindings = PHASE / "bv1_bindings_luna_v1_targeted"
    if {p.stem for p in bindings.glob("*.json")} != SAMPLES:
        raise ValueError("unexpected variant sample set")
    if {(auth, jid) for auth, jid, _, _ in repairs} != {(AUTH, LABEL + "/bv1/" + sid) for sid in SAMPLES}:
        raise ValueError("targeted repairs outside scope")
    success_records = {}
    free = c["source_adoption"]["sha256"]["freeflow"]
    originals = PHASE / "freeflow_bv1_luna_v1/attempt_responses"
    fingerprints = {str(p.relative_to(PHASE)):base.digest(checked(p, PHASE)) for p in originals.rglob("*.json")}
    if base.digest(json.dumps(fingerprints, sort_keys=True).encode()) != "1c2656c410f484ea9ced9228d1028cfb181fc34b25f0606a4a3a422436dc52d9":
        raise ValueError("original attempt inventory changed")
    for sid, sha in free.items():
        prefix = c["id_prefix"] + "_BV1_" + sid
        if not list((originals / prefix).glob("*.json")):
            raise ValueError("missing original attempts: " + sid)
        output, sidecar, bind = paths(sid, sid in SAMPLES)
        data = checked(output, ROOT)
        record = json.loads(checked(bind, PHASE))
        if sid not in SAMPLES:
            if record.get("source_sha256") != sha or record.get("output_sha256") != base.digest(data):
                raise ValueError("v1 binding mismatch: " + sid)
            continue
        prov = json.loads(checked(sidecar, ROOT))
        ref = prov["attempt_record"]
        if not re.fullmatch(re.escape(prefix) + r"/[0-9]+\.json", ref):
            raise ValueError("wrong immutable attempt path: " + sid)
        attempt = json.loads(checked(PHASE / "freeflow_bv1_luna_v1_targeted/attempt_responses" / ref, PHASE))
        binding(record, attempt, data, sha, sid)
        verify_sidecar(prov, ref, attempt, data, sha, sid)
        jid = LABEL + "/bv1/" + sid
        auth, _, used, limit = next(row for row in repairs if row[1] == jid)
        applied = [json.loads(v) for i, e, v in events if i == jid and e == "bv1_targeted_repair_applied"]
        if not (1 <= used <= limit == 2 and applied == [dict(arm=ARM, authorization=auth,
                attempt=used, limit=limit, output=str(output), output_sha256=base.digest(data))]):
            raise ValueError("finalize event mismatch: " + sid)
        success_records[sid] = ref
    rows = list(csv.DictReader(checked(PHASE / "freeflow_bv1_luna_v1/sample_manifest.tsv", PHASE).decode().splitlines(), delimiter="\t"))
    if len(rows) != 125 or {(r["sample_id"], r["output_file"]) for r in rows} != {
            (f"{LABEL}/{s}.json", str(paths(s, s in SAMPLES)[0])) for s in free}:
        raise ValueError("sample manifest arm/output mismatch")
    ready = PHASE / "QUEUE_ANALYSIS_READY.json"
    if not ready.exists():
        blockers.append("QUEUE_ANALYSIS_READY missing")
    else:
        r = json.loads(checked(ready, PHASE))
        if (r.get("state") != "analysis_only_awaiting_review"
                or r.get("model") != SLUG
                or r.get("source_adoption") != c["source_adoption"]
                or r.get("raw_counts") != {"freeflow": 125, "values": 120}
                or any(r.get(k) is not False for k in (
                    "publication_complete", "website_touched", "site_integration_performed"))):
            raise ValueError("invalid terminal readiness")
        # A v1-only terminal declaration cannot attest the recovered mixture.
        if r.get("bv1") != {"bv1": 125, "bv1_variant_arms": dict.fromkeys(SAMPLES, ARM)}:
            blockers.append("terminal record does not attest targeted variant provenance")
    # The fork adopted the retry OUTPUTS, not the successful attempt logs.
    # Keep both failed originals and these separately named recovery records.
    for sid, coder in RETRIES.items():
        rel = Path("samples") / sid / "layer_a" / (coder + ".jsonl")
        receipt = json.loads(checked(RETRY_STATE / (sid + ".receipt.json"), RETRY_STATE))
        digest = base.digest(checked(PHASE / rel, PHASE))
        if receipt != dict(task=f"{LABEL}/a/{sid}/{coder}", sha256=digest,
                           parent_hold_sha256="26e8543a73da119e833a564ecb06c0cc6659b5991fd06c2fea4ffa01d7731f07",
                           output=str(RETRY_PHASE / rel)):
            raise ValueError("values retry adoption mismatch: " + sid)
        for src in (rel, rel.with_suffix(".attempts.jsonl"), rel.parent.parent / "manifest.jsonl"):
            add("analysis", RETRY_PHASE / src, str((RETRY_PHASE / src).relative_to(ROOT)),
                digest if src == rel else None)
        retry_attempt = json.loads(checked(RETRY_PHASE / rel.with_suffix(".attempts.jsonl"), RETRY_PHASE))
        parsed = json.loads(retry_attempt["raw_text"].strip().removeprefix("<JSON>").removesuffix("</JSON>").strip())
        adopted = json.loads(checked(PHASE / rel, PHASE))
        if (retry_attempt["layered_id"] != c["id_prefix"] + "_" + sid
                or retry_attempt["coder_key"] != coder or parsed.get("layered_id") != adopted["layered_id"]
                or any(adopted[k] != v for k,v in parsed.items())):
            raise ValueError("values retry response mismatch: " + sid)
        for ext in (".failed.jsonl", ".attempts.jsonl"):
            original = json.loads(checked(PHASE / rel.with_suffix(ext), PHASE))
            if original["layered_id"] != retry_attempt["layered_id"] or original["coder_key"] != coder:
                raise ValueError("wrong original values attempt: " + sid)
        add("retry_evidence", RETRY_STATE / (sid + ".receipt.json"), sid + ".receipt.json")
    status = json.loads(checked(STATE / "status.json", STATE))
    if (status.get("counts") != {"done": 1336} or status.get("state") != "complete"
            or status.get("blockers") != [] or status.get("models") != {LABEL: {"done": 1336}}
            or status.get("completion_boundary") != "analysis_only_awaiting_review"
            or json.loads(checked(STATE / "terminal.json", STATE)) != {"engine_result": "complete"}
            or json.loads(checked(STATE / "host-terminal.json", STATE)).get("rc") != 0):
        raise ValueError("incomplete fork terminal records")
    for name in ("config.json", "spec.json", "terminal.json", "host-terminal.json", "status.json"):
        add("evidence", STATE / name, name)
    if missing:
        blockers.append("Phi-equivalent artifacts missing")
    return dict(schema="gemma-recovered-variant-stage-v1", label=LABEL,
                evaluator_variant=ARM, variant_samples=sorted(SAMPLES),
                repair_note_sha256=NOTE, publication_authorized=False,
                import_complete=not blockers, entries=list(entries.values()),
                missing=sorted(set(missing)), blockers=blockers,
                deferred_integration=deferred, task_snapshot=jobs,
                immutable_successful_attempts=success_records, targeted_repairs=repairs,
                repair_events=events,
                notes=["No variant files are renamed to v1.",
                       "Terminal analysis readiness is not publication readiness."])


def stage(m, name):
    if not name.startswith("recovered_stage_") or Path(name).name != name:
        raise ValueError("stage must be a new recovered_stage_* child")
    # Revalidate all live evidence before writing any bundle.
    if manifest() != m:
        raise ValueError("inputs changed; rerun")
    base.stage(m, name)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", metavar="recovered_stage_NEW")
    a = p.parse_args()
    try:
        m = manifest()
        if a.stage:
            stage(m, a.stage)
        print(json.dumps(m, indent=2))
        return 0 if m["import_complete"] else 2
    except (ValueError, KeyError, OSError, sqlite3.Error, TypeError, IndexError) as e:
        print(json.dumps({"import_complete": False, "error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
