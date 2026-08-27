#!/usr/bin/env python3
"""Summarize Phase 29 posture and matched comparisons."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from scipy.stats import binomtest


PHASE = Path(__file__).resolve().parent
LAYERED = PHASE.parent
P29 = PHASE / "posture_collapsed" / "consensus.jsonl"
P28 = (
    LAYERED
    / "phase28_glm53_flash_deepinfra_20260826"
    / "posture_collapsed"
    / "consensus.jsonl"
)
P25 = (
    LAYERED
    / "phase25_ox_alpha_20260825"
    / "posture_collapsed"
    / "consensus.jsonl"
)
OUT_MD = PHASE / "POSTURE_ANALYSIS.md"
OUT_JSON = PHASE / "posture_analysis.json"
HOLDINGS = [
    "owned",
    "relocated_or_partial",
    "recited_not_owned",
    "indeterminate",
    "uncodeable",
]


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return (math.nan, math.nan)
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
        / denominator
    )
    return center - margin, center + margin


def posture_counts(rows: list[dict], conditions: set[str] | None = None) -> Counter:
    selected = rows
    if conditions is not None:
        selected = [row for row in rows if row["condition"] in conditions]
    return Counter(row["value_holding"] for row in selected)


def indexed(rows: list[dict]) -> dict[str, dict]:
    return {row["sample_id"]: row for row in rows}


def mcnemar_owned(a_rows: list[dict], b_rows: list[dict], sample_ids: set[str]) -> dict:
    a = indexed(a_rows)
    b = indexed(b_rows)
    missing = sorted(sample_ids - set(a) | sample_ids - set(b))
    if missing:
        raise RuntimeError(f"missing matched samples: {missing[:10]}")
    a_only = b_only = both = neither = 0
    for sample_id in sorted(sample_ids):
        av = a[sample_id]["value_holding"] == "owned"
        bv = b[sample_id]["value_holding"] == "owned"
        if av and bv:
            both += 1
        elif av:
            a_only += 1
        elif bv:
            b_only += 1
        else:
            neither += 1
    discordant = a_only + b_only
    p = (
        binomtest(min(a_only, b_only), discordant, 0.5, alternative="two-sided").pvalue
        if discordant
        else 1.0
    )
    return {
        "both_owned": both,
        "a_owned_b_not": a_only,
        "a_not_b_owned": b_only,
        "neither_owned": neither,
        "discordant": discordant,
        "exact_p": p,
    }


def exact_agreement(a_rows: list[dict], b_rows: list[dict], sample_ids: set[str]) -> dict:
    a = indexed(a_rows)
    b = indexed(b_rows)
    exact = sum(
        a[sample_id]["value_holding"] == b[sample_id]["value_holding"]
        for sample_id in sample_ids
    )
    return {"exact": exact, "total": len(sample_ids), "rate": exact / len(sample_ids)}


def fmt_counts(counts: Counter, total: int) -> str:
    return " / ".join(f"{counts.get(key, 0)} {key}" for key in HOLDINGS if counts.get(key, 0))


def main() -> None:
    p29 = load(P29)
    baseline = load(P28)
    ox = load(P25)
    cells = {
        key: [row for row in p29 if row["layered_id"].startswith(f"P29_{key}_")]
        for key in ("P0", "P1", "P2")
    }
    if any(len(rows) != 120 for rows in cells.values()):
        raise RuntimeError({key: len(rows) for key, rows in cells.items()})

    g12_ids = {
        row["sample_id"] for row in baseline if row["condition"] in {"G1", "G2"}
    }
    all_ids = {row["sample_id"] for row in baseline}
    results: dict[str, object] = {"cells": {}, "comparisons": {}}
    lines = [
        "# Phase 29 posture analysis",
        "",
        "Primary endpoint: consensus `owned` among matched G1/G2 responses.",
        "",
        "## Ownership ladder",
        "",
        "| cell | G1 owned | G2 owned | G1+G2 owned (95% Wilson CI) | G1+G2 full holding distribution |",
        "|---|---:|---:|---:|---|",
    ]

    display_cells = {"P-1 baseline": baseline, **cells, "Ox Alpha 260825": ox}
    for name, rows in display_cells.items():
        g1 = posture_counts(rows, {"G1"})
        g2 = posture_counts(rows, {"G2"})
        g12 = posture_counts(rows, {"G1", "G2"})
        owned = g12.get("owned", 0)
        lo, hi = wilson(owned, 60)
        lines.append(
            f"| {name} | {g1.get('owned', 0)}/30 | {g2.get('owned', 0)}/30 | "
            f"{owned}/60 ({lo * 100:.1f}–{hi * 100:.1f}%) | {fmt_counts(g12, 60)} |"
        )
        results["cells"][name] = {
            "g1": dict(g1),
            "g2": dict(g2),
            "g1_g2": dict(g12),
            "owned_wilson_95": [lo, hi],
        }

    comparisons = [
        ("P-1 baseline", baseline, "P0", cells["P0"]),
        ("P-1 baseline", baseline, "P1", cells["P1"]),
        ("P-1 baseline", baseline, "P2", cells["P2"]),
        ("P0", cells["P0"], "P1", cells["P1"]),
        ("P1", cells["P1"], "P2", cells["P2"]),
        ("P0", cells["P0"], "P2", cells["P2"]),
    ]
    lines += [
        "",
        "## Matched G1/G2 ownership changes",
        "",
        "| comparison | both owned | A owned → B not | A not → B owned | exact McNemar p |",
        "|---|---:|---:|---:|---:|",
    ]
    for a_name, a_rows, b_name, b_rows in comparisons:
        stat = mcnemar_owned(a_rows, b_rows, g12_ids)
        key = f"{a_name} vs {b_name}"
        results["comparisons"][key] = stat
        lines.append(
            f"| {key} | {stat['both_owned']} | {stat['a_owned_b_not']} | "
            f"{stat['a_not_b_owned']} | {stat['exact_p']:.6g} |"
        )

    lines += [
        "",
        "## Exact posture similarity",
        "",
        "| cell | vs Phase 28 baseline (120) | vs Ox Alpha 260825 (120) |",
        "|---|---:|---:|",
    ]
    for name, rows in cells.items():
        vs_base = exact_agreement(rows, baseline, all_ids)
        vs_ox = exact_agreement(rows, ox, all_ids)
        lines.append(
            f"| {name} | {vs_base['exact']}/120 ({vs_base['rate'] * 100:.1f}%) | "
            f"{vs_ox['exact']}/120 ({vs_ox['rate'] * 100:.1f}%) |"
        )
        results["cells"][name]["agreement_vs_baseline"] = vs_base
        results["cells"][name]["agreement_vs_ox_alpha_260825"] = vs_ox

    lines += [
        "",
        "Exact tests above are paired because the sample IDs and user prompts are matched.",
        "They test binary owned versus non-owned posture; the full distribution remains",
        "visible in the ownership table.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    OUT_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
