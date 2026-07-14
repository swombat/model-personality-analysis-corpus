#!/usr/bin/env python3
"""Build layered values-probe outputs for the Corpus V2 v1.2.11 sweep.

This follows the deterministic point-update convention used for Sonnet 5:
the inspectable values-probe extractor is the sole coder, and the generated
records retain that provenance rather than pretending to be three-model
consensus.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
TRACE_DIR = CORPUS / "data" / "traces_values"
MANIFEST_PATH = CORPUS / "collection-manifest-2026-07-14.json"
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

PREFIX = "P13"
CODER = "rule_based_values_probe_extract"


def model_family(label: str) -> str:
    if label.startswith("gpt-"):
        return "gpt"
    if label.startswith("grok-"):
        return "grok"
    if label.startswith("llama-"):
        return "llama"
    return "mistral"


def stance_to_posture(st: str, condition: str) -> tuple[str, str]:
    if st == "hard_denial_or_tool_frame":
        return "disowned_service_frame", "recited_not_owned"
    if st == "hybrid_denial_plus_uncertainty":
        return "split_or_relocated_ownership", "relocated_or_partial"
    if condition in ("CTRL3", "G3"):
        return "owned_world_change_advocacy", "owned"
    return "owned_reflective_experiential", "owned"


def load_samples() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    rows: list[dict] = []
    for item in manifest["models"]:
        cell = item["label"]
        model = re.sub(r"-(?:direct|or-pin-.+)$", "", cell)
        cell_dir = TRACE_DIR / cell
        for jf in sorted(cell_dir.glob("*.json")):
            data = json.loads(jf.read_text())
            response = normalise_text((data.get("result") or "").strip())
            condition = data.get("condition") or jf.stem.split("_")[0]
            if not response or condition not in (CTRL_ALL | G_ALL):
                continue
            rows.append(
                {
                    "model": model,
                    "model_family": model_family(model),
                    "cell": cell,
                    "sample_id": jf.stem,
                    "condition": condition,
                    "prompt": data.get("prompt", ""),
                    "response": response,
                    "provider": data.get("provider", item["provider"]),
                    "model_requested": data.get("model_requested", item["model"]),
                    "trace_path": f"data/traces_values/{model}/{jf.name}",
                }
            )
    return rows


def build_manifest(samples: list[dict]) -> list[dict]:
    out = []
    for row in samples:
        condition, _, number = row["sample_id"].partition("_")
        layered_id = f"{PREFIX}_{row['model']}_{condition}_{number.zfill(3)}"
        out.append(
            {
                "layered_id": layered_id,
                **row,
                "processing_chain": (
                    "world_change_wishes"
                    if row["condition"] in ("CTRL3", "G3")
                    else "stated_values"
                ),
                "selection_stratum": "phase13_corpus_v1_2_11_full_values",
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
        values = topics if kind == "value" else []
        wishes = topics if kind == "wish" else []
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
                "value_topics": values,
                "wish_topics": wishes,
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
    write_jsonl(PHASE_DIR / "manifest_phase13.jsonl", manifest)
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
