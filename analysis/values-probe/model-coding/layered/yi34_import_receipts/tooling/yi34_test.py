import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yi34_import as importer
import yi34_apply as apply


class Evidence(unittest.TestCase):
    def test_actual_complete_model(self):
        r = importer.inspect()
        self.assertTrue(r["import_complete"])
        self.assertEqual(set(r["variant_samples"]), importer.SAMPLES)
        self.assertEqual(len(r["task_snapshots"]["finish"]), 10)
        self.assertEqual(sum(e["destination"].startswith("raw/") for e in r["entries"]), 245)
        for part in ("/phase/freeflow_bv1_luna_v1/attempt_responses/",
                     "/phase/freeflow_bv1_luna_v1_targeted/attempt_responses/"):
            self.assertTrue(any(part in e["destination"] for e in r["entries"]))

    def test_finish_pin_rejects_drift(self):
        with patch.object(importer, "SPEC_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "spec drift"):
                importer.inspect()

    def test_adoption_mismatch_rejected(self):
        original = importer.read
        def read(path, *args, **kwargs):
            if str(path).endswith("/samples/G3_25/layer_a/kimi-k2-6.jsonl") and "capture_recovery_v1_" in str(path):
                return b"corrupt\n"
            return original(path, *args, **kwargs)
        with patch.object(importer, "read", side_effect=read):
            with self.assertRaisesRegex(ValueError, "receipt hash"):
                importer.inspect()

    def test_final_manifest_cannot_rename_targeted_to_v1(self):
        original = importer.read
        def read(path, *args, **kwargs):
            data = original(path, *args, **kwargs)
            if str(path).endswith("/freeflow_bv1_luna_v1/sample_manifest.tsv"):
                data = data.replace(importer.variant.ARM.encode(), importer.variant.V1.encode())
            return data
        with patch.object(importer, "read", side_effect=read):
            with self.assertRaisesRegex(ValueError, "mixed manifest"):
                importer.inspect()

    def test_ten_jobs_required(self):
        original = importer.common.snapshot
        def snapshot(directory):
            spec, tasks, rows = original(directory)
            return spec, tasks, rows[:-1] if directory == importer.STATE else rows
        with patch.object(importer.common, "snapshot", side_effect=snapshot):
            with self.assertRaisesRegex(ValueError, "job inventory"):
                importer.inspect()

    def test_multiset_not_set(self):
        self.assertTrue(apply.lane.rows(b'{"x":1}\n{"x":1}\n') - apply.lane.rows(b'{"x":1}\n'))

    def test_apply_wrong_base_no_writes(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            with patch.object(apply, "TARGET", target), \
                 patch.object(importer, "inspect", return_value={"import_complete": True}), \
                 patch.object(apply.lane.subprocess, "check_output", return_value=b"wrong\n"):
                with self.assertRaisesRegex(ValueError, "base changed"):
                    apply.main()
            self.assertEqual(list(target.iterdir()), [])

    def test_apply_occupied_index_no_writes(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            with patch.object(apply, "TARGET", target), \
                 patch.object(importer, "inspect", return_value={"import_complete": True}), \
                 patch.object(apply.lane.subprocess, "check_output",
                              side_effect=[(apply.HEAD + "\n").encode(), b"website/file\n"]):
                with self.assertRaisesRegex(ValueError, "index already populated"):
                    apply.main()
            self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
