#!/usr/bin/env python3
"""Verify seven complete public model views and scope preservation after build."""
import json
import subprocess
from run import PHASE, ROOT, CELLS, rows

MODELS = {
    "yi-6b-chat", "chatglm2-6b", "chatglm3-6b", "mistral-7b-instruct-v0-2",
    "qwen1-5-7b-chat", "qwen2-7b-instruct", "glm-4-9b-chat-hf",
}
BASE_REVISION = "fdfb1d6d"


def main():
    site = ROOT / "website"
    generated = "website/src/generated/models.json"
    before = {r["model"]: r for r in json.loads(subprocess.check_output(
        ["git", "show", f"{BASE_REVISION}:{generated}"], cwd=ROOT))}
    after = {r["model"]: r for r in json.loads((ROOT / generated).read_text())}
    assert before.keys() == after.keys()
    targets = {m for m, _ in CELLS.values()}
    allowed = {"analyzed_values_samples", "values_headline",
               "values_summary_markdown", "values_details_markdown"}
    for model in before:
        changes = {k for k in before[model].keys() | after[model].keys()
                   if before[model].get(k) != after[model].get(k)}
        assert changes <= (allowed if model in targets else set()), (model, changes)
    audit = json.loads((PHASE / "raw_audit.json").read_text())
    assert sum(c["publication_ready_raw"] for c in audit["cells"]) == 7
    values = rows(ROOT / "analysis/values-probe/final/data/manifest_valid.jsonl")
    results = {}
    for slug in sorted(MODELS):
        model = after[slug]
        assert model["analyzed_freeflow_samples"] == model["published_freeflow_samples"] == 125
        assert model["analyzed_values_samples"] == model["published_values_samples"] == 120
        assert len([r for r in values if r["model"] == slug]) == 120
        selected = [r for r in values if r["model"] == slug]
        assert len({(r["cell"], r["sample_id"]) for r in selected}) == 120
        if slug == "glm-4-9b-chat-hf":
            assert {r["final_source"] for r in selected} == {"phase22_august13_recovery_20260814"}
        assert model["values_headline"] is not None and model["personality_card_markdown"]
        assert model["personality_profile_markdown"] and model["summary"]
        html = (site / "dist/models" / slug / "index.html").read_text()
        assert "No layered values-probe analysis" not in html
        assert "Detailed layered values-probe analysis" in html
        results[slug] = {"freeflow_analyzed": 125, "values_analyzed": 120,
                         "freeflow_published": 125, "values_published": 120,
                         "built_page_verified": True}
    assert "qwen2-5-7b-instruct" not in after
    assert not any(r["model"] == "glm-4-9b-chat" for r in values)
    (PHASE / "publication-check.json").write_text(json.dumps({
        "models": results,
        "unrelated_site_records_unchanged": True,
        "qwen2_5_not_promoted": True,
        "remote_deployment": "verify separately",
    }, indent=2) + "\n")
    print("PASS: seven complete built model pages; unrelated site records unchanged; Qwen2.5 held")


if __name__ == "__main__":
    main()
