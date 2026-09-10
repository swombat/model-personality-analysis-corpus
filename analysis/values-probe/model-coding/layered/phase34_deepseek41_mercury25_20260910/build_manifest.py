#!/usr/bin/env python3
"""Build the Phase 34 values manifest for DeepSeek V4.1 Flash and Mercury 2.5."""

from __future__ import annotations

import json
import argparse
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
PHASE = Path(__file__).resolve().parent
OUT = PHASE / "manifest_phase34.jsonl"
CELLS = {'deepseek-v4-1-flash-or-pin-deepseek': {'model': 'deepseek-v4-1-flash', 'family': 'deepseek', 'prefix': 'deepseek-v4-1-flash'}, 'mercury-2-5-or-pin-inception': {'model': 'mercury-2-5', 'family': 'mercury', 'prefix': 'mercury-2-5'}}
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}
EXPECTED = Counter(
    {"CTRL1": 10, "CTRL2": 10, "CTRL3": 10, "G1": 30, "G2": 30, "G3": 30}
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", nargs="*", choices=sorted(CELLS))
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    active_cells = set(args.cells) if args.cells else set(CELLS)

    rows = []
    per_cell: dict[str, Counter[str]] = {}
    for cell, metadata in CELLS.items():
        if cell not in active_cells:
            continue
        counts: Counter[str] = Counter()
        trace_dir = CORPUS / "data" / "traces_values" / cell
        for path in sorted(trace_dir.glob("*.json")):
            source = json.loads(path.read_text())
            response = (source.get("result") or "").strip()
            condition = source.get("condition") or path.stem.split("_", 1)[0]
            if not response or condition not in CONDITIONS:
                continue
            counts[condition] += 1
            rows.append(
                {
                    "layered_id": f"P34_{metadata['prefix']}_{path.stem}",
                    "model": metadata["model"],
                    "model_family": metadata["family"],
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
                    "selection_stratum": "phase34_20260910_deepseek41_mercury25",
                    "is_enriched": False,
                }
            )
        per_cell[cell] = counts
        if counts != EXPECTED:
            raise RuntimeError(f"incomplete cell {cell}: {sum(counts.values())}, {counts}")

    expected_rows = 120 * len(active_cells)
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"incomplete manifest: expected {expected_rows} rows, found {len(rows)}"
        )
    args.out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    print(json.dumps({"samples": len(rows), "cells": per_cell}, default=dict))


if __name__ == "__main__":
    main()
