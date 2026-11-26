#!/usr/bin/env python3
"""Exact-cell Qwen14 staging; optional final map verification."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--with-map", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
site = root / "website"
slug = "gemma-7b-it"
base = "17d4b64f2d3c9985e64ae31f72a8ff3603057b70"
pin = "af46dc229c73e24862b248ce1733a8a8c37cf642"

def git_json(rev, path):
    return json.loads(subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=root))

models = json.loads((site / "src/generated/models.json").read_text())
model = next(m for m in models if m["model"] == slug)
assert len(models) == 200
assert model["display_name"] == "Gemma 7B IT"
assert model["summary"] == git_json(pin, "website/src/generated/model-summaries.json")[slug].split(",")[0]
assert model["release_date"] == "2024-02-21"
assert model["analyzed_freeflow_samples"] == model["published_freeflow_samples"] == 125
assert model["analyzed_values_samples"] == model["published_values_samples"] == 120
assert model["capability"]["status"] == "not_scored"
assert model["capability"]["ladder"] is None
assert model["capability"]["measured_rungs"] == 0
assert "9c5798d2" in model["openrouter"]["availability_label"]
assert "L4" in model["notes_markdown"]
assert "123" in model["notes_markdown"] and "G1_27" in model["notes_markdown"]
samples = json.loads((site / f"public/data/samples/{slug}.json").read_text())["samples"]
assert len(samples) == 245
assert all("gemma-7b-it-colab-vllm-bf16-r9c5798d2" in s["cell"] for s in samples)
baseline = git_json(base, "website/src/generated/models.json")
assert len(baseline) == 199
assert {m["model"]: m for m in baseline} == {m["model"]: m for m in models if m["model"] != slug}
for old in baseline:
    path = f"website/public/data/samples/{old['model']}.json"
    assert (root / path).read_bytes() == subprocess.check_output(["git", "show", f"{base}:{path}"], cwd=root), path
for suffix in (".webp", "-thumb.webp"):
    path = f"website/public/images/models/{slug}{suffix}"
    assert (root / path).read_bytes() == subprocess.check_output(["git", "show", f"{pin}:{path}"], cwd=root)
if args.with_map:
    mapping = json.loads((site / "src/generated/model-map.json").read_text())
    assert len(mapping["order"]) == 200 and slug in mapping["order"]
    assert next(m for m in mapping["models"] if m["model"] == slug)["strapline"] == model["summary"]
    fingerprint = hashlib.sha256()
    fingerprint.update(b"models.json\0" + (site / "src/generated/models.json").read_bytes() + b"\0")
    for path in sorted((site / "public/data/samples").glob("*.json")):
        raw = path.read_bytes()
        if json.loads(raw)["model"] in mapping["order"]:
            fingerprint.update(path.name.encode() + b"\0" + raw + b"\0")
    assert fingerprint.hexdigest() == mapping["generated_from"]["input_sha256"], "stale map"
print("Gemma 7B IT: 245 exact-cell samples; pinned editorial; previous 199 models and sample exports unchanged")
