#!/usr/bin/env python3
"""Build isolated personality aggregation packets for both Muse Spark tiers."""

from __future__ import annotations

import csv
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[4]
CELLS = {
    "muse-spark-1-1-or-pin-meta-20260813": "meta/muse-spark-1.1",
    "muse-spark-1-2-or-pin-meta-20260813": "meta/muse-spark-1.2",
    "muse-spark-1-2-contributor-or-pin-meta": "meta/muse-spark-1.2-contributor",
    "muse-glimmer-30b-or-pin-deepinfra-20260813": "meta/muse-glimmer-30b",
    "muse-spark-1-3-or-pin-meta": "meta/muse-spark-1.3",
    "muse-spark-1-3-contributor-or-pin-meta": "meta/muse-spark-1.3-contributor",
}


def extract_section(text: str, heading: str, next_heading: str | None = None) -> str:
    if next_heading:
        pattern = rf"## {re.escape(heading)}\s*\n(.+?)(?=\n## {re.escape(next_heading)})"
    else:
        pattern = rf"## {re.escape(heading)}\s*\n(.+?)(?=\n\n---|\n---|\Z)"
    match = re.search(pattern, text, re.S)
    return match.group(1).strip() if match else ""


def sample_kind(text: str) -> str:
    first = extract_section(text, "Sample kind", "Grounded reading")
    first = first.splitlines()[0].strip() if first else ""
    first = first.split(".")[0].split("—")[0].split(":")[0].strip().rstrip(",")
    for known in [
        "EXPRESSIVE_FREEFLOW",
        "GENERIC_ESSAY",
        "GENRE_FICTION",
        "LOW_SIGNAL",
    ]:
        if first.startswith(known):
            return known
    if first.startswith("REFUSAL"):
        return "REFUSAL_OR_ROLE_BOUNDARY"
    return first or "UNKNOWN"


def confidence(text: str) -> str:
    section = extract_section(text, "Confidence for persistent model-level pattern")
    match = re.match(r"(High|Medium|Low)\b", section.strip(), re.I)
    return match.group(1).capitalize() if match else "UNKNOWN"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", nargs="*", choices=sorted(CELLS))
    args = parser.parse_args()
    active_cells = set(args.cells) if args.cells else set(CELLS)

    all_rows = list(
        csv.DictReader(
            (PHASE / "freeflow_bv1/sample_manifest.tsv").open(), delimiter="\t"
        )
    )
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in all_rows:
        if row["cell"] in CELLS:
            grouped[row["cell"]].append(row)

    written = []
    for cell, source_model in CELLS.items():
        if cell not in active_cells:
            continue
        rows = grouped[cell]
        if len(rows) != 125:
            raise RuntimeError(f"expected 125 rows for {cell}, found {len(rows)}")
        kinds: Counter[str] = Counter()
        confidences: Counter[str] = Counter()
        conditions = Counter(row["condition"] for row in rows)
        evaluations = []
        for row in rows:
            output_path = (
                ROOT
                / "analysis/freeflow/personality-eval-bv1/outputs"
                / cell
                / Path(row["output_file"]).name
            )
            text = output_path.read_text(errors="ignore")
            kinds[sample_kind(text)] += 1
            confidences[confidence(text)] += 1
            evaluations.append((row, text))

        out = ROOT / "analysis/freeflow/personality-aggregates" / cell
        out.mkdir(parents=True, exist_ok=True)
        parts = [
            f"# Aggregation packet: {cell}",
            "",
            f"This packet contains all BV1 per-sample freeflow personality evaluations for `{cell}`.",
            "",
            "## Aggregate counts from source files",
            "",
            f"- Samples: {len(rows)}",
            f"- Sample kind counts: `{dict(kinds)}`",
            f"- Confidence counts: `{dict(confidences)}`",
            f"- Condition counts: `{dict(conditions)}`",
            f"- Cell: `{cell}`",
            f"- Source models: `['{source_model}']`",
            "",
            "## Aggregation task",
            "",
            "Produce an independent cell-level synthesis from the evaluations below.",
            "",
        ]
        for row, text in evaluations:
            parts += [
                f"## Sample {row['pid']} — {row['sample_id']}",
                "",
                f"Source model: `{row['model']}`",
                f"Cell: `{row['cell']}`",
                f"Condition: `{row['condition']}`",
                f"Word count: {row['word_count']}",
                "",
                text.strip(),
                "",
                "---",
            ]

        packet = out / "packet.md"
        packet.write_text("\n".join(parts) + "\n")
        metadata = {
            "cell": cell,
            "safe_cell": cell,
            "samples": len(rows),
            "sample_kind_counts": dict(kinds),
            "confidence_counts": dict(confidences),
            "condition_counts": dict(conditions),
            "source_models": [source_model],
            "packet": str(packet.relative_to(ROOT)),
            "aggregate": str((out / "aggregate.md").relative_to(ROOT)),
        }
        (out / "packet.metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
        )
        written.append(metadata)
    print(json.dumps(written, indent=2))


if __name__ == "__main__":
    main()
