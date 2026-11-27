"""Exact mixed-Colab Qwen page invariants; no evaluation or network."""
import hashlib
from collections import Counter
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
BASE = "0c1dac2f73c758e65e5eaf6336d6c3d4b5cc219f"
PIN = "325c06a54"
SLUG = "qwen2-5-3b-instruct"
LINE = "One day, a young woman named Elara"

def read(p):
    return json.loads((ROOT / p).read_text())

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])

class QwenPage(unittest.TestCase):
    def test_full_map(self):
        m = read("website/src/generated/model-map.json")
        self.assertEqual(m["generated_from"]["models"], 212)
        self.assertEqual(m["generated_from"]["freeflow_docs"], 37820)
        self.assertEqual(set(m["projections"]), {"pca2", "pca3", "mds2", "mds3", "umap2", "umap3"})
        row = next(r for r in m["models"] if r["model"] == SLUG)
        self.assertEqual(row["strapline"], LINE)

    def test_values_preserve_prior_records(self):
        folder = "analysis/values-probe/final/data"
        for p in (ROOT / folder).glob("*.jsonl"):
            rel = str(p.relative_to(ROOT))
            old = [json.loads(x) for x in git("show", BASE + ":" + rel).decode().splitlines() if x.strip()]
            now = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
            key = lambda r: json.dumps(r, sort_keys=True)
            self.assertFalse(Counter(map(key, old)) - Counter(map(key, now)), rel)

    def test_page_and_prior_records(self):
        path = "website/src/generated/models.json"
        old = json.loads(git("show", BASE + ":" + path))
        now = read(path)
        self.assertEqual(len(now), 212)
        self.assertEqual([m for m in now if m["model"] != SLUG], old)
        m = next(m for m in now if m["model"] == SLUG)
        self.assertEqual(m["summary"], LINE)
        self.assertEqual(m["release_date"], "2024-09-19")
        self.assertEqual(m["analyzed_values_samples"], 120)
        self.assertEqual(m["analyzed_freeflow_samples"], 125)
        self.assertIn("v1.2.70", m["notes_markdown"])
        self.assertIn("LONG_10 on one NVIDIA L4", m["notes_markdown"])
        for sid in ("SHORT_11", "VARY_3", "VARY_8", "VARY_14"):
            self.assertIn(sid, m["notes_markdown"])
        for suffix in (".webp", "-thumb.webp"):
            p = f"website/public/images/models/{SLUG}{suffix}"
            self.assertEqual((ROOT / p).read_bytes(), git("show", PIN + ":" + p))

    def test_samples_and_prior_downloads(self):
        samples = read(f"website/public/data/samples/{SLUG}.json")["samples"]
        self.assertEqual(len(samples), 245)
        self.assertEqual(sum(s["type"] == "freeflow" for s in samples), 125)
        for sid in ("SHORT_11", "VARY_3", "VARY_8", "VARY_14"):
            self.assertIn(LINE, next(s["result"] for s in samples if
                                    s["type"] == "freeflow" and s["sample_id"] == sid))
        paths = git("ls-tree", "-r", "--name-only", BASE, "--",
                    "website/public/data", "website/public/downloads").decode().splitlines()
        for p in paths:
            self.assertEqual(hashlib.sha256((ROOT / p).read_bytes()).digest(),
                             hashlib.sha256(git("show", BASE + ":" + p)).digest(), p)

if __name__ == "__main__":
    unittest.main()
