"""Offline, byte-preserving Qwen1.5 32B analysis import. No provider code loaded."""
from pathlib import Path
import hashlib
import json
import sqlite3
import subprocess

ROOT = Path("/home/agent/work/colab-batch-queue")
LANE = ROOT / "qwen32_values_authorized_20261127"
SITE = Path("/home/agent/work/colab-q1532-analysis")
SOURCE = LANE / "analysis"
SLUG = "qwen1-5-32b-chat"
PROV = SITE / "analysis/import-provenance/qwen1-5-32b-chat-local-20261127"
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
    data = p.read_bytes()
    if dest.exists():
        assert dest.read_bytes() == data, dest
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    assert sha(dest) == sha(p)
    inventory.append(dict(source=str(p), destination=str(dest.relative_to(SITE)), sha256=sha(p)))

def tree(p, dest):
    for f in sorted(p.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            copy(f, dest / f.relative_to(p))

def main():
    assert not (PROV / "validation.json").exists()
    config = load(LANE / "config.json")
    phase = Path(config["phase"])
    label = config["label"]
    terminal = load(LANE / "terminal.json")
    assert terminal["bv1"] == 125 and terminal["values"] == 120
    for p, digest in terminal["receipts"].items():
        assert sha(p) == digest
    # Retain all phase coding, consensus, adjudication, attempt and binding files.
    tree(phase, SITE / phase.relative_to(SOURCE))
    for rel in [
        f"analysis/freeflow/personality-aggregates/{label}",
        f"analysis/freeflow/personality-model-cards/cards/{SLUG}.md",
        f"analysis/freeflow/personality-model-profiles/profiles/{SLUG}.md",
        f"analysis/values-probe/final/reports/{SLUG}.md",
    ]:
        p = SOURCE / rel
        tree(p, SITE / rel) if p.is_dir() else copy(p, SITE / rel)
    evidence = load(LANE / "offline-validation.json")["samples"]
    assert len(evidence) == len({r["sample"] for r in evidence}) == 125
    for row in evidence:
        p = Path(row["output"])
        assert sha(p) == row["output_sha256"]
        if row["separate_v13_revalidation"]:
            assert row["sample"] in {"MID_7", "MID_9", "MID_19", "MID_23", "LONG_2", "LONG_5", "LONG_21"}
            # Keep separately adopted reading, not falsely attributed mainline output.
            copy(p, PROV / "canonical-readings" / (row["sample"] + ".md"))
        else:
            copy(p, SITE / p.relative_to(SOURCE))
    # Preserve producing-arm outputs and sidecars even for separately adopted rows.
    for arm in ("bv1-luna-v1-20260929", "bv1-luna-v1-targeted-20261016"):
        p = SOURCE / f"analysis/freeflow/personality-eval-bv1/arms/{arm}/outputs/{label}"
        tree(p, SITE / p.relative_to(SOURCE))
    # Historical lanes, including failure state/logs and offline validator source.
    names = [
        "continuation_batch_v13_qwen1-5-32b-chat",
        "continuation_batch_v13_qwen1-5-32b-chat_offline_six_20261127",
        "qwen32_three_targeted_20261127",
        "qwen32_values_authorized_20261127",
        "remaining_recovery_colab-qwen1-5-32b-chat",
        "state/qwen32-scoped-essay-recovery-v1",
        "state/colab-qwen1-5-32b-chat",
    ]
    for name in names:
        lane = ROOT / name
        history_name = "original-state" if name.startswith("state/") else name
        assert lane.is_dir(), lane
        for p in sorted(lane.rglob("*")):
            rel = p.relative_to(lane)
            if not p.is_file() or rel.parts[0] in {"analysis", "phase", "__pycache__"}:
                continue
            if p.name.startswith("state.sqlite") or p.name.endswith(".lock"):
                continue
            copy(p, PROV / "history" / history_name / rel)
        dbp = lane / "state.sqlite"
        if dbp.exists():
            with sqlite3.connect(f"file:{dbp}?mode=ro", uri=True) as db:
                cols = [r[1] for r in db.execute("pragma table_info(jobs)")]
                jobs = [dict(zip(cols, r)) for r in db.execute("select * from jobs order by id")]
            put(PROV / "history" / history_name / "jobs-snapshot.json", jobs)
    for p in ROOT.glob("qwen32*.log"):
        copy(p, PROV / "history/logs" / p.name)
    copy(ROOT / "qwen32-scoped-essay-recovery-report.md", PROV / "history/recovery-report.md")
    for p in ROOT.glob("qwen32*.py"):
        copy(p, PROV / "history/scripts" / p.name)
    # Only append final Qwen rows to current shared data; never replace newer models.
    shared = []
    for p in sorted((SOURCE / "analysis/values-probe/final/data").glob("*.jsonl")):
        rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        if not rows:
            continue
        assert all(SLUG in json.dumps(r) or phase.name in json.dumps(r) for r in rows), p
        dest = SITE / p.relative_to(SOURCE)
        prior = dest.read_bytes() if dest.exists() else b""
        existing = [json.loads(l) for l in prior.splitlines() if l.strip()]
        if any(SLUG in json.dumps(r) or phase.name in json.dumps(r) for r in existing):
            assert existing[-len(rows):] == rows
            assert prior.endswith(p.read_bytes())
            prior = prior[:-len(p.read_bytes())]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(prior + p.read_bytes())
        assert dest.read_bytes().startswith(prior)
        shared.append(dict(path=str(dest.relative_to(SITE)), prior_sha256=hashlib.sha256(prior).hexdigest(), added_rows=len(rows), sha256=sha(dest)))
    for rel, key, incoming in [
        ("analysis/freeflow/personality-model-profiles/index.json", "model", SLUG),
        ("analysis/values-probe/final/capture_sources.json", None, phase.name),
    ]:
        dest = SITE / rel
        old = load(dest)
        src = load(SOURCE / rel)
        additions = [r for r in src if (r[key] if key else r) == incoming]
        assert len(additions) == 1
        if any((r[key] if key else r) == incoming for r in old):
            assert old[-1:] == additions
            old = old[:-1]
        put(dest, old + additions)
        assert load(dest)[:len(old)] == old
    # Raw traces are separately published; verify every canonical source locally.
    traces = []
    for probe, expected in (("freeflow", 125), ("values", 120)):
        hashes = config["source_adoption"]["sha256"][probe]
        assert len(hashes) == expected
        for sid, digest in hashes.items():
            p = ROOT / "raw" / ("data/traces_freeflow" if probe == "freeflow" else "data/traces_values") / (("freeflow_" if probe == "freeflow" else "") + label) / (sid + ".json")
            assert sha(p) == digest
            traces.append(dict(probe=probe, sample=sid, source=str(p), sha256=digest))
    for row in evidence:
        assert row["source_sha256"] == config["source_adoption"]["sha256"]["freeflow"][row["sample"]]
    for r in terminal["transport_receipts"]:
        assert sha(r["charge"]) == r["charge_sha256"]
        assert sha(r["response"]) == r["response_sha256"]
    for item in inventory:
        assert sha(SITE / item["destination"]) == item["sha256"]
    put(PROV / "validation.json", dict(
        base=subprocess.check_output(["git", "-C", str(SITE), "rev-parse", "HEAD"], text=True).strip(),
        bv1=125, values=120, copied_files=inventory, canonical_readings=evidence,
        canonical_raw_sources=traces, append_only_jsonl=shared,
        model_calls=0, remote_writes=False, website_changes=False,
    ))
    print(json.dumps(dict(copied_files=len(inventory), bv1=125, values=120, validation=str(PROV / "validation.json"))))

if __name__ == "__main__":
    main()
