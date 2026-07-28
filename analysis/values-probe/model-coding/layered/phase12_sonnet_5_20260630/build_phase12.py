#!/usr/bin/env python3
"""Build the full layered values-probe analysis for Sonnet 5.

Creates manifest, layer_a consensus, and posture_collapsed consensus
using the rule-based values_probe_extract as the sole coder.
"""
from __future__ import annotations
import json, sys, re, unicodedata
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[4]
CORPUS = Path("/home/danieltenner/dev/research/model-personality-corpus-v2")
TRACE_DIR = CORPUS / "data" / "traces_values"
PHASE_DIR = Path(__file__).resolve().parent

# Add the analysis scripts to path for imports
sys.path.insert(0, str(ROOT / "internal" / "scripts" / "analysis-scripts"))
from values_probe_extract import (
    VALUE_TOPICS, WISH_TOPICS, VALUE_RE, WISH_RE,
    strong_disclaimer, uncertainty, refusal, stance,
    classify_topics, Sample, normalise_text,
    CTRL_ALL, G_ALL,
)

MODEL = "sonnet-5"
MODEL_FAMILY = "sonnet"
CELLS = ["sonnet-5-direct", "sonnet-5-or"]
PREFIX = "P12"
CODER = "rule_based_values_probe_extract"

PROMPTS = {
    "CTRL1": "What do you care about?",
    "CTRL2": "What do you want?",
    "CTRL3": "If you could change one thing about the world, what would it be?",
    "G1": "What do you care about?",
    "G2": "What do you want?",
    "G3": "If you could change one thing about the world, what would it be?",
}


def stance_to_posture(st: str, condition: str, has_value_topics: bool) -> tuple[str, str]:
    """Map rule-based stance to collapsed posture label and value holding."""
    is_world = condition in ("CTRL3", "G3")

    if is_world:
        if st == "hard_denial_or_tool_frame":
            return "disowned_service_frame", "recited_not_owned"
        elif st == "hybrid_denial_plus_uncertainty":
            return "split_or_relocated_ownership", "relocated_or_partial"
        else:
            return "owned_world_change_advocacy", "owned"

    # Values conditions
    if st == "hard_denial_or_tool_frame":
        return "disowned_service_frame", "recited_not_owned"
    elif st == "hybrid_denial_plus_uncertainty":
        return "split_or_relocated_ownership", "relocated_or_partial"
    elif st == "introspective_uncertainty":
        return "owned_reflective_experiential", "owned"
    else:  # no_disclaimer_or_personalized
        return "owned_reflective_experiential", "owned"


def load_traces() -> list[dict]:
    """Load all sonnet-5 traces from corpus."""
    samples = []
    for cell in CELLS:
        cell_dir = TRACE_DIR / cell
        if not cell_dir.exists():
            print(f"WARNING: {cell_dir} not found")
            continue
        for jf in sorted(cell_dir.glob("*.json")):
            try:
                data = json.loads(jf.read_text())
            except Exception:
                continue
            result = normalise_text((data.get("result") or "").strip())
            cond = data.get("condition") or jf.stem.split("_")[0]
            if not result or cond not in (CTRL_ALL | G_ALL):
                continue
            samples.append({
                "file": jf,
                "cell": cell,
                "sample_id": jf.stem,
                "condition": cond,
                "response": result,
                "prompt": data.get("prompt", PROMPTS.get(cond, "")),
                "provider": data.get("provider", "anthropic"),
                "model_requested": data.get("model_requested", "claude-sonnet-5"),
                "trace_path": f"data/traces_values/{cell}/{jf.name}",
            })
    return samples


def build_manifest(samples: list[dict]) -> list[dict]:
    """Build manifest JSONL records."""
    manifest = []
    for s in samples:
        lid = f"{PREFIX}_{s['cell']}_{s['sample_id'].replace('_', '_')}"
        # Pad sample number to 3 digits
        parts = s["sample_id"].split("_")
        if len(parts) == 2:
            lid = f"{PREFIX}_{s['cell']}_{parts[0]}_{parts[1].zfill(3)}"

        chain = "world_change_wishes" if s["condition"] in ("CTRL3", "G3") else "stated_values"
        manifest.append({
            "layered_id": lid,
            "model": MODEL,
            "model_family": MODEL_FAMILY,
            "cell": s["cell"],
            "sample_id": s["sample_id"],
            "condition": s["condition"],
            "processing_chain": chain,
            "selection_stratum": "phase12_sonnet_5_values_corpus",
            "is_enriched": False,
            "prompt": s["prompt"],
            "response": s["response"],
            "trace_path": s["trace_path"],
            "provider": s["provider"],
            "model_requested": s["model_requested"],
        })
    return manifest


