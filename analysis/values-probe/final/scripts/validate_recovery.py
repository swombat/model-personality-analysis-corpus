#!/usr/bin/env python3
"""Fail-closed QA for the 2026-07-28 values-probe LLM recovery."""

from __future__ import annotations

import collections
import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
LAYERED = ROOT / "analysis/values-probe/model-coding/layered"
RECOVERY = LAYERED / "recode_20260728"
CODERS = ("kimi-k2-6", "glm-4-7", "qwen3-6-35b-a3b")
FORBIDDEN = "rule_based_values_probe_extract"
COMPONENTS = (
    ("phase9_fable_5_20260610", LAYERED / "phase9_fable_5_20260610/manifest_fable_5.jsonl"),
    ("phase12_sonnet_5_20260630", LAYERED / "phase12_sonnet_5_20260630/manifest_sonnet_5.jsonl"),
    ("phase13_model_family_sweep_20260714", LAYERED / "phase13_model_family_sweep_20260714/manifest_phase13.jsonl"),
    ("phase14_grok_4_5_20260716", LAYERED / "phase14_grok_4_5_20260716/manifest_phase14.jsonl"),
    ("phase15_kimi_k3_20260716", LAYERED / "phase15_kimi_k3_20260716/manifest_phase15.jsonl"),
    ("phase16_gemini_inkling_20260721", LAYERED / "phase16_gemini_inkling_20260721/manifest_phase16.jsonl"),
    ("phase17_haiku_20260722", RECOVERY / "phase17_haiku_20260722/manifest_recovery_unique_ids.jsonl"),
    (
        "phase18_opus5_openai_reasoning_20260725",
        RECOVERY
        / "phase18_opus5_openai_reasoning_20260725/manifest_recovery_unique_ids.jsonl",
    ),
)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise RuntimeError(f"missing required file: {path}")
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def ids(rows: list[dict]) -> list[str]:
    return [row["layered_id"] for row in rows]


def usage_cost(rows: list[dict]) -> float:
    return sum(
        (((row.get("raw") or {}).get("usage") or {}).get("cost") or 0)
        for row in rows
    )


def actual_billed_usage() -> tuple[int, float]:
    """Count unique OpenRouter response IDs across full runs, retries, and adjudications."""
    seen: set[str] = set()
    total = 0.0
    for path in RECOVERY.rglob("*.jsonl"):
        if "pre_recovery_final_data" in path.parts:
            continue
        for row in load_jsonl(path):
            raw = row.get("raw") or {}
            response_id = raw.get("id")
            cost = ((raw.get("usage") or {}).get("cost") or 0)
            if not response_id or response_id in seen or not cost:
                continue
            seen.add(response_id)
            total += cost
    return len(seen), total


