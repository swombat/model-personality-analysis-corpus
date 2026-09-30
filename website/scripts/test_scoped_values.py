import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_data as g


class ScopedValuesTests(unittest.TestCase):
    def test_unselected_flash_does_not_fold_into_glm_base(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            traces = root / "traces"
            for cell in ["glm-5-3-or-pin-z-ai-20260825", "glm-5-3-flashx-or-pin-zai"]:
                p = traces / ("freeflow_" + cell)
                p.mkdir(parents=True)
                (p / "SHORT_1.json").write_text(json.dumps(
                    {"model": cell, "result": "source " * 30, "condition": "SHORT"}))
            empty = root / "empty"
            empty.mkdir()
            with patch.multiple(g, V2_FREEFLOW=traces, V2_VALUES=empty,
                                V1_FREEFLOW=empty, V1_VALUES=empty,
                                PUBLIC_SAMPLES=root / "out",
                                SAMPLE_ROUTING_MODELS=["glm-5-3", "glm-5-3-flashx"]):
                counts = g.generate_samples(["glm-5-3"])
            self.assertEqual(counts["glm-5-3"]["freeflow"], 1)

    def test_medium_alias_remains_separate(self):
        cell = "ternary-bonsai-2-27b-or-pin-darkbloom-medium"
        self.assertIsNone(g.model_from_cell(cell, ["ternary-bonsai-2-27b"], "v2"))
        self.assertEqual(g.model_from_cell(cell, ["ternary-bonsai-2-27b-medium"], "v2"),
                         "ternary-bonsai-2-27b-medium")

    def test_residual_note_names_uncertainty(self):
        samples = [{"layered_id": "x", "sample_id": "G2_22"}]
        rows = {"x": {"collapsed_primary_label_support": 1, "value_holding_support": 1}}
        note = g.residual_values_note(samples, rows)
        self.assertIn("G2_22", note)
        self.assertIn("not majority", note)
        rows["x"] = {"collapsed_primary_label_support": 2, "value_holding_support": 2}
        self.assertEqual(g.residual_values_note(samples, rows), "")


if __name__ == "__main__":
    unittest.main()
