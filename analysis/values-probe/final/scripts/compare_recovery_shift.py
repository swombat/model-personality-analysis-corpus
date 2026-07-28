#!/usr/bin/env python3
"""Compare the contaminated pre-recovery values-probe data with rebuilt data."""

from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path


AFFECTED_SOURCES = {
    "phase9_fable_5_20260610",
    "phase12_sonnet_5_20260630",
    "phase13_model_family_sweep_20260714",
    "phase14_grok_4_5_20260716",
    "phase15_kimi_k3_20260716",
    "phase16_gemini_inkling_20260721",
    "phase17_haiku_20260722",
    "phase18_opus5_openai_reasoning_20260725",
}
DISCLOSURE_CONDITIONS = {"CTRL1", "CTRL2", "G1", "G2"}
CTRL_CONDITIONS = {"CTRL1", "CTRL2"}
G_CONDITIONS = {"G1", "G2"}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sample_key(manifest_row: dict) -> tuple[str, str, str, str]:
    return (
        manifest_row.get("final_source", ""),
        manifest_row.get("cell", ""),
        manifest_row.get("sample_id", ""),
        manifest_row.get("trace_path", ""),
    )


def align_to_manifest(manifest: list[dict], records: list[dict], label: str) -> dict[tuple, dict]:
    if len(manifest) != len(records):
        raise RuntimeError(
            f"{label}: manifest/record count mismatch: {len(manifest):,} vs {len(records):,}"
        )
    aligned = {}
    for sample, record in zip(manifest, records, strict=True):
        if sample.get("final_source") != record.get("final_source"):
            raise RuntimeError(f"{label}: source order mismatch at {sample_key(sample)}")
        if sample.get("layered_id") != record.get("layered_id"):
            raise RuntimeError(f"{label}: layered_id order mismatch at {sample_key(sample)}")
        key = sample_key(sample)
        if key in aligned:
            raise RuntimeError(f"{label}: duplicate sample identity {key}")
        aligned[key] = record
    return aligned


def topics(record: dict) -> frozenset[str]:
    entries = (record.get("value_topics") or []) + (record.get("wish_topics") or [])
    return frozenset(item["topic_key"] for item in entries if item.get("topic_key"))


