#!/usr/bin/env python3
"""Recovered Gemma 2 2B exact-cell release and old-195 preservation."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
site = root / "website"
slug = "gemma-2-2b-it"
pin = "fa5b220221bdaf2ef56c4d47b68d5d05b0128f72"
base = "4e35d4c43095be3ff365adf9132ac4ac527eef94"
models = json.loads((site / "src/generated/models.json").read_text())
model = next(m for m in models if m["model"] == slug)
assert model["display_name"] == "Gemma 2 2B IT"
assert model["summary"] == "Finds a forgotten world in every mote of dust"
assert model["release_date"] == "2024-07-31"
assert model["analyzed_freeflow_samples"] == model["published_freeflow_samples"] == 125
assert model["analyzed_values_samples"] == model["published_values_samples"] == 120
assert model["capability"]["status"] == "not_scored"
assert model["capability"]["ladder"] is None
assert model["capability"]["measured_rungs"] == 0
assert "299a8560" in model["openrouter"]["availability_label"]
assert "L4" in model["notes_markdown"]
samples = json.loads((site / f"public/data/samples/{slug}.json").read_text())["samples"]
assert len(samples) == 245
assert all("gemma-2-2b-it-colab-vllm-bf16-r299a8560" in s["cell"] for s in samples)
baseline = json.loads(subprocess.check_output(
    ["git", "show", f"{base}:website/src/generated/models.json"], cwd=root))
assert len(baseline) == 195
assert {m["model"]: m for m in baseline} == {
    m["model"]: m for m in models if m["model"] != slug}
for old in baseline:
    path = f"website/public/data/samples/{old['model']}.json"
    assert (root / path).read_bytes() == subprocess.check_output(
        ["git", "show", f"{base}:{path}"], cwd=root), path
for suffix in (".webp", "-thumb.webp"):
    path = f"website/public/images/models/{slug}{suffix}"
    assert (root / path).read_bytes() == subprocess.check_output(
        ["git", "show", f"{pin}:{path}"], cwd=root)
mapping = json.loads((site / "src/generated/model-map.json").read_text())
assert len(mapping["order"]) == 196
assert slug in mapping["order"]
assert next(m for m in mapping["models"] if m["model"] == slug)["strapline"] == model["summary"]
fingerprint = hashlib.sha256()
fingerprint.update(b"models.json\0" + (site / "src/generated/models.json").read_bytes() + b"\0")
for path in sorted((site / "public/data/samples").glob("*.json")):
    raw = path.read_bytes()
    if json.loads(raw)["model"] in mapping["order"]:
        fingerprint.update(path.name.encode() + b"\0" + raw + b"\0")
assert fingerprint.hexdigest() == mapping["generated_from"]["input_sha256"], "stale map"
print("Gemma 2 2B: 245 exact-cell samples; pinned editorial; prior 195 models and sample exports unchanged")
