import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integrate_capture_values import merge_rows


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
