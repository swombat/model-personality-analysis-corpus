#!/usr/bin/env python3
"""Wire the Epoch AI Capabilities Index ladder into the site.

Reads Epoch's per-model capability ladder (built by
internal/capability-ladder/ladder.py, sourced from Epoch AI's Capabilities
Index benchmark data, CC BY 4.0 — the only benchmark substrate this site is
licensed to redistribute) plus the site's alias map
(internal/capability-ladder/aliases.tsv, site_slug -> epoch_model with a
confidence tag), and writes the site's committed capability-ladder.json.

Every site model gets one of:

- a scored entry, resolved via an exact/snapshot-match/family-match alias
  to an Epoch `combined` entry, carrying the ladder score, how many of the
  ruler's rungs were actually measured for that model, and the match
  confidence;
- a `not_scored` entry, when no Epoch alias exists (aliases.tsv confidence
  "none") or the aliased Epoch entry cannot be found in ladder.json.

Usage:
    python3 website/scripts/refresh_capability_ladder.py

Environment:
    CAPABILITY_LADDER_JSON  Path (or later, URL) to Epoch's ladder.json.
                            Defaults to the pipeline's local output.
"""

from __future__ import annotations

import csv
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALIASES_PATH = ROOT / "internal" / "capability-ladder" / "aliases.tsv"
OUT_PATH = ROOT / "website" / "src" / "generated" / "capability-ladder.json"

DEFAULT_LADDER_JSON = "/Users/danieltenner/dev/model-capability/pipeline/data/ladder.json"

SOURCE_LABEL = "Epoch AI Capabilities Index, CC BY 4.0"


def load_ladder_json() -> dict:
    location = os.environ.get("CAPABILITY_LADDER_JSON", DEFAULT_LADDER_JSON)
    if location.startswith("http://") or location.startswith("https://"):
        with urllib.request.urlopen(location) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(location).read_text())


def load_aliases() -> list[dict[str, str]]:
    with ALIASES_PATH.open(newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    ladder = load_ladder_json()
    combined = ladder["combined"]
    points_per_rung = ladder["points_per_rung"]
    n_rungs = len(ladder["rungs"])
    ladder_max = points_per_rung * n_rungs
    if ladder_max == int(ladder_max):
        ladder_max = int(ladder_max)

    # Epoch model name -> combined entry. Checked unique at build time
    # (internal/capability-ladder/DESIGN.md, 2026-09-05 results): no two
    # combined entries currently share a `name`.
    by_name: dict[str, dict] = {}
    for entry in combined.values():
        name = entry.get("name")
        if name:
            by_name.setdefault(name, entry)

    aliases = load_aliases()
    models: dict[str, dict] = {}
    scored = 0
    not_scored = 0

    for row in aliases:
        site_slug = row["site_slug"]
        epoch_model = (row.get("epoch_model") or "").strip()
        confidence = (row.get("epoch_confidence") or "none").strip() or "none"
        entry = by_name.get(epoch_model) if confidence != "none" and epoch_model else None

        if entry is not None:
            models[site_slug] = {
                "ladder": round(entry["ladder"], 1),
                "ladder_max": ladder_max,
                "measured_rungs": entry["measured_rungs"],
                "n_rungs": entry["n_rungs"],
                "status": entry.get("status") or "scored",
                "epoch_model": epoch_model,
                "match_confidence": confidence,
                "point_variant": entry.get("point_variant"),
            }
            scored += 1
        else:
            models[site_slug] = {
                "ladder": None,
                "ladder_max": ladder_max,
                "measured_rungs": 0,
                "n_rungs": n_rungs,
                "status": "not_scored",
                "epoch_model": epoch_model or None,
                "match_confidence": "none",
                "point_variant": None,
            }
            not_scored += 1

    output = {
        "generated": ladder.get("generated"),
        "source": SOURCE_LABEL,
        "ladder_max": ladder_max,
        "n_rungs": n_rungs,
        "models": models,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")

    print(f"Wrote {OUT_PATH.relative_to(ROOT)}: {scored} scored, {not_scored} not_scored, ladder_max={ladder_max}")


if __name__ == "__main__":
    main()
