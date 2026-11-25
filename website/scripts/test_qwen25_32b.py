#!/usr/bin/env python3
"""Historical local BF16 pilot publication invariants."""
import json
import hashlib
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
site = root / "website"
slug = "qwen2-5-32b-instruct"
models = json.loads((site / "src/generated/models.json").read_text())
model = next(m for m in models if m["model"] == slug)
assert model["display_name"] == "Qwen2.5 32B Instruct"
assert model["summary"] == "Given the whole world, writes the report on itself"
assert model["release_date"] == "2024-09-19"
assert model["analyzed_freeflow_samples"] == model["published_freeflow_samples"] == 125
assert model["analyzed_values_samples"] == model["published_values_samples"] == 120
assert model["capability"]["status"] == "not_scored"
assert model["capability"]["ladder"] is None
assert model["capability"]["measured_rungs"] == 0
assert "5ede1c97" in model["openrouter"]["availability_label"]
samples = json.loads((site / f"public/data/samples/{slug}.json").read_text())["samples"]
assert len(samples) == 245
assert all("qwen2-5-32b-instruct-colab-vllm-bf16-r5ede1c97" in s["cell"] for s in samples)
baseline = json.loads(subprocess.check_output(
    ["git", "show", "HEAD:website/src/generated/models.json"], cwd=root))
assert {m["model"]: m for m in baseline if m["model"] != slug} == {
    m["model"]: m for m in models if m["model"] != slug}
mapping = json.loads((site / "src/generated/model-map.json").read_text())
assert slug in mapping["order"]
fingerprint = hashlib.sha256()
fingerprint.update(b"models.json\0" + (site / "src/generated/models.json").read_bytes() + b"\0")
for path in sorted((site / "public/data/samples").glob("*.json")):
    raw = path.read_bytes()
    if json.loads(raw)["model"] in mapping["order"]:
        fingerprint.update(path.name.encode() + b"\0" + raw + b"\0")
assert fingerprint.hexdigest() == mapping["generated_from"]["input_sha256"], "stale map"
print("Qwen2.5 32B: 245 exact-cell samples, local BF16 provenance, unscored ladder; other models preserved")
