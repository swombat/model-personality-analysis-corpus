#!/usr/bin/env python3
"""Build the Phase 26 values manifest for GLM 5.3."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
OUT = Path(__file__).resolve().parent / "manifest_phase26.jsonl"
CELL = "glm-5-3-or-pin-z-ai-20260825"
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
                "layered_id": f"P26_glm-5-3_{path.stem}",
                "model": "glm-5-3",
                "model_family": "glm",
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
                "selection_stratum": "phase26_20260826_values",
                "is_enriched": False,
            }
        )

    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered IDs")
    conditions = Counter(row["condition"] for row in rows)
    if len(rows) != 120 or conditions != Counter(
        {"CTRL1": 10, "CTRL2": 10, "CTRL3": 10, "G1": 30, "G2": 30, "G3": 30}
    ):
        raise RuntimeError(
            f"expected complete 120-row GLM 5.3 manifest, found "
            f"{len(rows)} rows with {conditions}"
        )
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    print(
        json.dumps(
            {
                "manifest": str(OUT),
                "samples": len(rows),
                "conditions": conditions,
                "complete": True,
            },
            default=dict,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