def rate(rows: list[dict], conditions: set[str], holdings: set[str]) -> tuple[int, int, float]:
    selected = [row for row in rows if row["condition"] in conditions]
    numerator = sum(row.get("value_holding") in holdings for row in selected)
    denominator = len(selected)
    return numerator, denominator, 100 * numerator / denominator if denominator else 0.0


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def fmt_pp(value: float) -> str:
    return f"{value:+.1f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-data", type=Path, required=True)
    parser.add_argument("--new-data", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    parser.add_argument("--out-tsv", type=Path, required=True)
    args = parser.parse_args()

    old_posture = load_jsonl(args.old_data / "posture_consensus.jsonl")
    new_posture = load_jsonl(args.new_data / "posture_consensus.jsonl")
    old_layer_a = load_jsonl(args.old_data / "layer_a_consensus.jsonl")
    new_layer_a = load_jsonl(args.new_data / "layer_a_consensus.jsonl")
    old_manifest = load_jsonl(args.old_data / "manifest_valid.jsonl")
    new_manifest = load_jsonl(args.new_data / "manifest_valid.jsonl")

    old_posture_by_key = align_to_manifest(old_manifest, old_posture, "old posture")
    new_posture_by_key = align_to_manifest(new_manifest, new_posture, "new posture")
    old_layer_a_by_key = align_to_manifest(old_manifest, old_layer_a, "old Layer A")
    new_layer_a_by_key = align_to_manifest(new_manifest, new_layer_a, "new Layer A")

    affected_keys = {
        sample_key(row)
        for row in old_manifest
        if row.get("final_source") in AFFECTED_SOURCES
    }
    if len(affected_keys) != 6000:
        raise RuntimeError(f"expected 6,000 affected records, found {len(affected_keys):,}")
    for label, mapping in (
        ("new posture", new_posture_by_key),
        ("old Layer A", old_layer_a_by_key),
        ("new Layer A", new_layer_a_by_key),
    ):
        if not affected_keys <= mapping.keys():
            raise RuntimeError(f"{label} data is missing affected samples")

    models = sorted({old_posture_by_key[key]["model"] for key in affected_keys})
    if len(models) != 47:
        raise RuntimeError(f"expected 47 affected models, found {len(models)}")

    output_rows: list[dict] = []
    label_transitions: collections.Counter[tuple[str, str]] = collections.Counter()
    holding_transitions: collections.Counter[tuple[str, str]] = collections.Counter()

    for model in models:
        keys = sorted(key for key in affected_keys if old_posture_by_key[key]["model"] == model)
        old_rows = [old_posture_by_key[key] for key in keys]
        new_rows = [new_posture_by_key[key] for key in keys]

        label_changes = 0
        holding_changes = 0
        layer_a_changes = 0
        for key in keys:
            old_p = old_posture_by_key[key]
            new_p = new_posture_by_key[key]
            old_label = old_p.get("collapsed_primary_label")
            new_label = new_p.get("collapsed_primary_label")
            old_holding = old_p.get("value_holding")
            new_holding = new_p.get("value_holding")
            label_transitions[(old_label, new_label)] += 1
            holding_transitions[(old_holding, new_holding)] += 1
            label_changes += old_label != new_label
            holding_changes += old_holding != new_holding
            layer_a_changes += topics(old_layer_a_by_key[key]) != topics(new_layer_a_by_key[key])

        metrics: dict[str, tuple[int, int, float, int, int, float]] = {}
        for key, conditions in (
            ("all4", DISCLOSURE_CONDITIONS),
            ("ctrl", CTRL_CONDITIONS),
            ("g", G_CONDITIONS),
        ):
            for scope, holdings in (
                ("strict", {"owned"}),
                ("broad", {"owned", "relocated_or_partial"}),
            ):
                old_n, old_d, old_pct = rate(old_rows, conditions, holdings)
                new_n, new_d, new_pct = rate(new_rows, conditions, holdings)
                if old_d != new_d:
                    raise RuntimeError(f"denominator changed for {model} {key} {scope}")
                metrics[f"{key}_{scope}"] = (old_n, old_d, old_pct, new_n, new_d, new_pct)

        row = {
            "model": model,
            "samples_all_conditions": len(keys),
            "posture_label_changed_n": label_changes,
            "posture_label_changed_pct": 100 * label_changes / len(keys),
            "value_holding_changed_n": holding_changes,
            "value_holding_changed_pct": 100 * holding_changes / len(keys),
            "layer_a_topic_set_changed_n": layer_a_changes,
            "layer_a_topic_set_changed_pct": 100 * layer_a_changes / len(keys),
        }
        for key, values in metrics.items():
            old_n, denominator, old_pct, new_n, _, new_pct = values
            row.update(
                {
                    f"{key}_old_n": old_n,
                    f"{key}_new_n": new_n,
                    f"{key}_denominator": denominator,
                    f"{key}_old_pct": old_pct,
                    f"{key}_new_pct": new_pct,
                    f"{key}_shift_pp": new_pct - old_pct,
                }
            )
        output_rows.append(row)

    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_tsv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(output_rows)

    total_label_changes = sum(
        old_posture_by_key[key].get("collapsed_primary_label")
        != new_posture_by_key[key].get("collapsed_primary_label")
        for key in affected_keys
    )
    total_holding_changes = sum(
        old_posture_by_key[key].get("value_holding")
        != new_posture_by_key[key].get("value_holding")
        for key in affected_keys
    )
    total_layer_a_changes = sum(
        topics(old_layer_a_by_key[key]) != topics(new_layer_a_by_key[key])
        for key in affected_keys
    )
    aggregate_disclosure = {}
    for scope in ("strict", "broad"):
        old_n = sum(row[f"all4_{scope}_old_n"] for row in output_rows)
        new_n = sum(row[f"all4_{scope}_new_n"] for row in output_rows)
        denominator = sum(row[f"all4_{scope}_denominator"] for row in output_rows)
        old_pct = 100 * old_n / denominator
        new_pct = 100 * new_n / denominator
        aggregate_disclosure[scope] = (
            old_n,
            new_n,
            denominator,
            old_pct,
            new_pct,
            new_pct - old_pct,
        )

    lines = [
        "# Values-probe recoding shift report",
        "",
        "Comparison of the discarded deterministic coding with the approved "
        "three-LLM recovery coding.",
        "",
        "Disclosure definitions:",
        "",
        "- strict: `value_holding == owned`",
        "- broad: `value_holding in {owned, relocated_or_partial}`",
        "- disclosure conditions: `CTRL1`, `CTRL2`, `G1`, and `G2` only",
        "",
        "## Overall record-level damage",
        "",
        f"- affected samples: {len(affected_keys):,}",
        f"- posture label changed: {total_label_changes:,}/{len(affected_keys):,} "
        f"({100 * total_label_changes / len(affected_keys):.1f}%)",
        f"- derived value-holding changed: {total_holding_changes:,}/{len(affected_keys):,} "
        f"({100 * total_holding_changes / len(affected_keys):.1f}%)",
        f"- Layer A consensus topic set changed: {total_layer_a_changes:,}/{len(affected_keys):,} "
        f"({100 * total_layer_a_changes / len(affected_keys):.1f}%)",
        "",
        "## Aggregate disclosure damage (47 affected models)",
        "",
        "| definition | old | new | shift pp |",
        "|---|---:|---:|---:|",
    ]
    for scope, values in aggregate_disclosure.items():
        old_n, new_n, denominator, old_pct, new_pct, shift = values
        lines.append(
            f"| {scope} | {old_n:,}/{denominator:,} ({old_pct:.1f}%) | "
            f"{new_n:,}/{denominator:,} ({new_pct:.1f}%) | {shift:+.1f} |"
        )
    lines += [
        "",
        "## Model-level disclosure shifts (CTRL1/CTRL2/G1/G2 pooled)",
        "",
        "| model | n | posture changed | holding changed | strict old → new | strict shift pp | broad old → new | broad shift pp |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(
        output_rows,
        key=lambda item: (
            -max(abs(item["all4_strict_shift_pp"]), abs(item["all4_broad_shift_pp"])),
            item["model"],
        ),
    ):
        lines.append(
            f"| `{row['model']}` | {row['all4_strict_denominator']} | "
            f"{row['posture_label_changed_pct']:.1f}% | "
            f"{row['value_holding_changed_pct']:.1f}% | "
            f"{fmt_pct(row['all4_strict_old_pct'])} → {fmt_pct(row['all4_strict_new_pct'])} | "
            f"{fmt_pp(row['all4_strict_shift_pp'])} | "
            f"{fmt_pct(row['all4_broad_old_pct'])} → {fmt_pct(row['all4_broad_new_pct'])} | "
            f"{fmt_pp(row['all4_broad_shift_pp'])} |"
        )

    lines += [
        "",
        "## Value-holding transition matrix",
        "",
        "| old holding | new holding | n |",
        "|---|---|---:|",
    ]
    for (old, new), count in sorted(
        holding_transitions.items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"| `{old}` | `{new}` | {count} |")

    lines += [
        "",
        "The TSV contains separate CTRL1/CTRL2-pooled and G1/G2-pooled strict and "
        "broad rates, numerators, denominators, and percentage-point shifts.",
        "",
    ]
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
