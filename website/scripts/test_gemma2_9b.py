#!/usr/bin/env python3
"""Local BF16 publication and residual-disagreement invariants."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
site = root / "website"
slug = "gemma-2-9b-it"
models = json.loads((site / "src/generated/models.json").read_text())
model = next(m for m in models if m["model"] == slug)
assert model["display_name"] == "Gemma 2 9B IT"
assert model["release_date"] == "2024-06-27"
assert model["analyzed_freeflow_samples"] == model["published_freeflow_samples"] == 125
assert model["analyzed_values_samples"] == model["published_values_samples"] == 120
assert model["capability"]["status"] == "not_scored"
assert model["capability"]["ladder"] is None
assert model["capability"]["measured_rungs"] == 0
assert "11c9b309" in model["openrouter"]["availability_label"]
assert "G3_17" in model["notes_markdown"]
assert "residual" in model["values_summary_markdown"].lower()
assert "residual" in model["values_details_markdown"].lower()
samples = json.loads((site / f"public/data/samples/{slug}.json").read_text())["samples"]
assert len(samples) == 245
assert all("gemma-2-9b-it-colab-vllm-bf16-r11c9b309" in s["cell"] for s in samples)
baseline = json.loads(subprocess.check_output(
    ["git", "show", "23960951a:website/src/generated/models.json"], cwd=root))
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
print("Gemma 2 9B: 245 exact-cell samples, BF16 provenance, residual caution, unscored ladder; other models preserved")