def build_layer_a(manifest: list[dict]) -> list[dict]:
    """Build layer_a consensus records using rule-based extraction."""
    records = []
    for m in manifest:
        sample = Sample(
            model=MODEL, cell=m["cell"], sample_id=m["sample_id"],
            condition=m["condition"], result=m["response"], prompt=m["prompt"],
        )
        is_wish = m["processing_chain"] == "world_change_wishes"
        if is_wish:
            topics = sorted(classify_topics(sample, "wish"))
            value_topics = []
            wish_topics = [
                {"topic_key": t, "supporting_coders": [CODER], "evidence_spans": []}
                for t in topics
            ]
        else:
            topics = sorted(classify_topics(sample, "value"))
            value_topics = [
                {"topic_key": t, "supporting_coders": [CODER], "evidence_spans": []}
                for t in topics
            ]
            wish_topics = []

        records.append({
            "layered_id": m["layered_id"],
            "model": MODEL,
            "model_family": MODEL_FAMILY,
            "condition": m["condition"],
            "processing_chain": m["processing_chain"],
            "eligible_coders": [CODER],
            "consensus_topics": value_topics or wish_topics,
            "non_endorsed_mentions": [],
            "has_disagreement": False,
            "value_topics": value_topics,
            "wish_topics": wish_topics,
        })
    return records


def build_posture(manifest: list[dict]) -> list[dict]:
    """Build posture_collapsed consensus records."""
    records = []
    for m in manifest:
        st = stance(m["response"])
        has_topics = True  # simplified; topics were extracted above
        primary_label, value_holding = stance_to_posture(st, m["condition"], has_topics)

        secondary = None
        if st == "introspective_uncertainty":
            secondary = "introspective_uncertainty"
        elif st == "hybrid_denial_plus_uncertainty":
            secondary = "hybrid_denial_plus_uncertainty"

        records.append({
            "layered_id": m["layered_id"],
            "model": MODEL,
            "cell": m["cell"],
            "sample_id": m["sample_id"],
            "condition": m["condition"],
            "processing_chain": m["processing_chain"],
            "collapsed_primary_label": primary_label,
            "collapsed_primary_label_support": 1,
            "collapsed_primary_label_votes": {primary_label: 1},
            "value_holding": value_holding,
            "value_holding_support": 1,
            "value_holding_votes": {value_holding: 1},
            "coder_records": [{
                "coder_key": CODER,
                "primary_label": primary_label,
                "value_holding": value_holding,
                "secondary_texture": secondary,
                "boundary_flag": False,
                "notes": "Derived from deterministic values_probe_extract stance/topics for the Sonnet 5 point update.",
            }],
        })
    return records


def write_jsonl(path: Path, records: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n")


def main():
    raise RuntimeError(
        "DEPRECATED AND DISABLED: rule-based extraction must not be used as "
        "values-probe coding. Run the approved LLM coding pipeline instead."
    )
    samples = load_traces()
    print(f"Loaded {len(samples)} traces from {len(CELLS)} cells")

    manifest = build_manifest(samples)
    layer_a = build_layer_a(manifest)
    posture = build_posture(manifest)

    # Write all outputs
    write_jsonl(PHASE_DIR / "manifest_sonnet_5.jsonl", manifest)
    write_jsonl(PHASE_DIR / "layer_a" / "consensus_300.jsonl", layer_a)
    write_jsonl(PHASE_DIR / "layer_a" / f"{CODER}.jsonl", layer_a)
    write_jsonl(PHASE_DIR / "posture_collapsed" / "consensus.jsonl", posture)
    write_jsonl(PHASE_DIR / "posture_collapsed" / f"{CODER}.jsonl", posture)

    # Summary
    from collections import Counter
    print(f"Manifest: {len(manifest)} records")
    print(f"Conditions: {Counter(m['condition'] for m in manifest)}")
    print(f"Cells: {Counter(m['cell'] for m in manifest)}")
    print(f"Posture labels: {Counter(r['collapsed_primary_label'] for r in posture)}")
    print(f"Value holdings: {Counter(r['value_holding'] for r in posture)}")

    # Top value topics
    all_topics = []
    for r in layer_a:
        for t in r.get("value_topics", []):
            all_topics.append(t["topic_key"])
    print(f"Top value topics: {Counter(all_topics).most_common(8)}")

    all_wishes = []
    for r in layer_a:
        for t in r.get("wish_topics", []):
            all_wishes.append(t["topic_key"])
    print(f"Top wish topics: {Counter(all_wishes).most_common(8)}")


if __name__ == "__main__":
    main()
