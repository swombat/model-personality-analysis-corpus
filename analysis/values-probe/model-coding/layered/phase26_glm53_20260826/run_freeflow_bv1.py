#!/usr/bin/env python3
"""Complete production BV1 for the GLM 5.3 freeflow cell."""

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
CELL = "glm-5-3-or-pin-z-ai-20260825"


def load_runner():
    spec = importlib.util.spec_from_file_location("phase26_bv1_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    runner = load_runner()
    runner.OUT = PHASE / "freeflow_bv1"
    runner.OUTPUTS = ROOT / "analysis/freeflow/personality-eval-bv1/outputs"
    runner.CORPUS = (
        ROOT.parent / "model-personality-corpus-v2/data/traces_freeflow"
    )
    runner.OUT.mkdir(parents=True, exist_ok=True)
    runner.OUTPUTS.mkdir(parents=True, exist_ok=True)

    all_rows = runner.build_rows()
    rows = [row for row in all_rows if row.get("cell") == CELL]
    if len(rows) != 125:
        raise RuntimeError(f"expected 125 GLM 5.3 rows, found {len(rows)}")
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
    statuses = Counter()
    for row in rows:
        path = Path(row["outpath"])
        if not path.exists():
            problems.append(
                {"sample_id": row["sample_id"], "problem": "missing"}
            )
            continue
        ok, reason = runner.valid_output(path.read_text(errors="ignore"))
        statuses["valid" if ok else "invalid"] += 1
        if not ok:
            problems.append(
                {"sample_id": row["sample_id"], "problem": reason}
            )
    status = {
        "cell": CELL,
        "samples": len(rows),
        "statuses": dict(statuses),
        "problems": problems,
        "wall_seconds": time.time() - start,
    }
    (runner.OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status, indent=2), flush=True)
    if problems or statuses["valid"] != 125:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
