#!/usr/bin/env python3
"""Compare semantic hash multisets, preserving prior rows and duplicate counts."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from run import PHASE, ROOT, CELLS

DATA = ROOT / "analysis/values-probe/final/data"
SOURCE = PHASE.name
FILES = ["manifest_valid.jsonl", "layer_a_consensus.jsonl", "posture_consensus.jsonl"]
FILES += [f"{layer}_coder_{coder}.jsonl"
          for layer in ["layer_a", "posture"]
          for coder in ["kimi-k2-6", "glm-4-7", "qwen3-6-35b-a3b"]]


def signature(lines):
    old = []
    new = []
    for line in lines:
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == "glm-4-9b-chat":
            row["model"] = "glm-4-9b-chat-hf"
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if row.get("final_source") == SOURCE:
            new.append(row)
        else:
            old.append(digest)
    combined = hashlib.sha256("".join(sorted(old)).encode()).hexdigest()
    return {"old_count": len(old), "old_multiset_sha256": combined}, new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    baseline = PHASE / "baseline-final-signatures-alias-aware.json"
    if args.baseline:
        assert not baseline.exists()
        result = {}
        for name in FILES:
            source = f"fdfb1d6d:analysis/values-probe/final/data/{name}"
            proc = subprocess.Popen(["git", "show", source], cwd=ROOT, stdout=subprocess.PIPE, text=True)
            sig, new = signature(proc.stdout)
            assert proc.wait() == 0
            assert not new
            result[name] = sig
        baseline.write_text(json.dumps(result, indent=2) + "\n")
        print("Saved semantic multiset baseline")
        return
    before = json.loads(baseline.read_text())
    results = {}
    expected = {f"P36_{model}_{cond}_{n}" for model, _ in CELLS.values()
                if model != "glm-4-9b-chat-hf"
                for cond, count in {"CTRL1": 10, "CTRL2": 10, "CTRL3": 10, "G1": 30, "G2": 30, "G3": 30}.items()
                for n in range(1, count + 1)}
    for name in FILES:
        with (DATA / name).open() as handle:
            sig, new = signature(handle)
        assert sig == before[name], (name, "prior rows changed")
        assert len(new) == 240 and {r["layered_id"] for r in new} == expected, name
        results[name] = {**sig, "new_count": len(new), "prior_rows_preserved_except_glm_model_alias": True}
    (PHASE / "integration-check.json").write_text(json.dumps(results, indent=2) + "\n")
    print("PASS: nine final files preserve all prior rows except the explicit GLM model alias and add 240 each")


if __name__ == "__main__":
    main()
