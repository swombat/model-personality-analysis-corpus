#!/usr/bin/env python3
"""Exact-cell Phi medium publication invariants and prior-record preservation."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
site = root / "website"
slug = "phi-3-medium-4k-instruct"
cell = slug + "-colab-vllm-bf16-r48d87cd5"
models = json.loads((site / "src/generated/models.json").read_text())
model = next(m for m in models if m["model"] == slug)
assert model["display_name"] == "Phi-3 Medium 4K Instruct"
assert model["summary"] == "Give it room and it files a titled magazine feature"
assert model["release_date"] == "2024-05-21"
assert model["analyzed_freeflow_samples"] == model["published_freeflow_samples"] == 125
assert model["analyzed_values_samples"] == model["published_values_samples"] == 120
assert model["capability"]["status"] == "not_scored"
assert model["capability"]["ladder"] is None
assert model["capability"]["measured_rungs"] == 0
assert "48d87cd5" in model["openrouter"]["availability_label"]
assert "A100" in model["notes_markdown"]
assert "G3_30" in model["notes_markdown"]
samples = json.loads((site / f"public/data/samples/{slug}.json").read_text())["samples"]
assert len(samples) == 245
assert all(cell in s["cell"] for s in samples)
baseline = json.loads(subprocess.check_output(
    ["git", "show", "be1a4e926:website/src/generated/models.json"], cwd=root))
assert {m["model"]: m for m in baseline} == {
    m["model"]: m for m in models if m["model"] != slug}
pin = "fa5b220221bdaf2ef56c4d47b68d5d05b0128f72"
for suffix in (".webp", "-thumb.webp"):
    path = f"website/public/images/models/{slug}{suffix}"
    assert (root/path).read_bytes() == subprocess.check_output(["git","show",f"{pin}:{path}"],cwd=root)
mapping = json.loads((site / "src/generated/model-map.json").read_text())
assert slug in mapping["order"]
assert next(m for m in mapping["models"] if m["model"] == slug)["strapline"] == model["summary"]
fingerprint = hashlib.sha256()
fingerprint.update(b"models.json\0" + (site / "src/generated/models.json").read_bytes() + b"\0")
for path in sorted((site / "public/data/samples").glob("*.json")):
    raw = path.read_bytes()
    if json.loads(raw)["model"] in mapping["order"]:
        fingerprint.update(path.name.encode() + b"\0" + raw + b"\0")
assert fingerprint.hexdigest() == mapping["generated_from"]["input_sha256"], "stale map"
print("Phi medium: 245 exact-cell samples, pinned editorial, verified metadata, unscored capability; prior records unchanged")
