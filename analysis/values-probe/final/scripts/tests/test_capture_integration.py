import sys, unittest, json, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integrate_capture_values import merge_rows, check_residual_policy, sha


class MergeTests(unittest.TestCase):
    def test_preserves_old_duplicate_multiplicity(self):
        old = [
            {"id": "old", "value": 1},
            {"id": "old", "value": 1},
            {"id": "old", "value": 2},
        ]
        new = [{"id": "new", "value": 3}]
        self.assertEqual(merge_rows(old, new, "id"), old + new)
        self.assertEqual(merge_rows(old + new, new, "id"), old + new)

    def test_conflict_fails_closed(self):
        with self.assertRaises(AssertionError):
            merge_rows([{"id": "same", "v": 1}], [{"id": "same", "v": 2}], "id")

    def test_incoming_duplicates_rejected(self):
        with self.assertRaises(AssertionError):
            merge_rows([], [{"id": "x"}, {"id": "x"}], "id")


class ResidualPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.phase = Path(self.tmp.name)
        (self.phase / "posture_final").mkdir()
        self.adjudication = {"residual_splits": ["CAP_test_G2_22"]}
        self.rows = [{"layered_id": "CAP_test_G2_22",
                      "collapsed_primary_label_support": 1, "value_holding_support": 1}]
        (self.phase / "adjudication.json").write_text(json.dumps(self.adjudication))
        (self.phase / "posture_final/consensus.jsonl").write_text(json.dumps(self.rows[0]) + "\n")

    def policy(self):
        p = {"policy": "preserve-provisional-ties-with-disclosure-v1",
             "residual_splits": self.adjudication["residual_splits"],
             "adjudication_sha256": sha(self.phase / "adjudication.json"),
             "posture_sha256": sha(self.phase / "posture_final/consensus.jsonl"),
             "authorization": "explicit reviewed publication", "method_note": "METHOD.md"}
        (self.phase / "residual_publication_policy.json").write_text(json.dumps(p))

    def test_no_splits_needs_no_exception(self):
        check_residual_policy(self.phase, {"residual_splits": []}, [])

    def test_residual_rejected_without_policy(self):
        with self.assertRaises(AssertionError):
            check_residual_policy(self.phase, self.adjudication, self.rows)

    def test_reviewed_split_preserved(self):
        self.policy()
        before = json.dumps(self.rows)
        check_residual_policy(self.phase, self.adjudication, self.rows)
        self.assertEqual(before, json.dumps(self.rows))

    def test_changed_votes_fail_closed(self):
        self.policy()
        (self.phase / "posture_final/consensus.jsonl").write_text("changed")
        with self.assertRaises(AssertionError):
            check_residual_policy(self.phase, self.adjudication, self.rows)

    def test_unacknowledged_split_fails_closed(self):
        self.policy()
        with self.assertRaises(AssertionError):
            check_residual_policy(self.phase, {"residual_splits": []}, self.rows)
