"""Offline-only, append-only Qwen2 1.5B import; no provider modules."""
from pathlib import Path
import hashlib
import json
import sqlite3
import subprocess

R = Path("/home/agent/work/colab-batch-queue")
L = R / "qwen2_final_20261127b"
S = L / "analysis"
T = Path("/home/agent/work/colab-q2-15-site")
P = T / "analysis/import-provenance/qwen2-1-5b-instruct-local-20261127"
slug = "qwen2-1-5b-instruct"
inventory = []

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    return json.loads(Path(p).read_text())

def put(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

def copy(p, dest):
    assert p.is_file() and not p.is_symlink(), p
    if dest.exists():
        assert dest.read_bytes() == p.read_bytes(), dest
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(p.read_bytes())
    inventory.append(dict(source=str(p), destination=str(dest.relative_to(T)), sha256=sha(p)))

def tree(p, dest):
    for f in sorted(p.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            copy(f, dest / f.relative_to(p))

def jobs(lane):
    with sqlite3.connect(f"file:{lane}/state.sqlite?mode=ro", uri=True) as db:
        cols = [r[1] for r in db.execute("pragma table_info(jobs)")]
        return [dict(zip(cols, r)) for r in db.execute("select * from jobs order by id")]

def main():
    assert not (P / "validation.json").exists()
    c = load(L / "config.json")
    phase = Path(c["phase"])
    label = c["label"]
    term = load(L / "terminal.json")
    assert term["bv1"] == 125 and term["values"] == 120
    for p, h in term["receipts"].items():
        assert sha(p) == h
    tree(phase, T / phase.relative_to(S))
    for rel in [
        f"analysis/freeflow/personality-aggregates/{label}",
        f"analysis/freeflow/personality-model-cards/cards/{slug}.md",
        f"analysis/freeflow/personality-model-profiles/profiles/{slug}.md",
        f"analysis/values-probe/final/reports/{slug}.md",
    ]:
        p = S / rel
        tree(p, T / rel) if p.is_dir() else copy(p, T / rel)
    for arm in ("bv1-luna-v1-20260929", "bv1-luna-v1-targeted-20261016"):
        p = S / f"analysis/freeflow/personality-eval-bv1/arms/{arm}/outputs/{label}"
        tree(p, T / p.relative_to(S))
    readings = []
    for row in jobs(L):
        if "/bv1/" not in row["id"]:
            continue
        assert row["state"] == "done"
        sid = row["id"].split("/")[-1]
        receipts = json.loads(row["receipts"])
        for p, h in receipts.items():
            assert sha(p) == h
        paths = [Path(p) for p in receipts]
        reading = next((p for p in paths if p.name == "reading.md"), None)
        if reading:
            attempt = next(p for p in paths if p.name in {"original_attempt.json", "generation_attempt.json"})
            a = load(attempt)
            assert a["response"]["choices"][0]["message"]["content"] == reading.read_text()
            assert a["source_sha256"] == c["source_adoption"]["sha256"]["freeflow"][sid]
            dest = P / "canonical-readings" / (sid + ".md")
        else:
            reading = next(p for p in paths if p.suffix == ".md")
            dest = T / reading.relative_to(R / "qwen2_eight_targeted_20261127/analysis")
        copy(reading, dest)
        readings.append(dict(sample=sid, source=str(reading), destination=str(dest.relative_to(T)),
                             sha256=sha(reading), separate_short_rule=reading.name == "reading.md",
                             receipts=receipts))
    assert len(readings) == len({r["sample"] for r in readings}) == 125
    offline = load(R / "continuation_batch_v13_qwen2-1-5b-instruct_offline_short_20261127/terminal.json")
    assert len(offline["adopted"]) == 14
    targeted = load(R / "qwen2_eight_targeted_20261127/terminal.json")
    assert len(offline["remaining_ids"]) == 8
    assert len(targeted["results"]) == 4
    names = [
        "continuation_batch_v13_qwen2-1-5b-instruct",
        "continuation_batch_v13_qwen2-1-5b-instruct_offline_short_20261127",
        "qwen2_eight_targeted_20261127",
        "qwen2_eight_targeted_20261127.setup-no-calls",
        "qwen2_final_20261127",
        "qwen2_final_20261127b",
        "remaining_recovery_colab-qwen2-1-5b-instruct",
        "state/colab-qwen2-1-5b-instruct",
    ]
    for name in names:
        lane = R / name
        assert lane.is_dir(), lane
        for p in sorted(lane.rglob("*")):
            rel = p.relative_to(lane)
            if not p.is_file() or rel.parts[0] in {"analysis", "phase", "__pycache__"}:
                continue
            if p.name.startswith("state.sqlite") or p.name.endswith(".lock"):
                continue
            copy(p, P / "history" / name / rel)
        if (lane / "state.sqlite").exists():
            put(P / "history" / name / "jobs-snapshot.json", jobs(lane))
    for pattern in ("qwen2*.py", "qwen2*.log"):
        for p in R.glob(pattern):
            if not p.name.startswith("qwen25"):
                copy(p, P / "history/scripts-and-logs" / p.name)
    # Freeze validator and original-generation provenance at their recorded paths.
    for row in offline["adopted"]:
        for key in ("original_validator_files_sha256", "validator_files_sha256"):
            for p, h in row[key].items():
                assert sha(p) == h
                copy(Path(p), P / "history/frozen-source" / Path(p).relative_to("/"))
    shared = []
    for p in sorted((S / "analysis/values-probe/final/data").glob("*.jsonl")):
        rows = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        if not rows:
            continue
        assert all(slug in json.dumps(x) or phase.name in json.dumps(x) for x in rows)
        dest = T / p.relative_to(S)
        prior = dest.read_bytes() if dest.exists() else b""
        assert not any(slug in json.dumps(json.loads(x)) for x in prior.splitlines() if x.strip())
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(prior + p.read_bytes())
        shared.append(dict(path=str(dest.relative_to(T)), prior_sha256=hashlib.sha256(prior).hexdigest(),
                           added_rows=len(rows), sha256=sha(dest), added_bytes=len(p.read_bytes())))
    for rel, key, incoming in [
        ("analysis/freeflow/personality-model-profiles/index.json", "model", slug),
        ("analysis/values-probe/final/capture_sources.json", None, phase.name),
    ]:
        dest = T / rel
        old, src = load(dest), load(S / rel)
        additions = [r for r in src if (r[key] if key else r) == incoming]
        assert len(additions) == 1 and not any((r[key] if key else r) == incoming for r in old)
        put(dest, old + additions)
    traces = []
    for probe, expected in (("freeflow", 125), ("values", 120)):
        hashes = c["source_adoption"]["sha256"][probe]
        assert len(hashes) == expected
        for sid, h in hashes.items():
            p = R / "raw" / ("data/traces_freeflow" if probe == "freeflow" else "data/traces_values") / (("freeflow_" if probe == "freeflow" else "") + label) / (sid + ".json")
            assert sha(p) == h
            traces.append(dict(probe=probe, sample=sid, source=str(p), sha256=h))
    put(P / "validation.json", dict(
        base=subprocess.check_output(["git", "-C", str(T), "rev-parse", "HEAD"], text=True).strip(),
        bv1=125, values=120, offline_adoptions=14, targeted_scope=8, targeted_short_adoptions=4,
        canonical_readings=readings, canonical_raw_sources=traces,
        copied_files=inventory, append_only_jsonl=shared,
        model_calls=0, remote_writes=False, website_changes=False))
    print(len(inventory), "files preserved; 125+120 verified")

if __name__ == "__main__":
    main()
