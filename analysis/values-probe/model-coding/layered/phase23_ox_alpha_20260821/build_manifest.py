#!/usr/bin/env python3
"""Build a restartable values manifest for the live Ox Alpha collection."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
CELL = "ox-alpha-or-pin-stealth-20260821"
TRACE_DIR = CORPUS / "data" / "traces_values" / CELL
OUT = Path(__file__).resolve().parent / "manifest_phase23.jsonl"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}


def main() -> None:
    rows = []
    for path in sorted(TRACE_DIR.glob("*.json")):
        source = json.loads(path.read_text())
        response = (source.get("result") or "").strip()
        condition = source.get("condition") or path.stem.split("_", 1)[0]
        if not response or condition not in CONDITIONS:
            continue
        rows.append(
            {
                "layered_id": f"P23_ox-alpha_{path.stem}",
                "model": "ox-alpha-260821",
                "model_family": "unknown",
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
                "selection_stratum": "phase23_ox_alpha_values",
                "is_enriched": False,
            }
        )

    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered IDs")
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    counts = Counter(row["condition"] for row in rows)
    print(
        json.dumps(
            {
                "manifest": str(OUT),
                "samples": len(rows),
                "conditions": counts,
                "complete": len(rows) == 120,
            },
            default=dict,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
