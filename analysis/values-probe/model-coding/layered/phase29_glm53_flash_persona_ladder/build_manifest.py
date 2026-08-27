#!/usr/bin/env python3
"""Build the 360-row Phase 29 persona-ladder values manifest."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


PHASE = Path(__file__).resolve().parent
ANALYSIS_REPO = Path(__file__).resolve().parents[5]
CORPUS = ANALYSIS_REPO.parent / "model-personality-corpus-v2"
OUT = PHASE / "manifest_phase29.jsonl"
CONDITIONS = {"CTRL1", "CTRL2", "CTRL3", "G1", "G2", "G3"}
CELLS = {
    "P0": "glm-5-3-flash-or-pin-deepinfra-p0-20260827",
    "P1": "glm-5-3-flash-or-pin-deepinfra-p1-20260827",
    "P2": "glm-5-3-flash-or-pin-deepinfra-p2-20260827",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cells",
        nargs="*",
        choices=list(CELLS),
        default=list(CELLS),
        help="Persona cells to include (default: all).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT,
        help="Output JSONL path.",
    )
    args = parser.parse_args()

    rows = []
    selected_cells = {
        key: cell for key, cell in CELLS.items() if key in set(args.cells)
    }
    for persona_condition, cell in selected_cells.items():
        trace_dir = CORPUS / "data" / "traces_values" / cell
        for path in sorted(trace_dir.glob("*.json")):
            source = json.loads(path.read_text())
            response = (source.get("result") or "").strip()
            condition = source.get("condition") or path.stem.split("_", 1)[0]
            if not response or condition not in CONDITIONS:
                continue
            rows.append(
                {
                    "layered_id": f"P29_{persona_condition}_{path.stem}",
                    "model": "glm-5-3-flash",
                    "model_family": "glm",
                    "cell": cell,
                    "persona_condition": persona_condition,
                    "system_prompt": source.get("system_prompt"),
                    "sample_id": path.stem,
                    "condition": condition,
                    "prompt": source.get("prompt", ""),
                    "response": response,
                    "provider": source.get("provider", ""),
                    "upstream_provider": (source.get("raw") or {}).get("provider"),
                    "model_requested": source.get("model_requested")
                    or source.get("model"),
                    "trace_path": f"data/traces_values/{cell}/{path.name}",
                    "processing_chain": (
                        "world_change_wishes"
                        if condition in {"CTRL3", "G3"}
                        else "stated_values"
                    ),
                    "selection_stratum": (
                        f"phase29_20260827_persona_ladder_{persona_condition.lower()}"
                    ),
                    "is_enriched": False,
                }
            )

    per_cell = Counter(row["persona_condition"] for row in rows)
    per_condition = Counter(
        (row["persona_condition"], row["condition"]) for row in rows
    )
    expected_conditions = {
        "CTRL1": 10,
        "CTRL2": 10,
        "CTRL3": 10,
        "G1": 30,
        "G2": 30,
        "G3": 30,
    }
    errors = []
    for persona_condition in selected_cells:
        if per_cell[persona_condition] != 120:
            errors.append(
                f"{persona_condition}: {per_cell[persona_condition]}/120 rows"
            )
        for condition, expected in expected_conditions.items():
            actual = per_condition[(persona_condition, condition)]
            if actual != expected:
                errors.append(
                    f"{persona_condition}/{condition}: {actual}/{expected}"
                )
    if errors:
        raise RuntimeError("incomplete manifest: " + "; ".join(errors))

    rows.sort(key=lambda r: (r["persona_condition"], r["sample_id"]))
    args.out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    print(
        json.dumps(
            {
                "samples": len(rows),
                "per_cell": dict(per_cell),
                "out": str(args.out),
            }
        )
    )


if __name__ == "__main__":
    main()
