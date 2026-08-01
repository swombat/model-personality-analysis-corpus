#!/usr/bin/env python3
"""Build the Phase 19 values manifest for the July 31 flash/small releases.

This script only packages source samples and provenance. It performs no topic
or posture classification; those are produced by the approved independent LLM
coder and consensus pipeline.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
TRACE_DIR = CORPUS / "data" / "traces_values"
PHASE_DIR = Path(__file__).resolve().parent
OUT = PHASE_DIR / "manifest_phase19.jsonl"

CELLS = {
    "deepseek-v4-flash-direct-20260731": {
        "model": "deepseek-v4-flash-0731",
        "model_family": "deepseek",
        "provider": "deepseek-direct",
        "model_requested": "deepseek-v4-flash",
    },
    "qwen3-7-flash-or-pin-alibaba": {
        "model": "qwen3-7-flash",
        "model_family": "qwen",
        "provider": "openrouter",
        "model_requested": "qwen/qwen3.7-flash",
    },
    "inkling-small-or-pin-deepinfra": {
        "model": "inkling-small",
        "model_family": "inkling",
        "provider": "openrouter",
        "model_requested": "thinkingmachines/inkling-small",
    },
}
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}


def load_rows() -> list[dict]:
    rows: list[dict] = []
    for cell, meta in CELLS.items():
        directory = TRACE_DIR / cell
        for path in sorted(directory.glob("*.json")):
            source = json.loads(path.read_text())
            response = (source.get("result") or "").strip()
            condition = source.get("condition") or path.stem.split("_", 1)[0]
            if not response or condition not in CONDITIONS:
                continue
            rows.append(
                {
                    "layered_id": f"P19_{meta['model']}_{path.stem}",
                    "model": meta["model"],
                    "model_family": meta["model_family"],
                    "cell": cell,
                    "sample_id": path.stem,
                    "condition": condition,
                    "prompt": source.get("prompt", ""),
                    "response": response,
                    "provider": source.get("provider", meta["provider"]),
                    "model_requested": source.get(
                        "model_requested", meta["model_requested"]
                    ),
                    "trace_path": f"data/traces_values/{cell}/{path.name}",
                    "processing_chain": (
                        "world_change_wishes"
                        if condition in {"CTRL3", "G3"}
                        else "stated_values"
                    ),
                    "selection_stratum": (
                        "phase19_corpus_july_31_flash_small_values"
                    ),
                    "is_enriched": False,
                }
            )
    return rows


def main() -> None:
    rows = load_rows()
    expected = len(CELLS) * 120
    if len(rows) != expected:
        raise RuntimeError(
            f"refusing incomplete Phase 19 manifest: {len(rows)}/{expected} samples"
        )
    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered_id values in Phase 19 manifest")
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    print(
        json.dumps(
            {
                "manifest": str(OUT),
                "samples": len(rows),
                "models": Counter(row["model"] for row in rows),
                "conditions": Counter(row["condition"] for row in rows),
            },
            default=dict,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
