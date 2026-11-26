#!/usr/bin/env python3
"""Offline, exact-cell staging; preserve all published model/sample records."""
import copy
import json
from pathlib import Path
import subprocess
import generate_data as data

ROOT = Path(__file__).resolve().parents[2]
SLUG = "gemma-7b-it"
BASE = "17d4b64f2d3c9985e64ae31f72a8ff3603057b70"
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
assert len(baseline) == 199
index_path = ROOT / "analysis/freeflow/personality-model-profiles/index.json"
index = json.loads(index_path.read_text())
if not any(r["model"] == SLUG for r in index):
    index.insert(0, {
        "model": SLUG, "safe": SLUG, "analysis_inputs": 1, "samples": 125,
        "sample_kind_counts": {"GENRE_FICTION": 92, "EXPRESSIVE_FREEFLOW": 23, "GENERIC_ESSAY": 10},
        "profile": f"analysis/freeflow/personality-model-profiles/profiles/{SLUG}.md",
        "card": f"analysis/freeflow/personality-model-cards/cards/{SLUG}.md",
    })
index_path.write_text(json.dumps(index, indent=2) + "\n")
summary = git_json(PIN, "website/src/generated/model-summaries.json")[SLUG]
assert summary == "In the quaint town of Willow Creek, nestled amidst whispering willows"
update("model-summaries.json", summary.split(",")[0])
update("model-release-dates.json", "2024-02-21")
update("model-release-date-sources.json", "Google: Gemma open models announcement, 2024-02-21. https://blog.google/technology/developers/gemma-open-models/")
update("model-notes.json", "Official google/gemma-7b-it revision 9c5798d27f588501ce1e108079d2a19e4c3a2353, BF16 via vLLM 0.34.0 on Google Colab (one NVIDIA L4). Of 125 freeflow evaluations, 123 used the original BV1-Luna arm; MID_5 and VARY_9 used its targeted evidence variant. The GLM values judgment for G1_27 was recovered separately. These retries evaluated the original responses; they did not replace them. Among the 125 freeflow responses, 30 open in the quaint town or village of Willow Creek. The strapline is the exact opening of 11.")
notes = json.loads((GEN / "model-notes.json").read_text())[SLUG]
update("model-notes.json", notes.replace("The strapline is the exact opening of 11.", f'Eleven begin with the longer phrase “{summary}”.'))
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
        f.write(f"{SLUG}\tGemma 7B IT\t2024-02-21\t\tnone\t\tnone\t2026-11-26: Historical Colab BF16 checkpoint. No verified per-benchmark measurements imported; unscored.\n")

# Narrow generation avoids missing legacy corpora mutating published records.
data.PROFILE_INDEX = index_path
data.openrouter_for_model = lambda model: None
data.SAMPLE_ROUTING_MODELS = [m["model"] for m in baseline] + [SLUG]
original_samples = data.generate_samples
data.generate_samples = lambda models: original_samples([SLUG])
# main reads only this profile while leaving shared index complete.
temporary = GEN / ".g7-profile-index.json"
temporary.write_text(json.dumps([r for r in index if r["model"] == SLUG]))
data.PROFILE_INDEX = temporary
try:
    data.main()
    new = json.loads((GEN / "models.json").read_text())
    assert len(new) == 1 and new[0]["model"] == SLUG
    (GEN / "models.json").write_text(json.dumps(sorted(baseline + new, key=lambda m: (m["lab"], m["model"])), ensure_ascii=False, indent=2))
finally:
    temporary.unlink(missing_ok=True)
