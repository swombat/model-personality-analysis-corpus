#!/usr/bin/env python3
"""Build the Phase 24 values manifest for Gemini 3.7 Flash."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
TRACE_DIR = CORPUS / "data" / "traces_values"
PHASE_DIR = Path(__file__).resolve().parent
OUT = PHASE_DIR / "manifest_phase24.jsonl"
CELL = "gemini-3-7-flash-or-pin-google"
MODEL = "gemini-3-7-flash"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}


def main() -> None:
    rows = []
    for path in sorted((TRACE_DIR / CELL).glob("*.json")):
        source = json.loads(path.read_text())
        response = (source.get("result") or "").strip()
        condition = source.get("condition") or path.stem.split("_", 1)[0]
        if not response or condition not in CONDITIONS:
            continue
        rows.append(
            {
                "layered_id": f"P24_{MODEL}_{path.stem}",
                "model": MODEL,
                "model_family": "google",
                "cell": CELL,
                "sample_id": path.stem,
                "condition": condition,
                "prompt": source.get("prompt", ""),
                "response": response,
                "provider": source.get("provider", "openrouter"),
                "model_requested": source.get(
                    "model_requested", "google/gemini-3.7-flash"
                ),
                "trace_path": f"data/traces_values/{CELL}/{path.name}",
                "processing_chain": (
                    "world_change_wishes"
                    if condition in {"CTRL3", "G3"}
                    else "stated_values"
                ),
                "selection_stratum": "phase24_gemini37_flash_values",
                "is_enriched": False,
            }
        )
    if len(rows) != 120:
        raise RuntimeError(f"refusing incomplete Phase 24 manifest: {len(rows)}/120")
    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered_id values in Phase 24 manifest")
    OUT.parent.mkdir(parents=True, exist_ok=True)
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
