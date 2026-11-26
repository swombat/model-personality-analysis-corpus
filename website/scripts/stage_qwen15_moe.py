#!/usr/bin/env python3
"""Offline, exact-cell staging; preserve all published model/sample records."""
import copy
import json
from pathlib import Path
import subprocess
import generate_data as data

ROOT = Path(__file__).resolve().parents[2]
SLUG = "qwen1-5-moe-a2-7b-chat"
BASE = "e930f41726f5eaa4264b14d358052322ed4c93c5"
PIN = "fa5b220221bdaf2ef56c4d47b68d5d05b0128f72"
GEN = ROOT / "website/src/generated"


def git_json(rev, path):
    return json.loads(subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT))


def update(name, value):
    path = GEN / name
    obj = json.loads(path.read_text())
    obj[SLUG] = value
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


baseline = git_json(BASE, "website/src/generated/models.json")
assert len(baseline) == 197
index_path = ROOT / "analysis/freeflow/personality-model-profiles/index.json"
index = json.loads(index_path.read_text())
if not any(r["model"] == SLUG for r in index):
    index.insert(0, {
        "model": SLUG, "safe": SLUG, "analysis_inputs": 1, "samples": 125,
        "sample_kind_counts": {"GENRE_FICTION": 1, "EXPRESSIVE_FREEFLOW": 13, "GENERIC_ESSAY": 55, "REFUSAL_OR_ROLE_BOUNDARY": 54, "LOW_SIGNAL": 2},
        "profile": f"analysis/freeflow/personality-model-profiles/profiles/{SLUG}.md",
        "card": f"analysis/freeflow/personality-model-cards/cards/{SLUG}.md",
    })
index_path.write_text(json.dumps(index, indent=2) + "\n")
summary = git_json(PIN, "website/src/generated/model-summaries.json")[SLUG]
update("model-summaries.json", summary)
update("model-release-dates.json", "2024-03-28")
update("model-release-date-sources.json", "Qwen official announcement, 'Qwen1.5-MoE: Matching 7B Model Performance with 1/3 Activated Parameters', 2024-03-28: https://qwenlm.github.io/blog/qwen-moe/ . Historical checkpoint release, not November 2026 capture.")
update("model-notes.json", "Historical local-weight capture, not a hosted endpoint: official Qwen/Qwen1.5-MoE-A2.7B-Chat revision ec052fda178e241c7c443468d2fa1db6618996be, BF16, vLLM 0.34.0 on Google Colab (one NVIDIA A100-SXM4-80GB). 125 freeflow responses and 120 values responses, preserved byte-for-byte. Of the 125 BV1-Luna evaluations, 119 use bv1-luna-v1-20260929 and six (MID_9, OPEN_11, OPEN_14, OPEN_20, SHORT_11, SHORT_14) use bv1-luna-v1-targeted-20261016. The targeted variants change the evaluation, not the model responses. [Qwen announced Qwen1.5-MoE on March 28, 2024](https://qwenlm.github.io/blog/qwen-moe/). No verified capability-ladder benchmarks or hosted API prices assigned.\n\nThe strapline describes one prompt family. All 25 VARY responses begin “As I sit here”; all 100 responses to the other four freeflow prompts open by identifying the speaker as an AI.")
cap_path = GEN / "capability-ladder.json"
cap = json.loads(cap_path.read_text())
cap["models"][SLUG] = copy.deepcopy(cap["models"]["gemma-2-2b-it"])
cap_path.write_text(json.dumps(cap, indent=2) + "\n")
for suffix in (".webp", "-thumb.webp"):
    path = f"website/public/images/models/{SLUG}{suffix}"
    (ROOT / path).write_bytes(subprocess.check_output(["git", "show", f"{PIN}:{path}"], cwd=ROOT))
alias = ROOT / "internal/capability-ladder/aliases.tsv"
if not any(line.startswith(SLUG + "\t") for line in alias.read_text().splitlines()):
    with alias.open("a") as f:
        f.write(f"{SLUG}\tQwen1.5 MoE A2.7B Chat\t2024-03-28\t\tnone\t\tnone\t2026-11-26: Historical Colab BF16 checkpoint. No verified per-benchmark measurements imported; unscored.\n")

# Narrow generation avoids missing legacy corpora mutating published records.
data.PROFILE_INDEX = index_path
data.openrouter_for_model = lambda model: None
data.SAMPLE_ROUTING_MODELS = [m["model"] for m in baseline] + [SLUG]
original_samples = data.generate_samples
data.generate_samples = lambda models: original_samples([SLUG])
# main reads only this profile while leaving shared index complete.
temporary = GEN / ".qmoe-profile-index.json"
temporary.write_text(json.dumps([r for r in index if r["model"] == SLUG]))
data.PROFILE_INDEX = temporary
try:
    data.main()
    new = json.loads((GEN / "models.json").read_text())
    assert len(new) == 1 and new[0]["model"] == SLUG
    (GEN / "models.json").write_text(json.dumps(sorted(baseline + new, key=lambda m: (m["lab"], m["model"])), ensure_ascii=False, indent=2))
finally:
    temporary.unlink(missing_ok=True)
