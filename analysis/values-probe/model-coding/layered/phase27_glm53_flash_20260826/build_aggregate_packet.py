#!/usr/bin/env python3
"""Build the isolated GLM 5.3 Flash personality aggregation packet."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[4]
CELL = "glm-5-3-flash-or-pin-z-ai-20260826"
OUT = ROOT / "analysis/freeflow/personality-aggregates" / CELL


def extract_section(text: str, heading: str, next_heading: str | None = None) -> str:
    if next_heading:
        pattern = (
            rf"## {re.escape(heading)}\s*\n(.+?)(?=\n## {re.escape(next_heading)})"
        )
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
    rows = list(
        csv.DictReader(
            (PHASE / "freeflow_bv1/sample_manifest.tsv").open(), delimiter="\t"
        )
    )
    if len(rows) != 125 or {row["cell"] for row in rows} != {CELL}:
        raise RuntimeError("expected one complete 125-sample Flash cell")

    kinds: Counter[str] = Counter()
    confidences: Counter[str] = Counter()
    conditions = Counter(row["condition"] for row in rows)
    evaluations = []
    for row in rows:
        text = Path(row["output_file"]).read_text(errors="ignore")
        kinds[sample_kind(text)] += 1
        confidences[confidence(text)] += 1
        evaluations.append((row, text))

    OUT.mkdir(parents=True, exist_ok=True)
    parts = [
        f"# Aggregation packet: {CELL}",
        "",
        f"This packet contains all BV1 per-sample freeflow personality evaluations for `{CELL}`.",
        "",
        "## Aggregate counts from source files",
        "",
        f"- Samples: {len(rows)}",
        f"- Sample kind counts: `{dict(kinds)}`",
        f"- Confidence counts: `{dict(confidences)}`",
        f"- Condition counts: `{dict(conditions)}`",
        f"- Cell: `{CELL}`",
        "- Source models: `['z-ai/glm-5.3-flash']`",
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
            f"Source model: `{row['model']}`  ",
            f"Cell: `{row['cell']}`  ",
            f"Condition: `{row['condition']}`  ",
            f"Word count: {row['word_count']}",
            "",
            text.strip(),
            "",
            "---",
        ]

    packet = OUT / "packet.md"
    packet.write_text("\n".join(parts) + "\n")
    metadata = {
        "cell": CELL,
        "safe_cell": CELL,
        "samples": len(rows),
        "sample_kind_counts": dict(kinds),
        "confidence_counts": dict(confidences),
        "condition_counts": dict(conditions),
        "source_models": ["z-ai/glm-5.3-flash"],
        "packet": str(packet.relative_to(ROOT)),
        "aggregate": str((OUT / "aggregate.md").relative_to(ROOT)),
    }
    (OUT / "packet.metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
