import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import gemma7_import as importer
import gemma7_apply as apply


class ModelEvidence(unittest.TestCase):
    def test_actual_complete_model(self):
        r = importer.inspect()
        self.assertTrue(r["import_complete"])
        self.assertEqual(r["variant_samples"], ["MID_5", "VARY_9"])
        self.assertEqual(len(r["task_snapshots"]["finish"]), 10)
        self.assertEqual(len([e for e in r["entries"] if e["destination"].startswith("raw/")]), 245)
        self.assertTrue(any("/phase/freeflow_bv1_luna_v1/attempt_responses/" in e["destination"]
                            for e in r["entries"]))

    def test_finish_pin_rejects_drift(self):
        with patch.object(importer, "SPEC_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "spec drift"):
                importer.inspect()

    def test_adoption_mismatch_rejected(self):
        original = importer.read
        def read(path, *args, **kwargs):
            if str(path).endswith("/samples/G1_27/layer_a/glm-4-7.jsonl") and "capture_recovery_v1_" in str(path):
                return b"corrupt\n"
            return original(path, *args, **kwargs)
        with patch.object(importer, "read", side_effect=read):
            with self.assertRaisesRegex(ValueError, "adopted receipt hash"):
                importer.inspect()

    def test_final_manifest_cannot_rename_targeted_to_v1(self):
        original = importer.read
        def read(path, *args, **kwargs):
            data = original(path, *args, **kwargs)
            if str(path).endswith("/freeflow_bv1_luna_v1/sample_manifest.tsv"):
                data = data.replace(importer.planner.variant.ARM.encode(), importer.planner.variant.V1.encode())
            return data
        with patch.object(importer, "read", side_effect=read):
            with self.assertRaisesRegex(ValueError, "mixed-arm manifest"):
                importer.inspect()

    def test_ten_jobs_required(self):
        original = importer.planner.common.snapshot
        def snapshot(directory):
            spec, tasks, rows = original(directory)
            if directory == importer.STATE:
                rows = rows[:-1]
            return spec, tasks, rows
        with patch.object(importer.planner.common, "snapshot", side_effect=snapshot):
            with self.assertRaisesRegex(ValueError, "ten terminal"):
                importer.inspect()

    def test_multiset_not_set(self):
        self.assertTrue(apply.rows(b'{"x":1}\n{"x":1}\n') - apply.rows(b'{"x":1}\n'))

    def test_apply_wrong_base_no_writes(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            with patch.object(apply, "TARGET", target), \
                 patch.object(importer, "inspect", return_value={"import_complete": True}), \
                 patch.object(apply.subprocess, "check_output", return_value=b"wrong\n"):
                with self.assertRaisesRegex(ValueError, "base changed"):
                    apply.main()
            self.assertEqual(list(target.iterdir()), [])

    def test_apply_occupied_index_no_writes(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            with patch.object(apply, "TARGET", target), \
                 patch.object(importer, "inspect", return_value={"import_complete": True}), \
                 patch.object(apply.subprocess, "check_output",
                              side_effect=[(apply.HEAD + "\n").encode(), b"website/file\n"]):
                with self.assertRaisesRegex(ValueError, "index already populated"):
                    apply.main()
            self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
