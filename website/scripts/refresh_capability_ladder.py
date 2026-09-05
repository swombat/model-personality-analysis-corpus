#!/usr/bin/env python3
"""Wire a capability ladder into the site.

Two independently-computed ladders exist, built by the same method (every
public benchmark is a rung worth 10 points times the model's
chance-corrected score; missing cells are filled in with an item-response
fit; rungs are never retired) over two different benchmark substrates:

- ``aa`` (default): Artificial Analysis's own per-benchmark results
  (public model pages), median-thinking-budget variant. 19 rungs, max 190.
  This is the ladder the site displays.
- ``epoch``: Epoch AI's Capabilities Index (CC BY 4.0), used as an
  independent cross-check that the fit lands rungs at the same
  difficulties. 59 rungs, max 590. Kept as an option here so the same
  script can regenerate either file; not the site's displayed source.

Reads the chosen substrate's ``ladder.json`` (built by
internal/capability-ladder/ladder.py) plus the site's alias map
(internal/capability-ladder/aliases.tsv), and writes the site's committed
capability-ladder.json.

Alias resolution differs by substrate:

- ``epoch``: aliases.tsv's ``epoch_model`` column is matched against each
  combined entry's ``name`` field (exact string match).
- ``aa``: aliases.tsv's ``aa_slug`` column is matched against each combined
  entry's ``link_slug`` field — the base slug with any reasoning-effort
  suffix already stripped by the pipeline (e.g. ``claude-fable-5-1``, not
  ``claude-fable-5-1-high``). Where aa_slug was recorded against a specific
  effort/reasoning variant (an artifact of the older AAII-era alias table)
  and no exact link_slug match exists, both sides are normalized by
  stripping known effort/reasoning-mode suffixes and matched again; this
  is what folds e.g. `grok-4-6` (site's old "-xhigh" alias) onto the
  Combined median-effort entry, and is also where reasoning/non-reasoning
  site variants can collapse onto one Combined entry if Artificial
  Analysis does not track them as distinct base models.

Every site model gets a ladder score, a not_scored entry (if
``benchmarks.aaii`` should be tried as a fallback — handled downstream in
generate_data.py, not here), or nothing.

Usage:
    python3 website/scripts/refresh_capability_ladder.py [--substrate aa|epoch]

Environment:
    CAPABILITY_LADDER_JSON  Path (or URL) to the substrate's ladder.json.
                            Overrides the substrate's default path.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALIASES_PATH = ROOT / "internal" / "capability-ladder" / "aliases.tsv"
OUT_PATH = ROOT / "website" / "src" / "generated" / "capability-ladder.json"

DEFAULT_LADDER_JSON = {
    "aa": "/Users/danieltenner/dev/model-capability-aa/pipeline/data/ladder.json",
    "epoch": "/Users/danieltenner/dev/model-capability/pipeline/data/ladder.json",
}

SOURCE_LABEL = {
    "aa": (
        "Artificial Analysis per-benchmark results (public model pages), "
        "fitted by the Model Capability Ladder pipeline; "
        "permission requested 2026-09-05"
    ),
    "epoch": "Epoch AI Capabilities Index, CC BY 4.0",
}

# Tokens the pipeline appends to a base model slug to name a specific
# reasoning-effort or reasoning-mode variant. Stripped (longest-first, so a
# compound like "-reasoning-default" doesn't get half-stripped into a
# dangling "-default") when an exact alias match fails, to fold an
# effort-specific alias onto the Combined (median-effort) base entry.
EFFORT_SUFFIXES = [
    "-non-reasoning",
    "-reasoning-default",
    "-reasoning",
    "-xhigh",
    "-high",
    "-medium",
    "-low",
    "-minimal",
    "-max",
    "-default",
    "-thinking",
    "-adaptive",
]


def strip_effort_suffix(slug: str) -> str:
    changed = True
    while changed:
        changed = False
        for suffix in EFFORT_SUFFIXES:
            if slug.endswith(suffix):
                slug = slug[: -len(suffix)]
                changed = True
                break
    return slug


def load_ladder_json(substrate: str) -> dict:
    location = os.environ.get("CAPABILITY_LADDER_JSON", DEFAULT_LADDER_JSON[substrate])
    if location.startswith("http://") or location.startswith("https://"):
        with urllib.request.urlopen(location) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(location).read_text())


def load_aliases() -> list[dict[str, str]]:
    with ALIASES_PATH.open(newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def resolve_epoch(row: dict[str, str], by_name: dict[str, dict]) -> tuple[dict | None, str]:
    epoch_model = (row.get("epoch_model") or "").strip()
    confidence = (row.get("epoch_confidence") or "none").strip() or "none"
    if confidence == "none" or not epoch_model:
        return None, "none"
    return by_name.get(epoch_model), confidence


def resolve_aa(row: dict[str, str], by_link: dict[str, dict], by_link_normalized: dict[str, dict]) -> tuple[dict | None, str]:
    aa_slug = (row.get("aa_slug") or "").strip()
    if not aa_slug:
        return None, "none"
    entry = by_link.get(aa_slug)
    if entry is not None:
        return entry, "exact"
    normalized = strip_effort_suffix(aa_slug)
    entry = by_link_normalized.get(normalized)
    if entry is not None:
        return entry, "family-match"
    return None, "none"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--substrate", choices=["aa", "epoch"], default="aa")
    args = parser.parse_args()
    substrate = args.substrate

    ladder = load_ladder_json(substrate)
    combined = ladder["combined"]
    points_per_rung = ladder["points_per_rung"]
    n_rungs = len(ladder["rungs"])
    ladder_max = points_per_rung * n_rungs
    if ladder_max == int(ladder_max):
        ladder_max = int(ladder_max)

    if substrate == "epoch":
        # Epoch model name -> combined entry. No two combined entries
        # currently share a `name` (checked at build time,
        # internal/capability-ladder/DESIGN.md, 2026-09-05 results).
        by_name: dict[str, dict] = {}
        for entry in combined.values():
            name = entry.get("name")
            if name:
                by_name.setdefault(name, entry)
        by_link = by_link_normalized = {}
    else:
        # link_slug is the base slug with any effort suffix already
        # stripped by the pipeline (unique across the 513-entry combined
        # map, checked here at generation time).
        by_link = {}
        for entry in combined.values():
            link_slug = entry.get("link_slug")
            if link_slug:
                by_link.setdefault(link_slug, entry)
        by_link_normalized = {}
        for link_slug, entry in by_link.items():
            normalized = strip_effort_suffix(link_slug)
            by_link_normalized.setdefault(normalized, entry)
        by_name = {}

    aliases = load_aliases()
    models: dict[str, dict] = {}
    scored = 0
    not_scored = 0

    for row in aliases:
        site_slug = row["site_slug"]
        if substrate == "epoch":
            entry, confidence = resolve_epoch(row, by_name)
            matched_model = (row.get("epoch_model") or "").strip() or None
        else:
            entry, confidence = resolve_aa(row, by_link, by_link_normalized)
            matched_model = entry.get("base_name") if entry else ((row.get("aa_slug") or "").strip() or None)

        # An alias can resolve to a real combined entry that nonetheless has
        # no ladder score — the AA substrate marks these
        # "insufficient_measurements" (below the 3-rung floor). Treat that
        # the same as no match: a matched-but-unscored entry is still
        # unscored.
        if entry is not None and entry.get("ladder") is None:
            entry = None

        if entry is not None:
            models[site_slug] = {
                "ladder": round(entry["ladder"], 1),
                "ladder_max": ladder_max,
                "measured_rungs": entry["measured_rungs"],
                "n_rungs": entry["n_rungs"],
                "status": "scored",
                "matched_model": matched_model,
                "match_confidence": confidence,
                "point_variant": entry.get("point_variant"),
                "source": SOURCE_LABEL[substrate],
            }
            scored += 1
        else:
            models[site_slug] = {
                "ladder": None,
                "ladder_max": ladder_max,
                "measured_rungs": 0,
                "n_rungs": n_rungs,
                "status": "not_scored",
                "matched_model": None,
                "match_confidence": "none",
                "point_variant": None,
                "source": SOURCE_LABEL[substrate],
            }
            not_scored += 1

    output = {
        "generated": ladder.get("generated"),
        "substrate": substrate,
        "source": SOURCE_LABEL[substrate],
        "ladder_max": ladder_max,
        "n_rungs": n_rungs,
        "models": models,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")

    print(
        f"Wrote {OUT_PATH.relative_to(ROOT)} (substrate={substrate}): "
        f"{scored} scored, {not_scored} not_scored, ladder_max={ladder_max}"
    )


if __name__ == "__main__":
    main()
