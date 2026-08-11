#!/usr/bin/env python3
"""Build the Phase 21 values manifest for historical local checkpoints.

This packages source samples and provenance only. Topic and posture coding are
produced by the approved independent three-LLM consensus pipeline.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
TRACE_DIR = CORPUS / "data" / "traces_values"
PHASE_DIR = Path(__file__).resolve().parent
OUT = PHASE_DIR / "manifest_phase21.jsonl"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}

CELLS = [
    {
        "cell": "yi-6b-chat-local-transformers-bf16-r2dbf63b",
        "model": "yi-6b-chat",
        "model_family": "yi",
        "model_requested": "01-ai/Yi-6B-Chat",
    },
    {
        "cell": "chatglm2-6b-local-transformers427-mps-fp16-rd2e2d91",
        "model": "chatglm2-6b",
        "model_family": "glm",
        "model_requested": "zai-org/chatglm2-6b",
    },
]


def load_rows() -> list[dict]:
    rows: list[dict] = []
    for spec in CELLS:
        cell = spec["cell"]
        model = spec["model"]
        for path in sorted((TRACE_DIR / cell).glob("*.json")):
            source = json.loads(path.read_text())
            response = (source.get("result") or "").strip()
            condition = source.get("condition") or path.stem.split("_", 1)[0]
            if not response or condition not in CONDITIONS:
                continue
            rows.append(
                {
                    "layered_id": f"P21_{model}_{path.stem}",
                    "model": model,
                    "model_family": spec["model_family"],
                    "cell": cell,
                    "sample_id": path.stem,
                    "condition": condition,
                    "prompt": source.get("prompt", ""),
                    "response": response,
                    "provider": source.get("provider", "local-openai"),
                    "model_requested": source.get(
                        "model_requested", spec["model_requested"]
                    ),
                    "trace_path": f"data/traces_values/{cell}/{path.name}",
                    "processing_chain": (
                        "world_change_wishes"
                        if condition in {"CTRL3", "G3"}
                        else "stated_values"
                    ),
                    "selection_stratum": "phase21_historical_local_values",
                    "is_enriched": False,
                    "local_deployment": source.get("local_deployment"),
                }
            )
    return rows


def main() -> None:
    rows = load_rows()
    if len(rows) != 240:
        raise RuntimeError(
            f"refusing incomplete Phase 21 manifest: {len(rows)}/240 samples"
        )
    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered_id values in Phase 21 manifest")
    counts = Counter(row["model"] for row in rows)
    if counts != {"yi-6b-chat": 120, "chatglm2-6b": 120}:
        raise RuntimeError(f"unexpected per-model coverage: {dict(counts)}")
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
