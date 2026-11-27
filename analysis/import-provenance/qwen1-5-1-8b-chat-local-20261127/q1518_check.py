"""Independent offline import checks, including adopted-generation bindings."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path("/home/agent/work/colab-q1518-site")
prov = root / "analysis/import-provenance/qwen1-5-1-8b-chat-local-20261127"
phase = root / "analysis/values-probe/model-coding/layered/capture_qwen18_final_20261127"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
v = load(prov / "validation.json")
assert v["bv1"] == 125 and v["values"] == 120
for item in v["copied_files"]:
    assert sha(root / item["destination"]) == item["sha256"]
    assert sha(item["source"]) == item["sha256"]
for probe, count in (("freeflow", 125), ("values", 120)):
    rows = [r for r in v["canonical_raw_sources"] if r["probe"] == probe]
    assert len(rows) == len({r["sample"] for r in rows}) == count
    assert all(sha(r["source"]) == r["sha256"] for r in rows)
assert len((phase / "manifest.jsonl").read_text().splitlines()) == 120
for folder in ("layer_a", "posture_collapsed", "posture_final"):
    for p in (phase / folder).glob("*.jsonl"):
        assert len(p.read_text().splitlines()) == 120, p
assert len(v["canonical_readings"]) == 125
for sid, arm in (("MID_15", "bv1-luna-v1-20260929"), ("OPEN_8", "bv1-luna-v1-targeted-20261016")):
    binding = load(phase / "bv1_bindings_v13_revalidation" / (sid + ".json"))
    assert binding["evaluator_arm"] == arm and binding["revalidation_pass"]
    assert sha(prov / "canonical-readings" / (sid + ".md")) == binding["output_sha256"]
    matches = [p for p in phase.rglob("*.json") if "attempt_responses" in p.parts and sha(p) == binding["generation_attempt_sha256"]]
    assert len(matches) == 1 and sha(matches[0]) == binding["generation_attempt_sha256"]
    attempt = load(matches[0])
    assert attempt["arm"] == arm
    assert attempt["response"]["choices"][0]["message"]["content"] == (prov / "canonical-readings" / (sid + ".md")).read_text()
for item in v["append_only_jsonl"]:
    p = root / item["path"]
    base = subprocess.check_output(["git", "-C", str(root), "show", v["base"] + ":" + item["path"]])
    assert hashlib.sha256(base).hexdigest() == item["prior_sha256"]
    assert p.read_bytes().startswith(base) and sha(p) == item["sha256"]
    assert len(p.read_text().splitlines()) - len(base.splitlines()) == item["added_rows"]
for rel in ("analysis/freeflow/personality-model-profiles/index.json", "analysis/values-probe/final/capture_sources.json"):
    before = json.loads(subprocess.check_output(["git", "-C", str(root), "show", v["base"] + ":" + rel]))
    after = load(root / rel)
    assert after[:-1] == before
paths = subprocess.check_output(["git", "-C", str(root), "diff", "--name-only", "HEAD"], text=True).splitlines()
assert all(p.startswith("analysis/") for p in paths)
assert not subprocess.check_output(["git", "-C", str(root), "diff", "HEAD", "--", "website"])
print(f"PASS: {len(v['copied_files'])} source/destination hashes; 125+120 canonical; both offline bindings; coding counts; append-only shared data; website unchanged.")
