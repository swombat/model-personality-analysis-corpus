#!/usr/bin/env python3
"""Merge Phase 19 posture majority consensus with round-one adjudications."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "posture_collapsed"
BASE = ROOT / "consensus.jsonl"
ADJUDICATED = ROOT / "adjudication_round1" / "consensus.jsonl"
OUTPUT = ROOT / "final_consensus.jsonl"


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    rows = load(BASE)
    replacements = {row["layered_id"]: row for row in load(ADJUDICATED)}
    merged = [replacements.get(row["layered_id"], row) for row in rows]
    if len(merged) != 360 or len({row["layered_id"] for row in merged}) != 360:
        raise RuntimeError("Phase 19 final posture consensus must contain 360 unique records")
    if set(replacements) - {row["layered_id"] for row in rows}:
        raise RuntimeError("Adjudication contains IDs absent from the base consensus")
    OUTPUT.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in merged) + "\n"
    )
    print(f"{OUTPUT}: {len(merged)} records, {len(replacements)} adjudicated")


if __name__ == "__main__":
    main()
