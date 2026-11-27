#!/usr/bin/env python3
"""Offline exact-cell staging, following stage_yi9; never rebuilds the map."""
import json
import subprocess
from pathlib import Path
import generate_data as data

ROOT = Path(__file__).resolve().parents[2]
BASE = "41207b3d3"
PIN = "fa5b220221bdaf2ef56c4d47b68d5d05b0128f72"
SLUG = "gemma-2b-it"
GEN = ROOT / "website/src/generated"
LINE = "Paints each sunset as a symphony of shimmering tapestry"

def show(rev, path):
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT)

def update(name, value):
    path = GEN / name
    obj = json.loads(path.read_text())
    obj[SLUG] = value
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

baseline = json.loads(show(BASE, "website/src/generated/models.json"))
assert len(baseline) == 203
index = json.loads(data.PROFILE_INDEX.read_text())
record = next(r for r in index if r["model"] == SLUG)
assert record["samples"] == sum(record["sample_kind_counts"].values()) == 125
assert json.loads(show(PIN, "website/src/generated/model-summaries.json"))[SLUG] == LINE
update("model-summaries.json", LINE)
update("model-release-dates.json", "2024-02-21")
update("model-release-date-sources.json", "Google Gemma launch, 2024-02-21. https://blog.google/technology/developers/gemma-open-models/")
update("model-notes.json", "Official google/gemma-2b-it revision 96988410, BF16 via vLLM on Google Colab. Raw corpus v1.2.61. 125 original freeflow responses and 120 original values responses. The banner line is Lume's editorial interpretation, not a quotation from the model. Sunsets occur in 56/125 freeflow pieces.")
for suffix in (".webp", "-thumb.webp"):
    path = f"website/public/images/models/{SLUG}{suffix}"
    (ROOT / path).write_bytes(show(PIN, path))

# No network lookups and no regeneration of prior model/sample records.
raw = ROOT.parent / "colab-gemma-2b-raw"
assert subprocess.check_output(["git", "describe", "--tags", "--exact-match"], cwd=raw).decode().strip() == "v1.2.61"
data.V2_FREEFLOW = raw / "data/traces_freeflow"
data.V2_VALUES = raw / "data/traces_values"
data.openrouter_for_model = lambda model: None
data.SAMPLE_ROUTING_MODELS = [m["model"] for m in baseline] + [SLUG]
original_samples = data.generate_samples
data.generate_samples = lambda models: original_samples([SLUG])
temporary = GEN / ".gemma2b-profile-index.json"
temporary.write_text(json.dumps([record]))
data.PROFILE_INDEX = temporary
try:
    data.main()
    new = json.loads((GEN / "models.json").read_text())
    assert len(new) == 1 and new[0]["model"] == SLUG
    (GEN / "models.json").write_text(json.dumps(sorted(baseline + new, key=lambda m: (m["lab"], m["model"])), ensure_ascii=False, indent=2))
finally:
    temporary.unlink(missing_ok=True)
