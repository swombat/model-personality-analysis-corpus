#!/usr/bin/env python3
"""Offline publication custody and exact raw-export checks."""
import collections
import json
from pathlib import Path
import subprocess
import generate_data as data

ROOT = Path(__file__).resolve().parents[2]
BASE = "41207b3d3"
SLUG = "gemma-2b-it"
PIN = "fa5b220221bdaf2ef56c4d47b68d5d05b0128f72"
def show(rev, path):
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT)
def load(path):
    return json.loads((ROOT / path).read_text())

base = json.loads(show(BASE, "website/src/generated/models.json"))
models = load("website/src/generated/models.json")
assert len(base) == 203 and len(models) == 204
assert {m["model"]: m for m in models if m["model"] != SLUG} == {m["model"]: m for m in base}
m = next(m for m in models if m["model"] == SLUG)
assert m["display_name"] == "Gemma 2B IT"
assert m["summary"] == "Paints each sunset as a symphony of shimmering tapestry"
assert "Lume" in m["notes_markdown"] and "not a quotation" in m["notes_markdown"]
assert "56/125" in m["notes_markdown"] and "v1.2.61" in m["notes_markdown"]
assert (m["analyzed_freeflow_samples"], m["analyzed_values_samples"]) == (125, 120)
assert (m["published_samples"], m["published_freeflow_samples"], m["published_values_samples"]) == (245, 125, 120)
for key in ("personality_profile_markdown", "personality_card_markdown", "values_summary_markdown", "values_details_markdown"):
    assert len(m[key]) > 500, key
for key, suffix in (("image", ".webp"), ("image_thumb", "-thumb.webp")):
    assert m[key] == f"images/models/{SLUG}{suffix}"
    path = f"website/public/{m[key]}"
    assert (ROOT / path).read_bytes() == show(PIN, path)
samples = load(f"website/public/data/samples/{SLUG}.json")["samples"]
assert collections.Counter(s["type"] for s in samples) == {"freeflow": 125, "values": 120}
assert len({(s["type"], s["sample_id"]) for s in samples}) == 245
raw = ROOT.parent / "colab-gemma-2b-raw"
cell = SLUG + "-colab-vllm-bf16-r96988410"
expected = []
for kind in ("freeflow", "values"):
    cell = ("freeflow_" if kind == "freeflow" else "") + SLUG + "-colab-vllm-bf16-r96988410"
    files = sorted((raw / f"data/traces_{kind}" / cell).glob("*.json"))
    assert len(files) == (125 if kind == "freeflow" else 120)
    expected.extend(data.sample_record(f, kind, "v2", cell) for f in files)
assert sorted(samples, key=lambda s: (s["type"], s["sample_id"])) == sorted(expected, key=lambda s: (s["type"], s["sample_id"]))
# 56/125 is the supplied reviewed editorial motif count, not a lexical count.
assert sum("sunset" in s["result"].lower() for s in samples if s["type"] == "freeflow") == 25
for name in ("model-notes.json", "model-summaries.json", "model-release-dates.json", "model-release-date-sources.json"):
    path = "website/src/generated/" + name
    current = load(path)
    del current[SLUG]
    assert current == json.loads(show(BASE, path)), name
paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE, "--",
    "analysis", "website/public/data", "website/public/downloads",
    "website/src/generated/model-map.json", "website/src/generated/capability-ladder.json"], cwd=ROOT).decode().splitlines()
changed = set(subprocess.check_output(["git", "diff", "--name-only", BASE], cwd=ROOT).decode().splitlines()) & set(paths)
assert not changed, changed
print(f"PASS: 203 prior records and {len(paths)} prior analysis/export/map/capability files unchanged; reviewed images, real analysis, exact raw 125+120. Reviewed motif count 56/125 retained; literal sunset(s) occurs in 25/125.")
