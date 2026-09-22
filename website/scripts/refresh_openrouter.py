#!/usr/bin/env python3
"""Refresh OpenRouter pricing and throughput stats in generated model data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from generate_data import MODEL_SLUGS, GENERATED, openrouter_for_model, openrouter_speed_label


THROUGHPUT_FIELDS = {
    "median_throughput",
    "max_throughput",
    "max_throughput_provider",
    "max_throughput_date",
}


def merge_openrouter(existing: dict | None, fresh: dict) -> dict:
    if not existing:
        return fresh
    merged = {**existing, **fresh}
    for field in THROUGHPUT_FIELDS:
        if fresh.get(field) is None and existing.get(field) is not None:
            merged[field] = existing[field]
    return merged


def main() -> None:
    models_path = GENERATED / "models.json"
    models = json.loads(models_path.read_text())
    updated = 0
    skipped = 0
    fresh_throughput = 0

    for model in models:
        model_id = model.get("model")
        if not model_id or model_id not in MODEL_SLUGS:
            skipped += 1
            continue
        fresh = openrouter_for_model(model_id)
        if not fresh or not fresh.get("matched"):
            print(f"warn: preserving existing OpenRouter data for {model_id}", file=sys.stderr)
            skipped += 1
            continue

        model["openrouter"] = merge_openrouter(model.get("openrouter"), fresh)
        openrouter_median = model["openrouter"].get("median_throughput")
        if openrouter_median:
            model["speed_tokens_per_second"] = openrouter_median
            model["speed_source"] = openrouter_speed_label(model["openrouter"])
        if fresh.get("median_throughput"):
            fresh_throughput += 1
        updated += 1

    models_path.write_text(json.dumps(models, indent=2, ensure_ascii=False) + "\n")
    print(f"refreshed OpenRouter data for {updated} models; skipped {skipped}; fresh throughput for {fresh_throughput}/{updated}")
    if updated and not fresh_throughput:
        print("ERROR: no model returned fresh throughput — the OpenRouter page format has probably changed; "
              "speeds on the site are now stale (their labels carry the last observation date)", file=sys.stderr)


if __name__ == "__main__":
    main()
