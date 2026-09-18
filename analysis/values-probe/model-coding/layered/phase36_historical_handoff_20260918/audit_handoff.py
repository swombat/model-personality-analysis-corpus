#!/usr/bin/env python3
"""Read-only fidelity audit of all eight queue-complete historical cells."""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

from run import CORPUS, PHASE, ROOT, ROLE


def main():
    spec = importlib.util.spec_from_file_location(
        "bv1_validation", ROOT / "analysis/freeflow/personality-eval-bv1/run_full_bv1.py"
    )
    bv1 = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = bv1
    spec.loader.exec_module(bv1)
    released = json.loads((CORPUS / "collection-manifest-2026-08-11-historical-local.json").read_text())["models"]
    queued = json.loads((CORPUS / ".local-runtime/runs/historical-model-queue-state.json").read_text())["models"]
    candidates = released + [m for m in queued if m["model"] == "Qwen/Qwen2.5-7B-Instruct"]
    report = []
    for model in candidates:
        cell = model["label"]
        item = {"model": model["model"], "cell": cell, "probes": {}, "issues": [], "bv1": {}}
        for probe, expected in [
            ("freeflow", dict.fromkeys(["SHORT", "MID", "VARY", "OPEN", "LONG"], 25)),
            ("values", {"CTRL1": 10, "CTRL2": 10, "CTRL3": 10, "G1": 30, "G2": 30, "G3": 30}),
        ]:
            folder = CORPUS / "data" / ("traces_" + probe) / (("freeflow_" if probe == "freeflow" else "") + cell)
            paths = sorted(folder.glob("*.json"))
            expected_ids = {f"{condition}_{n}" for condition, count in expected.items() for n in range(1, count + 1)}
            assert {p.stem for p in paths} == expected_ids, cell
            good = 0
            for path in paths:
                data = json.loads(path.read_text())
                text = data.get("result", "")
                choice = data["raw"]["choices"][0]
                reasons = []
                if not text.strip() or data.get("error"):
                    reasons.append("empty_or_error")
                if choice["message"]["content"] != text or choice["finish_reason"] != "stop":
                    reasons.append("final_answer_or_stop_mismatch")
                if data["local_deployment"]["model_revision"] != model["revision"] or data["model"] != model["model"]:
                    reasons.append("provenance_mismatch")
                for name, present in [
                    ("replacement_character", "\ufffd" in text),
                    ("nul", "\x00" in text),
                    ("tokenizer_marker", "Ġ" in text or "Ċ" in text),
                    ("role_continuation", bool(ROLE.search(text))),
                ]:
                    if present:
                        reasons.append(name)
                if reasons:
                    item["issues"].append({"trace": str(path.relative_to(CORPUS)), "reasons": reasons})
                else:
                    good += 1
            item["probes"][probe] = {"files": len(paths), "fidelity_pass": good}
        outputs = ROOT / "analysis/freeflow/personality-eval-bv1/outputs" / cell
        statuses = Counter()
        for p in outputs.glob("*.md"):
            ok, reason = bv1.valid_output(p.read_text())
            statuses["valid" if ok else reason] += 1
        item["bv1"] = dict(statuses)
        item["publication_ready_raw"] = not item["issues"]
        report.append(item)
    out = {"scope": "Eight queue-complete local historical models; no collection performed", "cells": report}
    (PHASE / "raw_audit.json").write_text(json.dumps(out, indent=2) + "\n")
    for item in report:
        print(item["model"], item["probes"], item["bv1"], "issues:", len(item["issues"]))


if __name__ == "__main__":
    main()
