#!/usr/bin/env python3
"""Integrate verified capture values, preserving all other data/editorial fields.
No inference. Lock + preimage checks; changed concurrent files abort, never clobber.
"""

import argparse, collections, fcntl, hashlib, importlib.util, json, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FINAL = ROOT / "analysis/values-probe/final"
REGISTRY = FINAL / "capture_sources.json"
CODERS = ["kimi-k2-6", "glm-4-7", "qwen3-6-35b-a3b"]
VALUE_FIELDS = {
    "analyzed_values_samples",
    "values_headline",
    "values_summary_markdown",
    "values_details_markdown",
    "values_markdown",
}


def load_module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read_rows(p):
    return (
        [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        if p.exists()
        else []
    )


def encoded(rows):
    return ("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)).encode()


def canonical(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def merge_rows(old, new, key):
    # Legacy data contains duplicate IDs. Preserve its exact multiplicity;
    # never deduplicate unrelated historical records during an additive merge.
    index = collections.defaultdict(list)
    for row in old:
        index[row[key]].append(row)
    incoming = {}
    for row in new:
        k = row[key]
        assert k not in incoming, "duplicate incoming record " + str(k)
        incoming[k] = row
        if k in index:
            assert all(existing == row for existing in index[k]), (
                "conflicting existing record " + str(k)
            )
    result = old + [r for r in new if r[key] not in index]
    assert not (
        collections.Counter(map(canonical, old))
        - collections.Counter(map(canonical, result))
    )
    return result


def integrate(phases, validate=False):
    phases = [Path(p).resolve() for p in phases]
    lock = ROOT / "logs/capture-harness-publication.lock"
    lock.parent.mkdir(exist_ok=True)
    with lock.open("a+") as lane:
        fcntl.flock(lane, fcntl.LOCK_EX)
        pending = {}
        before = {p: sha(p) for p in (FINAL / "data").glob("*") if p.is_file()}
        before[REGISTRY] = sha(REGISTRY)

        def stage(path, content):
            if path not in before:
                before[path] = sha(path)
            pending[path] = content

        registry = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else []
        all_new = collections.defaultdict(list)
        models = {}
        sources = []
        reports = {}
        for phase in phases:
            assert phase.parent == ROOT / "analysis/values-probe/model-coding/layered"
            manifest = read_rows(phase / "manifest.jsonl")
            assert len(manifest) == 120
            modelset = {r["model"] for r in manifest}
            assert len(modelset) == 1
            model = next(iter(modelset))
            ids = {r["layered_id"] for r in manifest}
            assert len(ids) == 120
            models[model] = phase
            adjudication = json.loads((phase / "adjudication.json").read_text())
            assert not adjudication["residual_splits"], (
                "unresolved split needs explicit publication policy"
            )
            # Raw sources must still match their frozen verified manifests.
            raw = ROOT.parent / "model-personality-corpus-v2"
            for row in manifest:
                assert sha(raw / row["trace_path"]) == row["source_sha256"]
            files = {
                "manifest_valid.jsonl": phase / "manifest.jsonl",
                "layer_a_consensus.jsonl": phase / "layer_a/consensus_300.jsonl",
                "posture_consensus.jsonl": phase / "posture_final/consensus.jsonl",
            }
            files.update(
                {
                    f"layer_a_coder_{c}.jsonl": phase / "layer_a" / f"{c}.jsonl"
                    for c in CODERS
                }
            )
            files.update(
                {
                    f"posture_coder_{c}.jsonl": phase / "posture_final" / f"{c}.jsonl"
                    for c in CODERS
                }
            )
            for name, path in files.items():
                rows = read_rows(path)
                assert len(rows) == 120 and {r["layered_id"] for r in rows} == ids, (
                    model,
                    name,
                )
                all_new[name].extend({**r, "final_source": phase.name} for r in rows)
            sources.append(
                dict(
                    source=phase.name,
                    manifest=str((phase / "manifest.jsonl").relative_to(ROOT)),
                    layer_a_consensus=str(
                        (phase / "layer_a/consensus_300.jsonl").relative_to(ROOT)
                    ),
                    posture_consensus=str(
                        (phase / "posture_final/consensus.jsonl").relative_to(ROOT)
                    ),
                    samples=120,
                    models=1,
                    cells=1,
                )
            )
            if phase.name not in registry:
                registry.append(phase.name)
            reports[model] = (
                phase / "release_candidate/reports" / f"{model}.md"
            ).read_bytes()
        # Reuse the established assembler in a temporary output tree to calculate
        # reports/summary/QA, with identical method, not recoding samples.
        assembler = load_module(
            "values_assembler", FINAL / "scripts/assemble_final_values_probe.py"
        )
        with tempfile.TemporaryDirectory(prefix="values-integration-") as td:
            temp = Path(td)
            assembler.DATA = temp / "data"
            assembler.REPORTS = temp / "reports"
            assembler.SOURCES = [
                dict(
                    name=phase.name,
                    manifest=phase / "manifest.jsonl",
                    invalid=None,
                    layer_a_dir=phase / "layer_a",
                    layer_a_consensus=phase / "layer_a/consensus_300.jsonl",
                    posture_dir=phase / "posture_final",
                    posture_consensus=phase / "posture_final/consensus.jsonl",
                )
                for phase in phases
            ]
            assembler.main()
            for name, rows in all_new.items():
                path = FINAL / "data" / name
                old = read_rows(path)
                merged = merge_rows(old, rows, "layered_id")
                stage(path, encoded(merged))
            for name, rows, key in [
                ("source_map.jsonl", sources, "source"),
                (
                    "model_summary.jsonl",
                    read_rows(temp / "data/model_summary.jsonl"),
                    "model",
                ),
            ]:
                path = FINAL / "data" / name
                stage(path, encoded(merge_rows(read_rows(path), rows, key)))
            for model, content in reports.items():
                p = FINAL / "reports" / f"{model}.md"
                if p.exists():
                    assert p.read_bytes() == content, (
                        "existing report differs: " + model
                    )
                stage(p, content)
        manifest_rows = [
            json.loads(l)
            for l in pending[FINAL / "data/manifest_valid.jsonl"].decode().splitlines()
        ]
        source_rows = [
            json.loads(l)
            for l in pending[FINAL / "data/source_map.jsonl"].decode().splitlines()
        ]
        posture_rows = [
            json.loads(l)
            for l in pending[FINAL / "data/posture_consensus.jsonl"]
            .decode()
            .splitlines()
        ]
        qa = [
            "# Final values-probe data QA",
            "",
            f"- valid samples: {len(manifest_rows)}",
            f"- invalid/error traces excluded: {len(read_rows(FINAL / 'data/manifest_invalid_traces.jsonl'))}",
            f"- models: {len({r['model'] for r in manifest_rows})}",
            f"- cells: {len({r['cell'] for r in manifest_rows})}",
            "",
            "## Source components",
            "",
        ]
        qa += [
            f"- {r['source']}: {r['samples']} samples, {r['models']} model(s), {r['cells']} cell(s)"
            for r in source_rows
        ]
        for title, field in [
            ("Overall collapsed posture distribution", "collapsed_primary_label"),
            ("Overall value-holding distribution", "value_holding"),
        ]:
            qa += ["", "## " + title, ""]
            qa += [
                f"- `{k}`: {n} ({assembler.pct(n, len(posture_rows))})"
                for k, n in collections.Counter(
                    r[field] for r in posture_rows
                ).most_common()
            ]
        qa.append("")
        stage(FINAL / "data/QA.md", "\n".join(qa).encode())
        stage(REGISTRY, (json.dumps(sorted(registry), indent=2) + "\n").encode())
        # Website functions read an isolated copy of the staged final data.
        gd = load_module("values_website", ROOT / "website/scripts/generate_data.py")
        with tempfile.TemporaryDirectory(prefix="values-site-") as td:
            td = Path(td)
            for name in [
                "manifest_valid.jsonl",
                "layer_a_consensus.jsonl",
                "posture_consensus.jsonl",
            ]:
                (td / name).write_bytes(pending[FINAL / "data" / name])
            gd.FINAL_VALUES_DIR = td
            gd._FINAL_MANIFEST = gd._FINAL_LAYER_A = gd._FINAL_POSTURE = None
            site = ROOT / "website/src/generated/models.json"
            site_bytes = site.read_bytes()
            before[site] = hashlib.sha256(site_bytes).hexdigest()
            site_rows = json.loads(site_bytes)
            found = set()
            for model, phase in models.items():
                payload = dict(
                    model=model,
                    analyzed_values_samples=120,
                    values_headline=gd.values_headline_data(model),
                    values_summary_markdown=gd.build_values_summary(model),
                    values_details_markdown=gd.build_values_details(model),
                    values_markdown=reports[model].decode(),
                )
                assert (
                    "No layered values-probe analysis"
                    not in payload["values_summary_markdown"]
                )
                assert len(gd.final_values_for_model(model)[0]) == 120
                stage(
                    phase / "VALUES_CARD.json",
                    (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(),
                )
                for row in site_rows:
                    if row["model"] != model:
                        continue
                    old = dict(row)
                    row.update({k: payload[k] for k in VALUE_FIELDS})
                    found.add(model)
                    assert {k: v for k, v in row.items() if k not in VALUE_FIELDS} == {
                        k: v for k, v in old.items() if k not in VALUE_FIELDS
                    }
                receipt = dict(
                    state="values_integrated",
                    model=model,
                    samples=120,
                    source=phase.name,
                    site_entry_present=model in found,
                    publication_complete=False,
                )
                stage(
                    phase / "VALUES_INTEGRATED.json",
                    (json.dumps(receipt, indent=2) + "\n").encode(),
                )
            stage(site, (json.dumps(site_rows, ensure_ascii=False, indent=2)).encode())
        if validate:
            for path, content in pending.items():
                assert path.exists() and path.read_bytes() == content, (
                    "integration missing/drift: " + str(path)
                )
            return {
                "models": sorted(models),
                "site_models": sorted(found),
                "validated": True,
            }
        # No file is changed if any preimage moved while staging.
        assert all(sha(p) == h for p, h in before.items()), (
            "concurrent change detected; retry from fresh state"
        )
        for path, content in pending.items():
            if path.exists() and path.read_bytes() == content:
                continue
            assert sha(path) == before[path], (
                "concurrent change immediately before write: " + str(path)
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
            tmp.write_bytes(content)
            tmp.replace(path)
        result = {
            "models": sorted(models),
            "site_models": sorted(found),
            "samples_added_or_verified": len(models) * 120,
            "publication_complete": False,
        }
        print(json.dumps(result), flush=True)
        return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phases", nargs="+", type=Path)
    p.add_argument("--validate", action="store_true")
    a = p.parse_args()
    integrate(a.phases, a.validate)
