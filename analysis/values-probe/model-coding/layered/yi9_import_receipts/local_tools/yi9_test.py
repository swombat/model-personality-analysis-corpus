import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yi9_import as importer
import yi9_apply as apply


class Evidence(unittest.TestCase):
    def test_actual(self):
        result = importer.inspect()
        self.assertEqual(len(result["task_snapshots"]["finish"]), 6)
        self.assertEqual(result["variant_samples"], ["LONG_25", "LONG_9", "OPEN_18"])
        self.assertEqual(sum(e["destination"].startswith("raw/") for e in result["entries"]), 245)
        self.assertEqual(result["isolated_values_recovery"]["requests"], 1)
        self.assertTrue(any("returned-answer.json" in e["destination"] for e in result["entries"]))

    def test_pin(self):
        with patch.object(importer, "SPEC_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "spec drift"):
                importer.inspect()

    def test_adopted_posture(self):
        original = importer.read
        def read(path, *args, **kwargs):
            if "capture_recovery_v1_" in str(path) and str(path).endswith("/samples/G1_20/posture/kimi-k2-6.jsonl"):
                return b"corrupt"
            return original(path, *args, **kwargs)
        with patch.object(importer, "read", side_effect=read):
            with self.assertRaisesRegex(ValueError, "receipt hash"):
                importer.inspect()

    def test_untrusted_raw_manifest_path(self):
        original = importer.read
        def read(path, *args, **kwargs):
            data = original(path, *args, **kwargs)
            if str(path).endswith("/manifest.jsonl"):
                data = data.replace(b'"trace_path": "data/', b'"trace_path": "../data/')
            return data
        with patch.object(importer, "read", side_effect=read):
            with self.assertRaises(ValueError):
                importer.inspect()

    def test_multiset(self):
        self.assertTrue(apply.lane.rows(b'{"x":1}\n{"x":1}\n') - apply.lane.rows(b'{"x":1}\n'))

    def test_wrong_base_no_writes(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(apply, "TARGET", Path(td)), \
                 patch.object(importer, "inspect", return_value={"import_complete": True}), \
                 patch.object(apply.lane.subprocess, "check_output", return_value=b"wrong\n"):
                with self.assertRaisesRegex(ValueError, "base changed"):
                    apply.main()
            self.assertEqual(list(Path(td).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
