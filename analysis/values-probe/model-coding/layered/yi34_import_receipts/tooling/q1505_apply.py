#!/usr/bin/env python3
"""Offline local analysis import, fixed worktree; never stage website or run inference."""
import collections
import json
from pathlib import Path
import subprocess
import types

import q1505_import as evidence

TARGET = evidence.HOME.parent / "colab-q1505-site"
RAW = evidence.HOME.parent / "colab-q1505-raw"
HEAD = "2b95b7b7765beec5510cdc85fc2a5676b377e7aa"


def git(*args):
    return subprocess.check_output(["git", "-C", str(TARGET), *args])


def rows(data):
    return collections.Counter(json.dumps(json.loads(line), sort_keys=True)
                               for line in data.splitlines() if line.strip())


def main():
    manifest = evidence.inspect()
    evidence.need(manifest["import_complete"], "terminal incomplete")
    evidence.need(git("rev-parse", "HEAD").decode().strip() == HEAD, "base changed")
    evidence.need(not git("diff", "--cached", "--name-only"), "index already populated")
    prior_changes = git("status", "--porcelain", "--", "analysis").decode().splitlines()
    evidence.need(not prior_changes, "unexpected analysis changes")
    for e in manifest["entries"]:
        if e["destination"].startswith("raw/"):
            candidate = RAW / Path(e["destination"]).relative_to("raw")
            evidence.need(evidence.digest(evidence.read(candidate, root=RAW)) == e["sha256"],
                          "raw candidate mismatch: " + str(candidate))
    sources = [e for e in manifest["entries"] if e["destination"].startswith("analysis/")]
    pending = []
    for e in sources:
        rel = Path(e["destination"]).relative_to("analysis")
        evidence.need(rel.parts[0] == "analysis", "not analysis")
        dest = TARGET / rel
        evidence.need(not any(p.is_symlink() for p in (dest, *dest.parents)), "target symlink")
        data = evidence.read(e["source"])
        evidence.need(evidence.digest(data) == e["sha256"], "source drift")
        if dest.exists():
            evidence.need(dest.read_bytes() == data, "existing file conflict")
        else:
            pending.append((dest, data))
    final = TARGET / "analysis/values-probe/final"
    before = {p: p.read_bytes() for p in (final / "data").glob("*.jsonl")}
    # All checks above precede writes. No existing evidence is overwritten.
    for dest, data in pending:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    path = final / "scripts/integrate_capture_values.py"
    # The published integrator also updates website models.json. Remove that
    # entire explicitly bounded block in memory; never load website code.
    source = path.read_text()
    start = source.index("        # Website functions read an isolated copy")
    end = source.index("        if validate:", start)
    source = source[:start] + "        found = set()  # analysis-only lane\n" + source[end:]
    module = types.ModuleType("q1505_values_integrator")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.RAW = RAW
    phase = TARGET / Path(evidence.load(evidence.STATE / "config.json")["phase"]).relative_to(
        evidence.QUEUE / "analysis-worktree")
    module.integrate([phase])
    checks = {}
    for p, original in before.items():
        evidence.need(not (rows(original) - rows(p.read_bytes())), "prior JSONL rows lost: " + str(p))
        checks[str(p.relative_to(TARGET))] = {
            "prior_sha256": evidence.digest(original), "prior_rows": sum(rows(original).values()),
            "after_rows": sum(rows(p.read_bytes()).values()),
            "after_sha256": evidence.digest(p.read_bytes()), "prior_multiset_preserved": True}
    report = dict(base=HEAD, terminal=evidence.load(evidence.STATE / "terminal.json"),
                  evidence_manifest=manifest, jsonl_preservation=checks,
                  limitations=["No editorial review or semantic QA", "No raw repository writes",
                               "No site integration, release, push or network",
                               "Historical JSONL reserialized by existing integrator; row multiplicities preserved"])
    (evidence.HOME / "q1505_applied.json").write_text(json.dumps(report, indent=2) + "\n")
    # Stage analysis only. The owner may be concurrently editing website.
    imported = [str(p.relative_to(TARGET)) for p, _ in pending]
    final_changed = git("diff", "--name-only", "--", str(final.relative_to(TARGET))).decode().splitlines()
    # Explicit paths, never a broad add: preserve concurrent owner's index/site edits.
    paths = sorted(set(imported + final_changed))
    for offset in range(0, len(paths), 100):
        git("add", "-f", "--", *paths[offset:offset + 100])
    staged = git("diff", "--cached", "--name-only").decode().splitlines()
    evidence.need(all(p.startswith("analysis/") for p in staged), "non-analysis staged")
    print(json.dumps(dict(staged_files=len(staged), copied_files=len(pending),
                          jsonl_checks=checks), indent=2))


if __name__ == "__main__":
    main()
