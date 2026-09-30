#!/usr/bin/env python3
"""Isolated local-checkpoint analysis; stops at ready-for-Lume, not publication."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import subprocess
import sys
import shutil
from collections import Counter
from pathlib import Path

PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[4]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
LAYERED = PHASE.parent
BASE = LAYERED / "phase35_union_alpha_20260917"
OLD = LAYERED / "phase36_historical_handoff_20260918"
CODERS = ["qwen3-6-35b-a3b", "kimi-k2-6", "glm-4-7"]
CELL = "qwen2-5-7b-instruct-local-transformers-mps-auto-ra09a3545"
MODEL = "Qwen/Qwen2.5-7B-Instruct"
SLUG = "qwen2-5-7b-instruct"
MANIFEST = PHASE / "manifest.jsonl"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def write_rows(path, data):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in data))


def run(script, *args):
    subprocess.run([sys.executable, str(script), *map(str, args)], cwd=ROOT, check=True)


def coverage(folder, expected):
    for coder in CODERS:
        data = rows(folder / (coder + ".jsonl"))
        assert len(data) == len(expected) and {r["layered_id"] for r in data} == expected
        assert all(r.get("parse_clean", True) for r in data)


def prepare():
    repair = module("qwen_repair_audit", CORPUS / ".local-runtime/repair_qwen25_20260918.py")
    original = json.loads((repair.ARCHIVE / "manifest.json").read_text())
    accepted = json.loads((repair.RUN / "state.json").read_text())["accepted"]
    hashes = {}
    manifest = []
    counts = {"freeflow": Counter(), "values": Counter()}
    for p in repair.paths():
        rel = str(p.relative_to(CORPUS))
        d = json.loads(p.read_text())
        assert not repair.reasons(d), rel
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        expected_hash = accepted[rel]["sha256"] if rel in accepted else original["original_sha256"][rel]
        assert h == expected_hash, rel
        hashes[rel] = h
        probe = "values" if "traces_values" in rel else "freeflow"
        counts[probe][d["condition"]] += 1
        if probe == "values":
            condition = d["condition"]
            manifest.append(dict(
                layered_id=f"P38_{SLUG}_{p.stem}", model=SLUG, model_family="Qwen",
                cell=CELL, sample_id=p.stem, condition=condition,
                prompt=d["prompt"], response=d["result"], provider=d["provider"],
                model_requested=MODEL, trace_path=rel, source_sha256=h,
                processing_chain="world_change_wishes" if condition in {"CTRL3", "G3"} else "stated_values",
                selection_stratum=PHASE.name, is_enriched=False))
    assert counts["freeflow"] == dict.fromkeys(["SHORT", "MID", "LONG", "OPEN", "VARY"], 25)
    assert counts["values"] == {"CTRL1": 10, "CTRL2": 10, "CTRL3": 10, "G1": 30, "G2": 30, "G3": 30}
    if MANIFEST.exists():
        assert rows(MANIFEST) == manifest
    else:
        write_rows(MANIFEST, manifest)
    out = PHASE / "source-hashes.json"
    if out.exists():
        assert json.loads(out.read_text()) == hashes
    else:
        out.write_text(json.dumps(hashes, indent=2) + "\n")
    return manifest


def freeflow():
    validator = module("qwen_existing_bv1", ROOT / "analysis/freeflow/personality-eval-bv1/run_full_bv1.py")
    outputs = ROOT / "analysis/freeflow/personality-eval-bv1/outputs" / CELL
    for p in outputs.glob("*.md"):
        if not validator.valid_output(p.read_text())[0]:
            backups = PHASE / "freeflow_bv1/rejected"
            backups.mkdir(parents=True, exist_ok=True)
            prior = list(backups.glob(p.stem + ".attempt-*.md"))
            assert len(prior) < 2, f"Three BV1 draws failed for {p.name}; review rather than reroll"
            shutil.copy2(p, backups / f"{p.stem}.attempt-{len(prior)+1}.md")
    m = module("qwen_bv1", BASE / "run_freeflow_bv1.py")
    m.PHASE, m.ROOT, m.CELLS = PHASE, ROOT, {CELL}
    sys.argv = [sys.argv[0]]
    m.main()
    lock = ROOT / "logs/capture-harness-publication.lock"
    lock.parent.mkdir(exist_ok=True)
    with lock.open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        m = module("qwen_packets", BASE / "build_aggregate_packets.py")
        m.PHASE, m.ROOT, m.CELLS = PHASE, ROOT, {CELL: MODEL}
        m.main()
        m = module("qwen_assemble", BASE / "assemble_models.py")
        m.PHASE, m.ROOT, m.CELLS = PHASE, ROOT, {CELL: SLUG}
        m.main()


def values():
    la, posture = PHASE / "layer_a", PHASE / "posture_collapsed"
    la.mkdir(exist_ok=True)
    posture.mkdir(exist_ok=True)
    for coder in CODERS:
        run(LAYERED / "run_layer_a_coders.py", "--coder", coder, "--workers", 4,
            "--manifest", MANIFEST, "--outdir", la)
    expected = {r["layered_id"] for r in rows(MANIFEST)}
    coverage(la, expected)
    run(LAYERED / "build_layer_a_consensus.py", "--manifest", MANIFEST,
        "--outdir", la, "--coders", ",".join(CODERS))
    for coder in CODERS:
        run(LAYERED / "run_posture_coder_collapsed.py", "--coder", coder,
            "--manifest", MANIFEST, "--consensus", la / "consensus_300.jsonl",
            "--outdir", posture, "--workers", 4)
    coverage(posture, expected)
    run(LAYERED / "build_posture_collapsed_consensus.py", "--indir", posture,
        "--manifest", MANIFEST, "--out", posture / "consensus.jsonl")
    # Reuse bounded schema correction and full QA without editing old phases.
    sys.modules["run"] = sys.modules[__name__]
    module("qwen_schema", OLD / "repair_taxonomy.py").main()
    module("qwen_validate", OLD / "validate_coding.py").main()
    sys.path.insert(0, str(CORPUS / "scripts/capture_harness"))
    worker = module("qwen_values_finish", CORPUS / "scripts/capture_harness/worker.py")
    config = dict(analysis_root=str(ROOT), slug=SLUG, phase_name=PHASE.name)
    worker.adjudicate(config, PHASE, False)
    worker.values_report(config, PHASE, False)


def finish():
    prepare()
    s = json.loads((PHASE / "freeflow_bv1/status.json").read_text())
    assert s["samples"] == 125 and not s["problems"]
    bv = module("qwen_bv_validator", ROOT / "analysis/freeflow/personality-eval-bv1/run_full_bv1.py")
    outputs = ROOT / "analysis/freeflow/personality-eval-bv1/outputs" / CELL
    assert len(list(outputs.glob("*.md"))) == 125
    assert all(bv.valid_output(p.read_text())[0] for p in outputs.glob("*.md"))
    for folder in ["layer_a", "posture_collapsed", "posture_final"]:
        coverage(PHASE / folder, {r["layered_id"] for r in rows(MANIFEST)})
    final_votes = {c: {r["layered_id"]: r for r in rows(PHASE / "posture_final" / (c + ".jsonl"))}
                   for c in CODERS}
    labels = module("qwen_final_posture", LAYERED / "run_posture_coder_collapsed.py")
    for r in rows(PHASE / "posture_final/consensus.jsonl"):
        votes = Counter(final_votes[c][r["layered_id"]]["primary_label"] for c in CODERS)
        assert dict(votes) == r["collapsed_primary_label_votes"]
        assert votes[r["collapsed_primary_label"]] == r["collapsed_primary_label_support"]
        for c in CODERS:
            rec = final_votes[c][r["layered_id"]]
            assert rec["primary_label"] in labels.LABELS
            assert rec["value_holding"] == labels.HOLDING[rec["primary_label"]]
    baseline = json.loads((PHASE / "shared-index-baseline.json").read_text())
    for path, old_rows in baseline.items():
        current = json.loads((ROOT / path).read_text())
        assert all(r in current for r in old_rows), f"Pre-existing shared-index rows lost: {path}"
    for folder in ["personality-model-cards/cards", "personality-model-profiles/profiles"]:
        p = ROOT / "analysis/freeflow" / folder / (SLUG + ".md")
        assert p.exists() and len(p.read_text().split()) > 40
    report = PHASE / "release_candidate/reports" / (SLUG + ".md")
    assert report.exists()
    (PHASE / "ANALYSIS_READY.json").write_text(json.dumps(dict(
        state="analysis_complete_ready_for_lume", model=SLUG, cell=CELL,
        raw_counts={"freeflow": 125, "values": 120}, bv1=125,
        source_hashes_revalidated=True, values_coders=CODERS,
        adjudication=json.loads((PHASE / "adjudication.json").read_text()),
        publication_complete=False, editorial_assets_created=False,
        evidence_review="REVIEW.md",
        evidence_limitations={"non_verbatim_warnings": 63,
                              "suspect_coder_spans": 2,
                              "weakly_grounded_topic_consensus": "CTRL3_6: reduce_poverty"},
    ), indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["prepare", "freeflow", "values", "finish"])
    stage = parser.parse_args().stage
    prepare()
    if stage != "prepare":
        globals()[stage]()
