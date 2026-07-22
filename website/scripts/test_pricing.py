#!/usr/bin/env python3
"""Focused regression checks for authoritative website pricing."""

from __future__ import annotations

import json

from generate_data import FIRST_PARTY_API_PRICING, GENERATED, MODEL_SLUGS


CORRECTED = {
    "gpt-5-6-sol": (5.00, 30.00, "OpenAI API"),
    "gpt-5-6-terra": (2.50, 15.00, "OpenAI API"),
    "gpt-5-6-luna": (1.00, 6.00, "OpenAI API"),
    "grok-4-5": (2.00, 6.00, "xAI API"),
}


def main() -> None:
    models = {model["model"]: model for model in json.loads((GENERATED / "models.json").read_text())}

    for model, expected in FIRST_PARTY_API_PRICING.items():
        assert MODEL_SLUGS.get(model), f"{model} is missing its OpenRouter slug"
        assert model in models, f"{model} is missing from generated website data"

        generated = models[model].get("openrouter") or {}
        actual = (
            generated.get("prompt_per_million"),
            generated.get("completion_per_million"),
            generated.get("pricing_source"),
        )
        assert actual == expected, f"{model}: generated {actual}, expected {expected}"

    for model, expected in CORRECTED.items():
        assert FIRST_PARTY_API_PRICING.get(model) == expected, f"{model} correction regressed"

    print(
        f"pricing checks passed for {len(FIRST_PARTY_API_PRICING)} first-party models "
        f"including {len(CORRECTED)} corrected models"
    )


if __name__ == "__main__":
    main()
