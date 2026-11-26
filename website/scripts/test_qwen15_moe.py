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
slug = "qwen1-5-moe-a2-7b-chat"
base = "e930f41726f5eaa4264b14d358052322ed4c93c5"
pin = "fa5b220221bdaf2ef56c4d47b68d5d05b0128f72"

def git_json(rev, path):
    return json.loads(subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=root))

models = json.loads((site / "src/generated/models.json").read_text())
model = next(m for m in models if m["model"] == slug)
assert len(models) == 198
assert model["display_name"] == "Qwen1.5 MoE A2.7B Chat"
assert model["summary"] == git_json(pin, "website/src/generated/model-summaries.json")[slug]
assert model["release_date"] == "2024-03-28"
assert model["analyzed_freeflow_samples"] == model["published_freeflow_samples"] == 125
assert model["analyzed_values_samples"] == model["published_values_samples"] == 120
assert model["capability"]["status"] == "not_scored"
assert model["capability"]["ladder"] is None
assert model["capability"]["measured_rungs"] == 0
assert "ec052fda" in model["openrouter"]["availability_label"]
assert "A100-SXM4-80GB" in model["notes_markdown"]
assert "119" in model["notes_markdown"] and "six" in model["notes_markdown"]
samples = json.loads((site / f"public/data/samples/{slug}.json").read_text())["samples"]
assert len(samples) == 245
assert all("qwen1-5-moe-a2-7b-chat-colab-vllm-bf16-rec052fda" in s["cell"] for s in samples)
baseline = git_json(base, "website/src/generated/models.json")
assert len(baseline) == 197
assert {m["model"]: m for m in baseline} == {m["model"]: m for m in models if m["model"] != slug}
for old in baseline:
    path = f"website/public/data/samples/{old['model']}.json"
    assert (root / path).read_bytes() == subprocess.check_output(["git", "show", f"{base}:{path}"], cwd=root), path
for suffix in (".webp", "-thumb.webp"):
    path = f"website/public/images/models/{slug}{suffix}"
    assert (root / path).read_bytes() == subprocess.check_output(["git", "show", f"{pin}:{path}"], cwd=root)
if args.with_map:
    mapping = json.loads((site / "src/generated/model-map.json").read_text())
    assert len(mapping["order"]) == 198 and slug in mapping["order"]
    assert next(m for m in mapping["models"] if m["model"] == slug)["strapline"] == model["summary"]
    fingerprint = hashlib.sha256()
    fingerprint.update(b"models.json\0" + (site / "src/generated/models.json").read_bytes() + b"\0")
    for path in sorted((site / "public/data/samples").glob("*.json")):
        raw = path.read_bytes()
        if json.loads(raw)["model"] in mapping["order"]:
            fingerprint.update(path.name.encode() + b"\0" + raw + b"\0")
    assert fingerprint.hexdigest() == mapping["generated_from"]["input_sha256"], "stale map"
print("Qwen1.5 MoE: 245 exact-cell samples; pinned editorial; previous 197 models and sample exports unchanged")
