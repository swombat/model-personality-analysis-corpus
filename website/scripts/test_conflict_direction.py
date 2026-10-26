#!/usr/bin/env python3
"""Regression: a zero disclosure-conflict gap must not be described as 'higher' (Mira's review JbVorJ, 2026-10-26)."""

from __future__ import annotations

import json

from generate_data import GENERATED, conflict_direction


def main() -> None:
    assert conflict_direction(10.0, 10.0).startswith("no difference"), conflict_direction(10.0, 10.0)
    assert conflict_direction(10.0, 40.0) == "higher under cache-broken G1/G2 prompts"
    assert conflict_direction(40.0, 10.0) == "higher under direct CTRL1/2 prompts"
    for model in json.loads((GENERATED / "models.json").read_text()):
        c = (model.get("values_headline") or {}).get("conflict")
        if c:
            assert c["direction"] == conflict_direction(c["ctrl_percent"], c["g_percent"]), (model["model"], c)
    print("conflict direction: ok")


if __name__ == "__main__":
    main()
