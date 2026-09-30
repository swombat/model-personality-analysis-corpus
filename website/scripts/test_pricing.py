#!/usr/bin/env python3
"""Focused regression checks for authoritative website pricing."""

from __future__ import annotations

import json

from generate_data import API_ACCESS_OVERRIDES, FIRST_PARTY_API_PRICING, GENERATED, MODEL_SLUGS


CORRECTED = {
    "deepseek-v4-flash": (0.14, 0.28, "DeepSeek API (May 2026 pricing)"),
    "gpt-5-6-sol": (5.00, 30.00, "OpenAI API"),
    "gpt-5-6-terra": (2.50, 15.00, "OpenAI API"),
    "gpt-5-6-luna": (1.00, 6.00, "OpenAI API"),
    "grok-4-5": (2.00, 6.00, "xAI API"),
}

# The May deployment has no public profile. The separately captured July 31
# snapshot is `deepseek-v4-flash-0731`; do not transfer historical May prices to
# it merely to make this test green. Retain the historical correction check.
HISTORICAL_UNPUBLISHED = {"deepseek-v4-flash"}


def main() -> None:
    models = {model["model"]: model for model in json.loads((GENERATED / "models.json").read_text())}

    for model, expected in FIRST_PARTY_API_PRICING.items():
        assert MODEL_SLUGS.get(model) or model in API_ACCESS_OVERRIDES, (
            f"{model} has neither an OpenRouter slug nor an explicit access override"
        )
        if model in HISTORICAL_UNPUBLISHED:
            assert model not in models, f"{model} is published again; restore its pricing check"
            continue
        assert model in models, f"{model} is missing from generated website data"

        generated = models[model].get("openrouter") or {}
        # Access provenance deliberately refines the source label for local
        # measured cells with separately listed hosted prices.
        expected = (
            expected[0], expected[1],
            API_ACCESS_OVERRIDES.get(model, {}).get("pricing_source", expected[2]),
        )
        actual = (
            generated.get("prompt_per_million"),
            generated.get("completion_per_million"),
            generated.get("pricing_source"),
        )
        assert actual == expected, f"{model}: generated {actual}, expected {expected}"

    for model, expected in CORRECTED.items():
        assert FIRST_PARTY_API_PRICING.get(model) == expected, f"{model} correction regressed"

    print(
        f"pricing checks passed for {len(FIRST_PARTY_API_PRICING) - len(HISTORICAL_UNPUBLISHED)} published first-party models "
        f"including {len(CORRECTED)} correction records (one historical unpublished deployment)"
    )


if __name__ == "__main__":
    main()
