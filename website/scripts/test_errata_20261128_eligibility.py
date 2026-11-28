#!/usr/bin/env python3
"""Regression tests for ERRATA-2026-11-28 cell eligibility & fail-closed sample routing."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import generate_data as GD


class Errata20261128EligibilityTests(unittest.TestCase):
    def test_fails_closed_when_provenance_manifests_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stale_corpus = Path(tmp)
            (stale_corpus / "data").mkdir()
            with self.assertRaises(FileNotFoundError):
                GD.v2_excluded_probe_cells(stale_corpus)
            (stale_corpus / "data" / "MODEL_IDENTITY_CORRECTIONS.json").write_text('{"version":1,"corrections":[]}')
            with self.assertRaises(FileNotFoundError):
                GD.v2_excluded_probe_cells(stale_corpus)

    def test_v2_exclusions_and_unaffected_neighbour(self) -> None:
        v2_root = Path(os.environ.get("MODEL_PERSONALITY_V2_CORPUS", str(GD.V2_CORPUS)))
        self.assertTrue(
            (v2_root / "ERRATA.md").is_file(),
            f"ERRATA.md required at reviewed corpus checkout {v2_root} (never skip on stale corpus)",
        )
        self.assertTrue((v2_root / "data" / "MODEL_IDENTITY_CORRECTIONS.json").is_file())
        self.assertTrue((v2_root / "data" / "SYSTEM_PROMPT_PROVENANCE.json").is_file())

        with tempfile.TemporaryDirectory() as tmp:
            tmp_samples = Path(tmp)
            with (
                mock.patch.object(GD, "V2_CORPUS", v2_root),
                mock.patch.object(GD, "V2_FREEFLOW", v2_root / "data" / "traces_freeflow"),
                mock.patch.object(GD, "V2_VALUES", v2_root / "data" / "traces_values"),
                mock.patch.object(GD, "PUBLIC_SAMPLES", tmp_samples),
                mock.patch.object(GD, "SAMPLE_ROUTING_MODELS", sorted(set(GD.MODEL_SLUGS) | set(GD.CELL_MODEL_ALIASES.values()))),
            ):
                target_models = [
                    "mixtral-8x22b-instruct",
                    "mistral-saba",
                    "mistral-small-24b-instruct-2501",
                    "ministral-8b-2512",
                ]
                counts = GD.generate_samples(target_models)

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

            self.assertEqual(counts["mistral-saba"]["freeflow"], 0)
            self.assertEqual(counts["mistral-saba"]["values"], 0)

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


    def test_grok_partition_exclusions(self) -> None:
        v2_root = Path(os.environ.get("MODEL_PERSONALITY_V2_CORPUS", str(GD.V2_CORPUS)))
        self.assertTrue((v2_root / "ERRATA.md").is_file())

        with tempfile.TemporaryDirectory() as tmp:
            tmp_samples = Path(tmp)
            with (
                mock.patch.object(GD, "V2_CORPUS", v2_root),
                mock.patch.object(GD, "V2_FREEFLOW", v2_root / "data" / "traces_freeflow"),
                mock.patch.object(GD, "V2_VALUES", v2_root / "data" / "traces_values"),
                mock.patch.object(GD, "PUBLIC_SAMPLES", tmp_samples),
                mock.patch.object(GD, "SAMPLE_ROUTING_MODELS", sorted(set(GD.MODEL_SLUGS) | set(GD.CELL_MODEL_ALIASES.values()))),
            ):
                counts = GD.generate_samples(["grok-3", "grok-4", "grok-4-3"])

            self.assertEqual(counts["grok-3"]["freeflow"], 25)
            self.assertEqual(counts["grok-3"]["values"], 120)
            g3_models = {
                (s["type"], s["model"])
                for s in json.loads((tmp_samples / "grok-3.json").read_text())["samples"]
            }
            self.assertEqual(g3_models, {("freeflow", "grok-3"), ("values", "grok-3")})

            self.assertEqual(counts["grok-4"]["freeflow"], 25)
            self.assertEqual(counts["grok-4"]["values"], 120)
            g4_models = {
                (s["type"], s["model"])
                for s in json.loads((tmp_samples / "grok-4.json").read_text())["samples"]
            }
            self.assertEqual(g4_models, {("freeflow", "grok-4-0709"), ("values", "grok-4-0709")})

            self.assertEqual(counts["grok-4-3"]["freeflow"], 250)
            self.assertEqual(counts["grok-4-3"]["values"], 240)


if __name__ == "__main__":
    unittest.main()
