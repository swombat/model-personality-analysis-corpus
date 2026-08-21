#!/usr/bin/env python3
"""Run the production BV1 evaluator only for the Ox Alpha freeflow cell."""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[4]
RUNNER = ROOT / "analysis/freeflow/personality-eval-bv1/run_full_bv1.py"
CELL = "ox-alpha-or-pin-stealth-20260821"


def load_runner():
    spec = importlib.util.spec_from_file_location("phase23_bv1_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    runner = load_runner()
    runner.OUT = PHASE / "freeflow_bv1"
    runner.OUTPUTS = ROOT / "analysis/freeflow/personality-eval-bv1/outputs"
    runner.CORPUS = ROOT.parent / "model-personality-corpus-v2/data/traces_freeflow"
    runner.OUT.mkdir(parents=True, exist_ok=True)
    runner.OUTPUTS.mkdir(parents=True, exist_ok=True)

    rows = [row for row in runner.build_rows() if row.get("cell") == CELL]
    if len(rows) != 125:
        raise RuntimeError(f"expected 125 Ox Alpha rows, found {len(rows)}")

    start = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(runner.process, row, False) for row in rows]
        for future in as_completed(futures):
            results.append(future.result())

    problems = []
    statuses = Counter()
    for row in rows:
        path = Path(row["outpath"])
        if not path.exists():
            problems.append({"sample_id": row["sample_id"], "problem": "missing"})
            continue
        ok, reason = runner.valid_output(path.read_text(errors="ignore"))
        statuses["valid" if ok else "invalid"] += 1
        if not ok:
            problems.append({"sample_id": row["sample_id"], "problem": reason})
    status = {
        "cell": CELL,
        "samples": len(rows),
        "statuses": dict(statuses),
        "problems": problems,
        "wall_seconds": time.time() - start,
    }
    (runner.OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status, indent=2), flush=True)


if __name__ == "__main__":
    main()
