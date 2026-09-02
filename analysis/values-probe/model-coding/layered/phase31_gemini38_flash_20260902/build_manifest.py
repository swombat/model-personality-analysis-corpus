#!/usr/bin/env python3
"""Build the Phase 31 values manifest for Gemini 3.8 Flash."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
PHASE = Path(__file__).resolve().parent
OUT = PHASE / "manifest_phase31.jsonl"
CELL = "gemini-3-8-flash-or-pin-google"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}


def main() -> None:
    rows = []
    trace_dir = CORPUS / "data" / "traces_values" / CELL
    for path in sorted(trace_dir.glob("*.json")):
        source = json.loads(path.read_text())
        response = (source.get("result") or "").strip()
        condition = source.get("condition") or path.stem.split("_", 1)[0]
        if not response or condition not in CONDITIONS:
            continue
        rows.append(
            {
                "layered_id": f"P31_gemini-3-8-flash_{path.stem}",
                "model": "gemini-3-8-flash",
                "model_family": "gemini",
                "cell": CELL,
                "sample_id": path.stem,
                "condition": condition,
                "prompt": source.get("prompt", ""),
                "response": response,
                "provider": source.get("provider", ""),
                "model_requested": source.get("model_requested")
                or source.get("model"),
                "trace_path": f"data/traces_values/{CELL}/{path.name}",
                "processing_chain": (
                    "world_change_wishes"
                    if condition in {"CTRL3", "G3"}
                    else "stated_values"
                ),
                "selection_stratum": "phase31_20260902_gemini_3_8_flash",
                "is_enriched": False,
            }
        )

    conditions = Counter(row["condition"] for row in rows)
    expected = Counter(
        {"CTRL1": 10, "CTRL2": 10, "CTRL3": 10, "G1": 30, "G2": 30, "G3": 30}
    )
    if len(rows) != 120 or conditions != expected:
        raise RuntimeError(f"incomplete manifest: {len(rows)} rows, {conditions}")

    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    print(json.dumps({"samples": len(rows), "conditions": conditions}, default=dict))


if __name__ == "__main__":
    main()

