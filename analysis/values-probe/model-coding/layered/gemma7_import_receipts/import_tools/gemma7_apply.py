#!/usr/bin/env python3
"""Fixed original-Gemma analysis lane; no site, network, inference or raw writes."""
import json
from pathlib import Path
import subprocess
import types
import q1505_apply as predecessor
import gemma7_import as evidence

TARGET = evidence.HOME.parent / "colab-g7-site"
RAW = evidence.HOME.parent / "colab-g7-raw"
HEAD = "17d4b64f2d3c9985e64ae31f72a8ff3603057b70"
rows = predecessor.rows


def main():
    def git(*args):
        return subprocess.check_output(["git", "-C", str(TARGET), *args])
    need = evidence.need
    manifest = evidence.inspect()
    need(manifest["import_complete"], "terminal incomplete")
    need(git("rev-parse", "HEAD").decode().strip() == HEAD, "base changed")
    need(not git("diff", "--cached", "--name-only"), "index already populated")
    need(not git("status", "--porcelain", "--", "analysis"), "unexpected analysis changes")
    pending = []
    for e in manifest["entries"]:
        if e["destination"].startswith("raw/"):
            candidate = RAW / Path(e["destination"]).relative_to("raw")
            need(evidence.digest(evidence.read(candidate, root=RAW)) == e["sha256"],
                 "raw candidate mismatch")
        if e["destination"].startswith("evidence/"):
            rel = Path("analysis/values-probe/model-coding/layered") / (
                "gemma7_import_receipts") / Path(e["destination"]).relative_to("evidence")
        elif e["destination"].startswith("analysis/"):
            rel = Path(e["destination"]).relative_to("analysis")
        else:
            continue
        need(rel.parts[0] == "analysis" and ".." not in rel.parts, "not analysis")
        dest = TARGET / rel
        need(not any(p.is_symlink() for p in (dest, *dest.parents)), "target symlink")
        data = evidence.read(e["source"])
        need(evidence.digest(data) == e["sha256"], "source drift")
        if dest.exists():
            need(dest.read_bytes() == data, "existing file conflict")
        else:
            pending.append((dest, data))
    final = TARGET / "analysis/values-probe/final"
    before = {p: p.read_bytes() for p in (final / "data").glob("*.jsonl")}
    path = final / "scripts/integrate_capture_values.py"
    source = path.read_text()
    start = source.index("        # Website functions read an isolated copy")
    end = source.index("        if validate:", start)
    source = source[:start] + "        found = set()  # analysis-only lane\n" + source[end:]
    module = types.ModuleType("gemma7_values_integrator")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    module.RAW = RAW
    receipt = TARGET / "analysis/values-probe/model-coding/layered/gemma7_import_receipts/task_snapshots.json"
    need(not receipt.exists(), "snapshot already exists")
    pending.append((receipt, (json.dumps(manifest["task_snapshots"], indent=2) + "\n").encode()))
    for dest, data in pending:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    phase = TARGET / Path(evidence.load(evidence.STATE / "config.json")["phase"]).relative_to(
        evidence.QUEUE / "analysis-worktree")
    module.integrate([phase])
    checks = {}
    for p, original in before.items():
        need(not (rows(original) - rows(p.read_bytes())), "prior JSONL rows lost")
        checks[str(p.relative_to(TARGET))] = dict(
            prior_sha256=evidence.digest(original), prior_rows=sum(rows(original).values()),
            after_sha256=evidence.digest(p.read_bytes()), after_rows=sum(rows(p.read_bytes()).values()),
            prior_multiset_preserved=True)
    report = dict(base=HEAD, evidence_manifest=manifest, jsonl_preservation=checks,
                  scope="Analysis only; no site/raw/network writes")
    (evidence.HOME / "gemma7_applied.json").write_text(json.dumps(report, indent=2) + "\n")
    imported = [str(p.relative_to(TARGET)) for p, _ in pending]
    changed = git("diff", "--name-only", "--", str(final.relative_to(TARGET))).decode().splitlines()
    paths = sorted(set(imported + changed))
    need(all(p.startswith("analysis/") for p in paths), "non-analysis path")
    for offset in range(0, len(paths), 100):
        git("add", "-f", "--", *paths[offset:offset + 100])
    staged = git("diff", "--cached", "--name-only").decode().splitlines()
    need(set(staged) == set(paths), "index collision")
    print(json.dumps(dict(staged_files=len(staged), copied_files=len(pending),
                          jsonl_checks=checks), indent=2))


if __name__ == "__main__":
    main()