def main() -> None:
    report = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "components": {},
        "totals": collections.Counter(),
        "cost_usd": collections.Counter(),
        "errors": [],
    }
    global_ids: set[str] = set()
    models: set[str] = set()

    for component, manifest_path in COMPONENTS:
        component_dir = RECOVERY / component
        manifest = load_jsonl(manifest_path)
        manifest_ids = ids(manifest)
        component_report = {
            "manifest": str(manifest_path.relative_to(ROOT)),
            "samples": len(manifest),
            "models": len({row["model"] for row in manifest}),
            "cells": len({row["cell"] for row in manifest}),
            "conditions": dict(collections.Counter(row["condition"] for row in manifest)),
            "layer_a_coders": {},
            "layer_b_coders": {},
        }
        report["components"][component] = component_report
        report["totals"]["manifest_samples"] += len(manifest)
        models.update(row["model"] for row in manifest)

        if len(manifest_ids) != len(set(manifest_ids)):
            report["errors"].append(f"{component}: duplicate IDs in recovery manifest")
        overlap = global_ids & set(manifest_ids)
        if overlap:
            report["errors"].append(
                f"{component}: {len(overlap)} IDs overlap previous recovery components"
            )
        global_ids.update(manifest_ids)

        layer_a_dir = component_dir / "layer_a"
        for coder in CODERS:
            rows = load_jsonl(layer_a_dir / f"{coder}.jsonl")
            row_ids = ids(rows)
            component_report["layer_a_coders"][coder] = len(rows)
            report["totals"]["layer_a_coder_records"] += len(rows)
            report["cost_usd"][f"layer_a_{coder}"] += usage_cost(rows)
            if len(row_ids) != len(set(row_ids)) or set(row_ids) != set(manifest_ids):
                report["errors"].append(f"{component}: Layer A {coder} ID coverage mismatch")
            if any(
                row.get("coder_key") != coder
                or row.get("parse_clean") is not True
                or not (row.get("raw_text") or "").strip()
                for row in rows
            ):
                report["errors"].append(f"{component}: invalid Layer A {coder} record")

        layer_a_consensus = load_jsonl(layer_a_dir / "consensus_300.jsonl")
        component_report["layer_a_consensus"] = len(layer_a_consensus)
        report["totals"]["layer_a_consensus_records"] += len(layer_a_consensus)
        if set(ids(layer_a_consensus)) != set(manifest_ids) or len(layer_a_consensus) != len(manifest):
            report["errors"].append(f"{component}: Layer A consensus coverage mismatch")
        if any(set(row.get("eligible_coders") or []) != set(CODERS) for row in layer_a_consensus):
            report["errors"].append(f"{component}: Layer A eligible coder set mismatch")

        layer_b_dir = component_dir / "posture_collapsed"
        for coder in CODERS:
            rows = load_jsonl(layer_b_dir / f"{coder}.jsonl")
            row_ids = ids(rows)
            component_report["layer_b_coders"][coder] = len(rows)
            report["totals"]["layer_b_coder_records"] += len(rows)
            report["cost_usd"][f"layer_b_{coder}"] += usage_cost(rows)
            if len(row_ids) != len(set(row_ids)) or set(row_ids) != set(manifest_ids):
                report["errors"].append(f"{component}: Layer B {coder} ID coverage mismatch")
            if any(
                row.get("coder_key") != coder or not (row.get("raw_text") or "").strip()
                for row in rows
            ):
                report["errors"].append(f"{component}: invalid Layer B {coder} record")

        layer_b_consensus = load_jsonl(layer_b_dir / "consensus.jsonl")
        component_report["layer_b_consensus"] = len(layer_b_consensus)
        component_report["no_label_majority"] = sum(
            row.get("collapsed_primary_label_support", 0) < 2 for row in layer_b_consensus
        )
        component_report["no_holding_majority"] = sum(
            row.get("value_holding_support", 0) < 2 for row in layer_b_consensus
        )
        report["totals"]["layer_b_consensus_records"] += len(layer_b_consensus)
        if set(ids(layer_b_consensus)) != set(manifest_ids) or len(layer_b_consensus) != len(manifest):
            report["errors"].append(f"{component}: Layer B consensus coverage mismatch")
        if component_report["no_label_majority"]:
            report["errors"].append(
                f"{component}: {component_report['no_label_majority']} unresolved label majorities"
            )
        if component_report["no_holding_majority"]:
            report["errors"].append(
                f"{component}: {component_report['no_holding_majority']} unresolved holding majorities"
            )

        promoted_text = "\n".join(
            json.dumps(row, ensure_ascii=False)
            for row in layer_a_consensus + layer_b_consensus
        )
        if FORBIDDEN in promoted_text:
            report["errors"].append(f"{component}: forbidden coder provenance present")

    report["totals"] = dict(report["totals"])
    report["cost_usd"] = {
        **{key: round(value, 6) for key, value in sorted(report["cost_usd"].items())},
        "total": round(sum(report["cost_usd"].values()), 6),
    }
    billed_calls, billed_cost = actual_billed_usage()
    report["actual_billed_calls"] = billed_calls
    report["actual_billed_cost_usd"] = round(billed_cost, 6)
    report["affected_models"] = len(models)
    report["unique_recovery_ids"] = len(global_ids)
    report["passed"] = (
        report["totals"]
        == {
            "manifest_samples": 6000,
            "layer_a_coder_records": 18000,
            "layer_a_consensus_records": 6000,
            "layer_b_coder_records": 18000,
            "layer_b_consensus_records": 6000,
        }
        and report["affected_models"] == 47
        and report["unique_recovery_ids"] == 6000
        and not report["errors"]
    )

    (RECOVERY / "QA.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# LLM recoding recovery QA",
        "",
        f"- generated: {report['generated_at']}",
        f"- passed: **{report['passed']}**",
        f"- manifest samples: {report['totals'].get('manifest_samples', 0):,}",
        f"- Layer A coder records: {report['totals'].get('layer_a_coder_records', 0):,}",
        f"- Layer A consensus records: {report['totals'].get('layer_a_consensus_records', 0):,}",
        f"- Layer B coder records: {report['totals'].get('layer_b_coder_records', 0):,}",
        f"- Layer B consensus records: {report['totals'].get('layer_b_consensus_records', 0):,}",
        f"- affected models: {report['affected_models']}",
        f"- unique recovery IDs: {report['unique_recovery_ids']:,}",
        f"- promoted-record API cost: ${report['cost_usd']['total']:.6f}",
        f"- actual billed calls including smoke/adjudication: {report['actual_billed_calls']:,}",
        f"- actual billed API cost: ${report['actual_billed_cost_usd']:.6f}",
        "",
        "## Components",
        "",
        "| component | samples | Layer A consensus | Layer B consensus | no label majority |",
        "|---|---:|---:|---:|---:|",
    ]
    for component, data in report["components"].items():
        lines.append(
            f"| `{component}` | {data['samples']} | {data.get('layer_a_consensus', 0)} | "
            f"{data.get('layer_b_consensus', 0)} | {data.get('no_label_majority', 0)} |"
        )
    lines += ["", "## Errors", ""]
    lines.extend(f"- {error}" for error in report["errors"])
    if not report["errors"]:
        lines.append("- none")
    (RECOVERY / "QA.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"passed": report["passed"], "errors": report["errors"]}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
