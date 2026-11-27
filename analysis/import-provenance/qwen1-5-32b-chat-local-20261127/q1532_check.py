"""Independent offline import and provenance checks; no evaluator calls."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path("/home/agent/work/colab-q1532-analysis")
prov = root / "analysis/import-provenance/qwen1-5-32b-chat-local-20261127"
phase = root / "analysis/values-probe/model-coding/layered/capture_qwen32_final_20261127"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
v = load(prov / "validation.json")
assert v["base"] == "7b389986fffa3fe59b6c4436b7267c1adc4e9e69"
assert v["bv1"] == 125 and v["values"] == 120
for item in v["copied_files"]:
    assert sha(root / item["destination"]) == sha(item["source"]) == item["sha256"]
for probe, count in (("freeflow", 125), ("values", 120)):
    rows = [r for r in v["canonical_raw_sources"] if r["probe"] == probe]
    assert len(rows) == len({r["sample"] for r in rows}) == count
    assert all(sha(r["source"]) == r["sha256"] for r in rows)
assert len((phase / "manifest.jsonl").read_text().splitlines()) == 120
for folder in ("layer_a", "posture_collapsed", "posture_final"):
    for p in (phase / folder).glob("*.jsonl"):
        assert len(p.read_text().splitlines()) == 120, p
evidence = {r["sample"]: r for r in v["canonical_readings"]}
assert len(evidence) == 125
six = load(prov / "history/continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127/terminal.json")["adopted"]
assert {r["job"].split("/")[-1] for r in six} == {"MID_7", "MID_9", "MID_19", "MID_23", "LONG_5", "LONG_21"}
bindings = [load(phase / "bv1_bindings_v13_revalidation/LONG_2.json")] + six
attempts = [p for p in phase.rglob("*.json") if "attempt_responses" in p.parts]
by_sha = {sha(p): p for p in attempts}
for b in bindings:
    sid = b.get("job", "LONG_2").split("/")[-1]
    assert b["evaluator_arm"] == "bv1-luna-v1-20260929" and b["revalidation_pass"]
    assert sha(prov / "canonical-readings" / (sid + ".md")) == b["output_sha256"] == evidence[sid]["output_sha256"]
    attempt = load(by_sha[b["generation_attempt_sha256"]])
    assert attempt["arm"] == b["evaluator_arm"]
    assert attempt["response"]["choices"][0]["message"]["content"] == (prov / "canonical-readings" / (sid + ".md")).read_text()
for sid in ("MID_2", "MID_22", "SHORT_14"):
    row = evidence[sid]
    assert row["generation_arm"] == "bv1-luna-v1-targeted-20261016"
    assert not row["separate_v13_revalidation"]
    text = Path(row["output"]).read_text()
    binding = load(phase / "bv1_bindings_luna_v1_targeted" / (sid + ".json"))
    assert binding["output_sha256"] == row["output_sha256"]
    assert binding["source_sha256"] == row["source_sha256"]
    # Targeted runner writes response.strip() + newline as its canonical output.
    assert any(load(p)["arm"] == row["generation_arm"] and load(p)["response"]["choices"][0]["message"]["content"].strip() + "\n" == text for p in attempts if p.parent.name.endswith("_BV1_" + sid))
shared = {r["path"]: r for r in v["append_only_jsonl"]}
indices = {"analysis/freeflow/personality-model-profiles/index.json", "analysis/values-probe/final/capture_sources.json"}
changed = subprocess.check_output(["git", "-C", str(root), "diff", v["base"], "--name-only"], text=True).splitlines()
assert all(rel.startswith("analysis/") for rel in changed)
assert not subprocess.check_output(["git", "-C", str(root), "diff", v["base"], "--diff-filter=DR", "--name-only"])
modified = subprocess.check_output(["git", "-C", str(root), "diff", v["base"], "--diff-filter=M", "--name-only"], text=True).splitlines()
for rel in modified:
    assert rel.startswith("analysis/")
    # Every pre-existing tracked record must be identical except append-only files.
    before = subprocess.check_output(["git", "-C", str(root), "show", v["base"] + ":" + rel])
    after = (root / rel).read_bytes()
    if rel in shared:
        item = shared[rel]
        assert hashlib.sha256(before).hexdigest() == item["prior_sha256"]
        assert after.startswith(before) and sha(root / rel) == item["sha256"]
        assert len(after.splitlines()) - len(before.splitlines()) == item["added_rows"]
    elif rel in indices:
        assert json.loads(after)[:-1] == json.loads(before)
    else:
        assert before == after, rel
assert not subprocess.check_output(["git", "-C", str(root), "diff", v["base"], "--", "website"])
result = dict(status="PASS", copied_files=len(v["copied_files"]), canonical_bv1=125, canonical_values=120,
              separate_original_readings=7, offline_six=6, targeted_passes=3,
              earlier_records_unchanged=True, website_unchanged=True, model_calls=0, remote_writes=False)
(prov / "check-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
