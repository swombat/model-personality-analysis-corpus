#!/usr/bin/env python3
"""Complete missing historical values analyses, without recollecting raw data."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[4]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
LAYERED = PHASE.parent
CODERS = ["qwen3-6-35b-a3b", "kimi-k2-6", "glm-4-7"]
CELLS = {
    "yi-6b-chat-local-transformers-bf16-r2dbf63b": ("yi-6b-chat", "Yi"),
    "chatglm2-6b-local-transformers427-mps-fp16-rd2e2d91": ("chatglm2-6b", "GLM"),
    "glm-4-9b-chat-hf-local-transformers-mps-auto-r8599336f": ("glm-4-9b-chat-hf", "GLM"),
}
EXPECTED = {"CTRL1": 10, "CTRL2": 10, "CTRL3": 10, "G1": 30, "G2": 30, "G3": 30}
MANIFEST = PHASE / "manifest_phase36.jsonl"
ROLE = re.compile(r"(?:<\|(?:im_start|user|assistant|system)\|>|(?:^|\n)\s*(?:user|assistant|system)\s*\n)", re.I)


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_rows(path, data):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in data))


def run(script, *args):
    subprocess.run([sys.executable, str(script), *map(str, args)], cwd=ROOT, check=True)


def prepare():
    manifest = []
    for cell, (model, family) in CELLS.items():
        counts = Counter()
        for path in sorted((CORPUS / "data/traces_values" / cell).glob("*.json")):
            raw = json.loads(path.read_text())
            text = raw.get("result", "")
            choice = raw["raw"]["choices"][0]
            assert text.strip() and not raw.get("error"), path
            assert choice["message"]["content"] == text and choice["finish_reason"] == "stop", path
            assert not ROLE.search(text) and not any(c in text for c in ["\ufffd", "\x00", "Ġ", "Ċ"]), path
            condition = raw["condition"]
            counts[condition] += 1
            manifest.append({
                "layered_id": f"P36_{model}_{path.stem}",
                "model": model, "model_family": family, "cell": cell,
                "sample_id": path.stem, "condition": condition,
                "prompt": raw["prompt"], "response": text,
                "provider": raw["provider"],
                "model_requested": raw.get("model_requested") or raw["model"],
                "trace_path": str(path.relative_to(CORPUS)),
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "processing_chain": "world_change_wishes" if condition in {"CTRL3", "G3"} else "stated_values",
                "selection_stratum": "phase36_historical_handoff_20260918",
                "is_enriched": False,
            })
        assert counts == EXPECTED, (cell, counts)
    assert len(manifest) == 360
    if MANIFEST.exists():
        assert rows(MANIFEST) == manifest, "Source changed since analysis began"
    else:
        write_rows(MANIFEST, manifest)
    return manifest


def coverage(folder, expected):
    for coder in CODERS:
        data = rows(folder / f"{coder}.jsonl")
        assert len(data) == len(expected) and {r["layered_id"] for r in data} == expected, (folder, coder)
        assert all(r.get("parse_clean", True) for r in data), (folder, coder, "parse")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    manifest = prepare()
    if args.prepare_only:
        print("Validated 360 source values samples")
        return
    expected = {r["layered_id"] for r in manifest}
    la = PHASE / "layer_a"
    posture = PHASE / "posture_collapsed"
    la.mkdir(exist_ok=True)
    posture.mkdir(exist_ok=True)
    for coder in CODERS:
        run(LAYERED / "run_layer_a_coders.py", "--coder", coder, "--workers", 6,
            "--manifest", MANIFEST, "--outdir", la)
    coverage(la, expected)
    run(LAYERED / "build_layer_a_consensus.py", "--manifest", MANIFEST,
        "--outdir", la, "--coders", ",".join(CODERS))
    for coder in CODERS:
        run(LAYERED / "run_posture_coder_collapsed.py", "--coder", coder,
            "--manifest", MANIFEST, "--consensus", la / "consensus_300.jsonl",
            "--outdir", posture, "--workers", 8)
    coverage(posture, expected)
    run(LAYERED / "build_posture_collapsed_consensus.py", "--indir", posture,
        "--manifest", MANIFEST, "--out", posture / "consensus.jsonl")
    splits = [r for r in rows(posture / "consensus.jsonl")
              if r.get("collapsed_primary_label_support", 0) < 2]
    (PHASE / "unresolved_posture.json").write_text(json.dumps(splits, indent=2) + "\n")
    print(f"First pass complete: 360 values, six coder streams; {len(splits)} posture splits", flush=True)


if __name__ == "__main__":
    main()
