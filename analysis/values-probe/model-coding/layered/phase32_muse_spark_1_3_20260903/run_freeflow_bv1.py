#!/usr/bin/env python3
"""Run production BV1 only for both Muse Spark 1.3 corpus cells."""

from __future__ import annotations

import importlib.util
import argparse
import json
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[4]
RUNNER = ROOT / "analysis/freeflow/personality-eval-bv1/run_full_bv1.py"
CELLS = {
    "muse-spark-1-1-or-pin-meta-20260813",
    "muse-spark-1-2-or-pin-meta-20260813",
    "muse-spark-1-2-contributor-or-pin-meta",
    "muse-glimmer-30b-or-pin-deepinfra-20260813",
    "muse-spark-1-3-or-pin-meta",
    "muse-spark-1-3-contributor-or-pin-meta",
}


def load_runner():
    spec = importlib.util.spec_from_file_location("phase32_bv1_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cells",
        nargs="*",
        choices=sorted(CELLS),
        help="Optional subset to process now; a later full run safely skips valid outputs.",
    )
    args = parser.parse_args()
    active_cells = set(args.cells) if args.cells else CELLS

    runner = load_runner()
    runner.OUT = PHASE / "freeflow_bv1"
    runner.OUTPUTS = ROOT / "analysis/freeflow/personality-eval-bv1/outputs"
    runner.CORPUS = (
        ROOT.parent / "model-personality-corpus-v2/data/traces_freeflow"
    )
    runner.OUT.mkdir(parents=True, exist_ok=True)
    runner.OUTPUTS.mkdir(parents=True, exist_ok=True)

    rows = [row for row in runner.build_rows() if row.get("cell") in active_cells]
    per_cell = Counter(row["cell"] for row in rows)
    expected_rows = 125 * len(active_cells)
    if (
        len(rows) != expected_rows
        or set(per_cell) != active_cells
        or set(per_cell.values()) != {125}
    ):
        raise RuntimeError(
            f"expected {len(active_cells)} complete 125-sample cells, found {per_cell}"
        )

    manifest_lines = [
        "pid\tmodel\tcell\tcondition\tprovider\tsample_id\tword_count"
        "\tsource_json\toutput_file"
    ]
    for row in rows:
        manifest_lines.append(
            "\t".join(
                str(row[key])
                for key in [
                    "pid",
                    "model",
                    "cell",
                    "condition",
                    "provider",
                    "sample_id",
                    "word_count",
                    "source",
                    "outpath",
                ]
            )
        )
    (runner.OUT / "sample_manifest.tsv").write_text(
        "\n".join(manifest_lines) + "\n"
    )

    start = time.time()
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(runner.process, row, False) for row in rows]
        for future in as_completed(futures):
            future.result()

    problems = []
    statuses: dict[str, Counter[str]] = {cell: Counter() for cell in active_cells}
    for row in rows:
        path = Path(row["outpath"])
        if not path.exists():
            problems.append(
                {"cell": row["cell"], "sample_id": row["sample_id"], "problem": "missing"}
            )
            continue
        ok, reason = runner.valid_output(path.read_text(errors="ignore"))
        statuses[row["cell"]]["valid" if ok else "invalid"] += 1
        if not ok:
            problems.append(
                {
                    "cell": row["cell"],
                    "sample_id": row["sample_id"],
                    "problem": reason,
                }
            )
    status = {
        "cells": sorted(active_cells),
        "samples": len(rows),
        "per_cell": {cell: dict(counts) for cell, counts in statuses.items()},
        "problems": problems,
        "wall_seconds": time.time() - start,
    }
    (runner.OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status, indent=2), flush=True)
    if problems or any(counts["valid"] != 125 for counts in statuses.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
