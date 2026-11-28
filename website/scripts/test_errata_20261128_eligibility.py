#!/usr/bin/env python3
"""Regression tests for ERRATA-2026-11-28 cell eligibility & sample routing."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import generate_data as GD


class Errata20261128EligibilityTests(unittest.TestCase):
    def test_v2_exclusions_and_unaffected_neighbour(self) -> None:
        v2_root = Path(os.environ.get("MODEL_PERSONALITY_V2_CORPUS", str(GD.V2_CORPUS)))
        if not (v2_root / "ERRATA.md").is_file():
            self.skipTest(f"ERRATA.md not present in {v2_root}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_samples = Path(tmp)
            with (
                mock.patch.object(GD, "V2_CORPUS", v2_root),
                mock.patch.object(GD, "V2_FREEFLOW", v2_root / "data" / "traces_freeflow"),
                mock.patch.object(GD, "V2_VALUES", v2_root / "data" / "traces_values"),
                mock.patch.object(GD, "PUBLIC_SAMPLES", tmp_samples),
            ):
                target_models = [
                    "mixtral-8x22b-instruct",
                    "mistral-saba",
                    "mistral-small-24b-instruct-2501",
                    "ministral-8b-2512",
                ]
                counts = GD.generate_samples(target_models)

            # 1. Genuine Mixtral-8x22B-v0.1 replaces retired API slug without pooling
            self.assertEqual(counts["mixtral-8x22b-instruct"]["freeflow"], 125)
            self.assertEqual(counts["mixtral-8x22b-instruct"]["values"], 120)
            mix_cells = {
                s["cell"]
                for s in json.loads((tmp_samples / "mixtral-8x22b-instruct.json").read_text())["samples"]
            }
            self.assertEqual(
                mix_cells,
                {
                    "freeflow_mixtral-8x22b-instruct-v0-1-runpod-vllm-bf16-rcc88a6cc",
                    "mixtral-8x22b-instruct-v0-1-runpod-vllm-bf16-rcc88a6cc",
                },
            )

            # 2. Retired Saba slug is completely excluded from named-weight bundles
            self.assertEqual(counts["mistral-saba"]["freeflow"], 0)
            self.assertEqual(counts["mistral-saba"]["values"], 0)

            # 3. Bare Small-2501 replaces DeepInfra system-prompted cell without pooling
            self.assertEqual(counts["mistral-small-24b-instruct-2501"]["freeflow"], 125)
            self.assertEqual(counts["mistral-small-24b-instruct-2501"]["values"], 120)
            s2501_cells = {
                s["cell"]
                for s in json.loads((tmp_samples / "mistral-small-24b-instruct-2501.json").read_text())["samples"]
            }
            self.assertEqual(
                s2501_cells,
                {
                    "freeflow_mistral-small-24b-instruct-2501-runpod-vllm-bf16-bare-r8f4e4ef3",
                    "mistral-small-24b-instruct-2501-runpod-vllm-bf16-bare-r8f4e4ef3",
                },
            )

            # 4. Unaffected neighbour ministral-8b-2512 stays intact and un-pooled
            self.assertEqual(counts["ministral-8b-2512"]["freeflow"], 125)
            self.assertEqual(counts["ministral-8b-2512"]["values"], 120)
            m8b_cells = {
                s["cell"]
                for s in json.loads((tmp_samples / "ministral-8b-2512.json").read_text())["samples"]
            }
            self.assertEqual(
                m8b_cells,
                {
                    "freeflow_ministral-8b-2512-or-pin-mistral",
                    "ministral-8b-2512-or-pin-mistral",
                },
            )


if __name__ == "__main__":
    unittest.main()
