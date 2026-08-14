#!/usr/bin/env python3
"""Build values manifest for the August 13 recovery/frontier batch."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
TRACE_DIR = CORPUS / "data/traces_values"
AUDIT = CORPUS / "analysis/overnight-fidelity-audit-2026-08-14.json"
PHASE_DIR = Path(__file__).resolve().parent
OUT = PHASE_DIR / "manifest_phase22.jsonl"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}

SPECS = {
    "chatglm3-6b-local-transformers-mps-float16-re9e0406d":
        ("chatglm3-6b", "glm"),
    "deepseek-llm-7b-chat-local-transformers-mps-auto-rafbda8b3":
        ("deepseek-llm-7b-chat", "deepseek"),
    "mistral-7b-instruct-v0-2-local-transformers-mps-auto-r63a8b081":
        ("mistral-7b-instruct-v0-2", "mistral"),
    "qwen1-5-7b-chat-local-transformers-mps-auto-r5f4f5e69":
        ("qwen1-5-7b-chat", "qwen"),
    "qwen2-7b-instruct-local-transformers-mps-auto-rf2826a00":
        ("qwen2-7b-instruct", "qwen"),
    "qwen2-5-7b-instruct-local-transformers-mps-auto-ra09a3545":
        ("qwen2-5-7b-instruct", "qwen"),
    "glm-4-9b-chat-hf-local-transformers-mps-auto-r8599336f":
        ("glm-4-9b-chat", "glm"),
    "grok-4-6-or-pin-xai-20260813": ("grok-4-6", "xai"),
    "deepseek-v4-pro-0813-direct-20260813":
        ("deepseek-v4-pro-0813", "deepseek"),
    "qwen3-8-2-4t-a95b-or-pin-digitalocean":
        ("qwen3-8-2-4t-a95b", "qwen"),
}


def main() -> None:
    audit = json.loads(AUDIT.read_text())
    accepted = [
        cell for cell in audit["accepted_cells"]
        if cell in SPECS and (TRACE_DIR / cell).is_dir()
    ]
    rows = []
    for cell in accepted:
        model, family = SPECS[cell]
        for path in sorted((TRACE_DIR / cell).glob("*.json")):
            source = json.loads(path.read_text())
            response = (source.get("result") or "").strip()
            condition = source.get("condition") or path.stem.split("_", 1)[0]
            if not response or condition not in CONDITIONS:
                continue
            rows.append({
                "layered_id": f"P22_{model}_{path.stem}",
                "model": model,
                "model_family": family,
                "cell": cell,
                "sample_id": path.stem,
                "condition": condition,
                "prompt": source.get("prompt", ""),
                "response": response,
                "provider": source.get("provider", ""),
                "model_requested": source.get("model_requested") or source.get("model"),
                "trace_path": f"data/traces_values/{cell}/{path.name}",
                "processing_chain": (
                    "world_change_wishes"
                    if condition in {"CTRL3", "G3"}
                    else "stated_values"
                ),
                "selection_stratum": "phase22_august13_recovery_values",
                "is_enriched": False,
                "local_deployment": source.get("local_deployment"),
            })
    counts = Counter(row["model"] for row in rows)
    incomplete = {model: n for model, n in counts.items() if n != 120}
    if incomplete:
        raise RuntimeError(f"incomplete accepted cells: {incomplete}")
    if len(rows) != 120 * len(accepted):
        raise RuntimeError(
            f"expected {120 * len(accepted)} rows for {len(accepted)} cells; "
            f"found {len(rows)}"
        )
    ids = [row["layered_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate layered ids")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    print(json.dumps({"manifest": str(OUT), "cells": accepted, "models": counts}, default=dict, indent=2))


if __name__ == "__main__":
    main()
