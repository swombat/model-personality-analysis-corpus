#!/usr/bin/env python3
"""Regression checks for the three Phase-19 model cards."""

from __future__ import annotations

import json

from generate_data import GENERATED, PUBLIC_MODEL_IMAGES, PUBLIC_SAMPLES


EXPECTED = {
    "deepseek-v4-flash-0731": {
        "benchmark": 50,
        "openrouter_id": "deepseek/deepseek-v4-flash-0731",
        "input_price": 0.09,
        "output_price": 0.18,
    },
    "inkling-small": {"benchmark": 40},
    "qwen3-7-flash": {"benchmark": None},
}


def main() -> None:
    models = {
        row["model"]: row
        for row in json.loads((GENERATED / "models.json").read_text())
    }

    for slug, expected in EXPECTED.items():
        model = models[slug]
        assert model["status"] == "complete"
        assert model["analyzed_freeflow_samples"] == 125
        assert model["analyzed_values_samples"] == 120
        assert model["published_freeflow_samples"] == 125
        assert model["published_values_samples"] == 120
        assert model["published_samples"] == 245
        assert model["personality_card_markdown"].strip()
        assert model["personality_profile_markdown"].strip()
        assert model["values_summary_markdown"].strip()
        assert model["values_details_markdown"].strip()
        assert model["summary"].strip()
        assert model["release_date"] == "2026-07-31"
        assert (PUBLIC_MODEL_IMAGES / f"{slug}.webp").is_file()
        assert (PUBLIC_MODEL_IMAGES / f"{slug}-thumb.webp").is_file()

        benchmark = model.get("benchmarks")
        expected_score = expected["benchmark"]
        if expected_score is None:
            assert benchmark is None
        else:
            assert benchmark and benchmark["aaii"] == expected_score

        if expected.get("openrouter_id"):
            openrouter = model["openrouter"]
            assert openrouter["matched"] is True
            assert openrouter["id"] == expected["openrouter_id"]
            assert openrouter["prompt_per_million"] == expected["input_price"]
            assert openrouter["completion_per_million"] == expected["output_price"]

        samples = json.loads((PUBLIC_SAMPLES / f"{slug}.json").read_text())["samples"]
        assert len(samples) == 245

    print("Phase-19 card checks passed for 3 models (735 published samples)")


if __name__ == "__main__":
    main()
