#!/usr/bin/env python3
"""Build the Phase 25 values manifest for two complete dated cells."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
OUT = Path(__file__).resolve().parent / "manifest_phase25.jsonl"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}
CELLS = {
    "ox-alpha-260825-or-pin-stealth": {
        "model": "ox-alpha-260825",
        "family": "unknown",
        "prefix": "ox-alpha-260825",
    },
    "glm-5-3-or-pin-z-ai-20260825": {
        "model": "glm-5-3",
        "family": "glm",
        "prefix": "glm-5-3",
    },
}


def main() -> None:
    rows = []
    for cell, identity in CELLS.items():
        trace_dir = CORPUS / "data" / "traces_values" / cell
        for path in sorted(trace_dir.glob("*.json")):
            source = json.loads(path.read_text())
            response = (source.get("result") or "").strip()
            condition = source.get("condition") or path.stem.split("_", 1)[0]
            if not response or condition not in CONDITIONS:
                continue
            rows.append(
                {
                    "layered_id": f"P25_{identity['prefix']}_{path.stem}",
                    "model": identity["model"],
                    "model_family": identity["family"],
                    "cell": cell,
                    "sample_id": path.stem,
                    "condition": condition,
                    "prompt": source.get("prompt", ""),
                    "response": response,
                    "provider": source.get("provider", ""),
                    "model_requested": source.get("model_requested")
                    or source.get("model"),
                    "trace_path": f"data/traces_values/{cell}/{path.name}",
                    "processing_chain": (
                        "world_change_wishes"
                        if condition in {"CTRL3", "G3"}
                        else "stated_values"
                    ),
                    "selection_stratum": "phase25_20260825_values",
                    "is_enriched": False,
                }
            )

    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered IDs")
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    cells = Counter(row["cell"] for row in rows)
    conditions = Counter(row["condition"] for row in rows)
    complete = len(rows) == 240 and all(n == 120 for n in cells.values())
    print(
        json.dumps(
            {
                "manifest": str(OUT),
                "samples": len(rows),
                "cells": cells,
                "conditions": conditions,
                "complete": complete,
            },
            default=dict,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
