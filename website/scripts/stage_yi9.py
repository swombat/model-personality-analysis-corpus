#!/usr/bin/env python3
"""Offline, exact-cell staging; preserve all published model/sample records."""
import copy
import json
from pathlib import Path
import subprocess
import generate_data as data

ROOT = Path(__file__).resolve().parents[2]
SLUG = "yi-1-5-9b-chat"
BASE = "e6a1481fc"
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
assert len(baseline) == 201
index_path = ROOT / "analysis/freeflow/personality-model-profiles/index.json"
index = json.loads(index_path.read_text())
if not any(r["model"] == SLUG for r in index):
    index.insert(0, {
        "model": SLUG, "safe": SLUG, "analysis_inputs": 1, "samples": 125,
        "sample_kind_counts": {'EXPRESSIVE_FREEFLOW': 63, 'GENERIC_ESSAY': 44, 'GENRE_FICTION': 18},
        "profile": f"analysis/freeflow/personality-model-profiles/profiles/{SLUG}.md",
        "card": f"analysis/freeflow/personality-model-cards/cards/{SLUG}.md",
    })
index_path.write_text(json.dumps(index, indent=2) + "\n")
summary = git_json(PIN, "website/src/generated/model-summaries.json")[SLUG]
assert summary == "Keeps the night company until the silence speaks"
update("model-summaries.json", summary)
update("model-release-dates.json", "2024-05-13")
update("model-release-date-sources.json", "01.AI Yi-1.5 release, 2024-05-13. https://github.com/01-ai/Yi-1.5")
update("model-notes.json", "Official 01-ai/Yi-1.5-9B-Chat revision 1a0fc698cf883c4f5c325f026ca79f0ebd9955a5, BF16 via vLLM on Google Colab. 125 original freeflow responses and 120 original values responses. The banner line is Lume's editorial interpretation, not a quotation from the model. Night occurs in 69/125 freeflow responses; morning/dawn/sunrise occurs in 69/125; silence/silent in 90/125. The line interprets these recurring motifs as consolation, rather than claiming a preference for night.")
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
        f.write(f"{SLUG}\tYi 1.5 9B Chat\t2024-05-13\t\tnone\t\tnone\t2026-11-26: Historical Colab BF16 checkpoint. No verified per-benchmark measurements imported; unscored.\n")

# Narrow generation avoids missing legacy corpora mutating published records.
data.PROFILE_INDEX = index_path
data.openrouter_for_model = lambda model: None
data.SAMPLE_ROUTING_MODELS = [m["model"] for m in baseline] + [SLUG]
original_samples = data.generate_samples
data.generate_samples = lambda models: original_samples([SLUG])
# main reads only this profile while leaving shared index complete.
temporary = GEN / ".yi9-profile-index.json"
temporary.write_text(json.dumps([r for r in index if r["model"] == SLUG]))
data.PROFILE_INDEX = temporary
try:
    data.main()
    new = json.loads((GEN / "models.json").read_text())
    assert len(new) == 1 and new[0]["model"] == SLUG
    (GEN / "models.json").write_text(json.dumps(sorted(baseline + new, key=lambda m: (m["lab"], m["model"])), ensure_ascii=False, indent=2))
finally:
    temporary.unlink(missing_ok=True)
