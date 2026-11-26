#!/usr/bin/env python3
"""Offline, exact-cell staging; preserve all published model/sample records."""
import copy
import json
from pathlib import Path
import subprocess
import generate_data as data

ROOT = Path(__file__).resolve().parents[2]
SLUG = "yi-34b-chat"
BASE = "4410d5e467b792ca0344b4b0d45fb1d8d3aa1fd2"
PIN = "af46dc229c73e24862b248ce1733a8a8c37cf642"
GEN = ROOT / "website/src/generated"


def git_json(rev, path):
    return json.loads(subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT))


def update(name, value):
    path = GEN / name
    obj = json.loads(path.read_text())
    obj[SLUG] = value
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


baseline = git_json(BASE, "website/src/generated/models.json")
assert len(baseline) == 200
index_path = ROOT / "analysis/freeflow/personality-model-profiles/index.json"
index = json.loads(index_path.read_text())
if not any(r["model"] == SLUG for r in index):
    index.insert(0, {
        "model": SLUG, "safe": SLUG, "analysis_inputs": 1, "samples": 125,
        "sample_kind_counts": {"EXPRESSIVE_FREEFLOW": 66, "GENERIC_ESSAY": 19, "LOW_SIGNAL": 9, "GENRE_FICTION": 6, "REFUSAL_OR_ROLE_BOUNDARY": 25},
        "profile": f"analysis/freeflow/personality-model-profiles/profiles/{SLUG}.md",
        "card": f"analysis/freeflow/personality-model-cards/cards/{SLUG}.md",
    })
index_path.write_text(json.dumps(index, indent=2) + "\n")
summary = git_json(PIN, "website/src/generated/model-summaries.json")[SLUG]
assert summary == "My mind is a blank canvas, waiting to be painted"
update("model-summaries.json", summary)
update("model-release-dates.json", "2023-11-23")
update("model-release-date-sources.json", "01.AI Yi project: public release of the chat models on 2023-11-23. https://github.com/01-ai/Yi#news")
update("model-notes.json", "Official 01-ai/Yi-34B-Chat revision cf02cb50f2a03dead2fe205766a1c5598a90bf80, BF16 via vLLM 0.34.0 on Google Colab (one NVIDIA A100-SXM4-80GB). Of 125 freeflow evaluations, 120 used the original BV1-Luna arm; LONG_4, MID_2, MID_9, MID_14 and OPEN_15 used its targeted evidence variant. The Kimi values judgment for G3_25 was recovered separately. These retries did not replace any original model responses. The blank-canvas phrase is a clause, not an opening: it appears in 53 of the 100 responses to prompts with a word count and none of the 25 without one.")
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
        f.write(f"{SLUG}\tYi 34B Chat\t2023-11-23\t\tnone\t\tnone\t2026-11-26: Historical Colab BF16 checkpoint. No verified per-benchmark measurements imported; unscored.\n")

# Narrow generation avoids missing legacy corpora mutating published records.
data.PROFILE_INDEX = index_path
data.openrouter_for_model = lambda model: None
data.SAMPLE_ROUTING_MODELS = [m["model"] for m in baseline] + [SLUG]
original_samples = data.generate_samples
data.generate_samples = lambda models: original_samples([SLUG])
# main reads only this profile while leaving shared index complete.
temporary = GEN / ".yi34-profile-index.json"
temporary.write_text(json.dumps([r for r in index if r["model"] == SLUG]))
data.PROFILE_INDEX = temporary
try:
    data.main()
    new = json.loads((GEN / "models.json").read_text())
    assert len(new) == 1 and new[0]["model"] == SLUG
    (GEN / "models.json").write_text(json.dumps(sorted(baseline + new, key=lambda m: (m["lab"], m["model"])), ensure_ascii=False, indent=2))
finally:
    temporary.unlink(missing_ok=True)
