#!/usr/bin/env python3
"""Build the Phase 23 values manifest for the Qwen3.8 second replicates."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
TRACE_DIR = CORPUS / "data" / "traces_values"
PHASE_DIR = Path(__file__).resolve().parent
OUT = PHASE_DIR / "manifest_phase23.jsonl"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}

SPECS = {
    "qwen3-8-max-or-pin-alibaba-r2": (
        "qwen3-8-max",
        "qwen/qwen3.8-max",
    ),
    "qwen3-8-2-4t-a95b-or-pin-digitalocean-r2": (
        "qwen3-8-2-4t-a95b",
        "qwen/qwen3.8-2.4t-a95b",
    ),
}


def main() -> None:
    rows = []
    for cell, (model, requested) in SPECS.items():
        for path in sorted((TRACE_DIR / cell).glob("*.json")):
            source = json.loads(path.read_text())
            response = (source.get("result") or "").strip()
            condition = source.get("condition") or path.stem.split("_", 1)[0]
            if not response or condition not in CONDITIONS:
                continue
            rows.append(
                {
                    "layered_id": f"P23_{model}_r2_{path.stem}",
                    "model": model,
                    "model_family": "qwen",
                    "cell": cell,
                    "sample_id": f"r2_{path.stem}",
                    "condition": condition,
                    "prompt": source.get("prompt", ""),
                    "response": response,
                    "provider": source.get("provider", "openrouter"),
                    "model_requested": source.get("model_requested", requested),
                    "trace_path": f"data/traces_values/{cell}/{path.name}",
                    "processing_chain": (
                        "world_change_wishes"
                        if condition in {"CTRL3", "G3"}
                        else "stated_values"
                    ),
                    "selection_stratum": "phase23_qwen38_second_replicate",
                    "is_enriched": False,
                }
            )

    counts = Counter(row["model"] for row in rows)
    expected = {model: 120 for model, _ in SPECS.values()}
    if dict(counts) != expected:
        raise RuntimeError(
            f"refusing incomplete Phase 23 manifest: found {dict(counts)}, "
            f"expected {expected}"
        )
    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered_id values in Phase 23 manifest")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    print(
        json.dumps(
            {
                "manifest": str(OUT),
                "samples": len(rows),
                "models": counts,
                "conditions": Counter(row["condition"] for row in rows),
            },
            default=dict,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
