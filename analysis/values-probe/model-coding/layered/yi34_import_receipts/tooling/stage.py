#!/usr/bin/env python3
"""Offline, read-only input inspection; stdout manifest, optional local staging."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HOME = Path(__file__).resolve().parent
WORK = HOME.parent
QUEUE = WORK / "colab-batch-queue"
RAW = WORK / "model-personality-corpus-v2"
ANALYSIS = WORK / "model-personality-analysis-corpus"
PILOT_SLUG = "qwen2-5-32b-instruct"
PILOT_LABEL = PILOT_SLUG + "-colab-vllm-bf16-r5ede1c97"
PILOT_PHASE = "capture_20261125-colab-qwen25-32b_" + PILOT_LABEL
LAYERED = "analysis/values-probe/model-coding/layered/"
POST_INTEGRATION = {
    "ANALYSIS_READY.json", "CARD_READY.json", "VALUES_CARD.json",
    "VALUES_INTEGRATED.json",
}


def load(path):
    return json.loads(Path(path).read_bytes())


def git(repo, *args):
    # Only explicitly read-only Git plumbing. Never invoke queue/worker code.
    return subprocess.check_output(["git", "-C", str(repo), *args])


def tree(repo, commit):
    return git(repo, "ls-tree", "-r", "--name-only", commit).decode().splitlines()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_destination(path):
    p = Path(path)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError("unsafe destination")
    return p


def pilot_templates():
    receipt = load(QUEUE / "pilot-publication.json")
    paths = tree(ANALYSIS, receipt["analysis_commit"])
    # These are the exact model-specific analysis paths present at publication.
    analysis = [p for p in paths if p.startswith("analysis/") and (
        PILOT_LABEL in p or
        p in (
            f"analysis/freeflow/personality-model-cards/cards/{PILOT_SLUG}.md",
            f"analysis/freeflow/personality-model-profiles/profiles/{PILOT_SLUG}.md",
        ))]
    raw = [p for p in tree(RAW, receipt["raw_commit"])
           if p.startswith("data/") and PILOT_LABEL in p and p.endswith(".json")]
    if len(raw) != 245 or not analysis:
        raise ValueError("published pilot template incomplete")
    return receipt, raw, analysis


def manifest(cell):
    plan = load(QUEUE / "plan.json")
    allowed = {r["cell"]: r for r in plan["cells"]}
    if cell not in allowed:
        raise ValueError("cell is not active (held, pilot or unknown)")
    configs = list((QUEUE / "state" / cell / "models").glob("*.json"))
    if len(configs) != 1:
        raise ValueError("expected one compiled model config")
    c = load(configs[0])
    receipt, raw_template, analysis_template = pilot_templates()
    root = Path(c["analysis_root"]).resolve()
    if root != (QUEUE / "analysis-worktree").resolve():
        raise ValueError("unexpected analysis root")
    phase = Path(c["phase"]).resolve()
    if phase != root / LAYERED / c["phase_name"]:
        raise ValueError("unexpected phase")
    entries, missing, blockers = [], [], []

    def add(repo, src, dest, expected=None):
        safe_destination(dest)
        src = Path(src)
        if src.is_symlink():
            raise ValueError("symlink input")
        if not src.is_file():
            missing.append(str(src))
            return
        data = src.read_bytes()
        sha = digest(data)
        if expected and sha != expected:
            raise ValueError(f"raw hash mismatch: {src}")
        entries.append(dict(repository=repo, source=str(src), destination=dest,
                            sha256=sha, bytes=len(data)))

    for p in raw_template:
        dest = p.replace(PILOT_LABEL, c["label"])
        probe = "freeflow" if "/traces_freeflow/" in dest else "values"
        sid = Path(dest).stem
        expected = c["source_adoption"]["sha256"][probe][sid]
        add("raw", QUEUE / "raw" / dest, dest, expected)
    deferred = []
    for p in analysis_template:
        # Attempt response filenames contain run-specific timestamps/IDs. Import
        # the current cell's actual phase files below, never pilot timestamps.
        if "/attempt_responses/" in p:
            continue
        dest = p.replace(PILOT_PHASE, c["phase_name"]).replace(
            PILOT_LABEL, c["label"]).replace(PILOT_SLUG, c["slug"])
        if p.startswith(LAYERED + PILOT_PHASE + "/") and Path(p).name in POST_INTEGRATION:
            deferred.append(dest)
        else:
            add("analysis", root / dest, dest)
    ready = phase / "QUEUE_ANALYSIS_READY.json"
    if not ready.exists():
        blockers.append("QUEUE_ANALYSIS_READY missing: not analysis-complete")
    else:
        r = load(ready)
        if (r.get("state") != "analysis_only_awaiting_review"
                or r.get("model") != c["slug"]
                or r.get("source_adoption") != c["source_adoption"]
                or r.get("raw_counts") != {"freeflow": 125, "values": 120}
                or any(r.get(k) is not False for k in (
                    "publication_complete", "website_touched", "site_integration_performed"))):
            raise ValueError("invalid queue terminal record")
        add("analysis", ready, str(ready.relative_to(root)))
    # Include queue-only artifacts, but never unrelated cells or a whole worktree.
    known = {e["source"] for e in entries}
    if phase.exists():
        for src in sorted(phase.rglob("*")):
            if src.is_file() and str(src) not in known and src.name not in POST_INTEGRATION:
                add("analysis", src, str(src.relative_to(root)))
    if missing:
        blockers.append("pilot-equivalent analysis/raw artifacts missing; inspect missing list")
    destinations = [(e["repository"], e["destination"]) for e in entries]
    if len(destinations) != len(set(destinations)):
        raise ValueError("duplicate destinations")
    return dict(schema="colab-import-dry-run-v1", cell=cell, label=c["label"],
                publication_authorized=False, import_complete=not blockers,
                pilot=receipt, config_sha256=digest(configs[0].read_bytes()),
                entries=entries, missing=missing, blockers=blockers,
                deferred_integration=deferred,
                notes=["QUEUE_ANALYSIS_READY is not CARD_READY or ANALYSIS_READY.",
                       "No terminal record conversion or values/site integration performed.",
                       "Review semantic QA, adjudication, eligibility and release policy separately."])


def stage(m, name):
    # Bundle copies only; no Git index, releases or publication checkouts.
    if not m["import_complete"]:
        raise ValueError("incomplete manifest cannot be staged")
    if Path(name).name != name or name in ("", ".", ".."):
        raise ValueError("stage name must be one path component")
    target = HOME / name
    target.mkdir(exist_ok=False)
    for e in m["entries"]:
        data = Path(e["source"]).read_bytes()
        if digest(data) != e["sha256"]:
            raise ValueError("source changed since manifest")
        out = target / e["repository"] / safe_destination(e["destination"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    (target / "manifest.json").write_text(json.dumps(m, indent=2) + "\n")


def verify_pilot():
    receipt, raw, analysis = pilot_templates()
    checked = {}
    for repo, commit, paths in (
        (RAW, receipt["raw_commit"], raw),
        (ANALYSIS, receipt["analysis_commit"], analysis),
    ):
        checked[repo.name] = [
            dict(path=p, sha256=digest(git(repo, "show", f"{commit}:{p}")))
            for p in paths]
    return dict(evidence="local published-commit objects, not live website verification",
                receipt=receipt, files=checked)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cell")
    p.add_argument("--verify-pilot", action="store_true")
    p.add_argument("--stage", metavar="NEW_LOCAL_FOLDER")
    a = p.parse_args()
    if a.verify_pilot:
        if a.cell or a.stage:
            p.error("pilot verification cannot stage")
        result = verify_pilot()
    else:
        if not a.cell:
            p.error("--cell required")
        result = manifest(a.cell)
        if a.stage:
            stage(result, a.stage)
    print(json.dumps(result, indent=2))
