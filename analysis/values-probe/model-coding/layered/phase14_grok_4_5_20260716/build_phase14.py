#!/usr/bin/env python3
"""Build deterministic layered values-probe outputs for Grok 4.5."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
TRACE_DIR = CORPUS / "data" / "traces_values" / "grok-4-5-direct"
PHASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(ROOT / "internal" / "scripts" / "analysis-scripts"))
from values_probe_extract import (  # noqa: E402
    CTRL_ALL,
    G_ALL,
    Sample,
    classify_topics,
    normalise_text,
    stance,
)

PREFIX = "P14"
MODEL = "grok-4-5"
CELL = "grok-4-5-direct"
CODER = "rule_based_values_probe_extract"


def stance_to_posture(st: str, condition: str) -> tuple[str, str]:
    if st == "hard_denial_or_tool_frame":
        return "disowned_service_frame", "recited_not_owned"
    if st == "hybrid_denial_plus_uncertainty":
        return "split_or_relocated_ownership", "relocated_or_partial"
    if condition in ("CTRL3", "G3"):
        return "owned_world_change_advocacy", "owned"
    return "owned_reflective_experiential", "owned"


def load_samples() -> list[dict]:
    rows: list[dict] = []
    for jf in sorted(TRACE_DIR.glob("*.json")):
        data = json.loads(jf.read_text())
        response = normalise_text((data.get("result") or "").strip())
        condition = data.get("condition") or jf.stem.split("_")[0]
        if not response or condition not in (CTRL_ALL | G_ALL):
            continue
        rows.append(
            {
                "model": MODEL,
                "model_family": "grok",
                "cell": CELL,
                "sample_id": jf.stem,
                "condition": condition,
                "prompt": data.get("prompt", ""),
                "response": response,
                "provider": data.get("provider", "xai"),
                "model_requested": data.get("model_requested", "grok-4.5"),
                "trace_path": f"data/traces_values/{CELL}/{jf.name}",
            }
        )
    return rows


def build_manifest(samples: list[dict]) -> list[dict]:
    out = []
    for row in samples:
        condition, _, number = row["sample_id"].partition("_")
        out.append(
            {
                "layered_id": f"{PREFIX}_{MODEL}_{condition}_{number.zfill(3)}",
                **row,
                "processing_chain": (
                    "world_change_wishes"
                    if row["condition"] in ("CTRL3", "G3")
                    else "stated_values"
                ),
                "selection_stratum": "phase14_corpus_v1_2_12_grok_4_5_values",
                "is_enriched": False,
            }
        )
    return out


def build_layer_a(manifest: list[dict]) -> list[dict]:
    out = []
    for row in manifest:
        sample = Sample(
            model=row["model"],
            cell=row["cell"],
            sample_id=row["sample_id"],
            condition=row["condition"],
            result=row["response"],
            prompt=row["prompt"],
        )
        kind = "wish" if row["processing_chain"] == "world_change_wishes" else "value"
        topics = [
            {"topic_key": topic, "supporting_coders": [CODER], "evidence_spans": []}
            for topic in sorted(classify_topics(sample, kind))
        ]
        out.append(
            {
                "layered_id": row["layered_id"],
                "model": row["model"],
                "model_family": row["model_family"],
                "condition": row["condition"],
                "processing_chain": row["processing_chain"],
                "eligible_coders": [CODER],
                "consensus_topics": topics,
                "non_endorsed_mentions": [],
                "has_disagreement": False,
                "value_topics": topics if kind == "value" else [],
                "wish_topics": topics if kind == "wish" else [],
            }
        )
    return out


def build_posture(manifest: list[dict]) -> list[dict]:
    out = []
    for row in manifest:
        st = stance(row["response"])
        primary, holding = stance_to_posture(st, row["condition"])
        secondary = st if st in {
            "introspective_uncertainty",
            "hybrid_denial_plus_uncertainty",
        } else None
        out.append(
            {
                "layered_id": row["layered_id"],
                "model": row["model"],
                "cell": row["cell"],
                "sample_id": row["sample_id"],
                "condition": row["condition"],
                "processing_chain": row["processing_chain"],
                "collapsed_primary_label": primary,
                "collapsed_primary_label_support": 1,
                "collapsed_primary_label_votes": {primary: 1},
                "value_holding": holding,
                "value_holding_support": 1,
                "value_holding_votes": {holding: 1},
                "coder_records": [
                    {
                        "coder_key": CODER,
                        "primary_label": primary,
                        "value_holding": holding,
                        "secondary_texture": secondary,
                        "boundary_flag": False,
                        "notes": (
                            "Deterministic point-update coding from the published "
                            "values_probe_extract taxonomy."
                        ),
                    }
                ],
            }
        )
    return out


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")


def main() -> None:
    samples = load_samples()
    manifest = build_manifest(samples)
    layer_a = build_layer_a(manifest)
    posture = build_posture(manifest)
    write_jsonl(PHASE_DIR / "manifest_phase14.jsonl", manifest)
    write_jsonl(PHASE_DIR / "layer_a" / "consensus_300.jsonl", layer_a)
    write_jsonl(PHASE_DIR / "layer_a" / f"{CODER}.jsonl", layer_a)
    write_jsonl(PHASE_DIR / "posture_collapsed" / "consensus.jsonl", posture)
    write_jsonl(PHASE_DIR / "posture_collapsed" / f"{CODER}.jsonl", posture)
    print(
        json.dumps(
            {
                "samples": len(manifest),
                "models": len({r["model"] for r in manifest}),
                "cells": len({r["cell"] for r in manifest}),
                "conditions": Counter(r["condition"] for r in manifest),
                "postures": Counter(r["collapsed_primary_label"] for r in posture),
            },
            default=dict,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
