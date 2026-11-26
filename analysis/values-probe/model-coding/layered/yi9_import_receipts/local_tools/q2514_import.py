#!/usr/bin/env python3
"""Narrow offline evidence importer. No workers, sockets, git writes or integration."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sqlite3

HOME = Path(__file__).resolve().parent
QUEUE = HOME.parent / "colab-batch-queue"
STATE = QUEUE / "state/finish-qwen2-5-14b-instruct"
FORK = QUEUE / "remaining_recovery_colab-qwen2-5-14b-instruct"
SLUG = "qwen2-5-14b-instruct"
LABEL = SLUG + "-colab-vllm-bf16-rcf98f3b3"
ARM = "bv1-luna-v1-targeted-20261016"
V1 = "bv1-luna-v1-20260929"
VARIANTS = {"LONG_24", "VARY_21"}
SPEC_SHA = "0c252bea7acbe55ba6a8c5dc0172b6e07d9080c969038f4ea13e6cf8dc11f156"
NOTE = "a468a4f9f8d50f32617ab745facf605658ac4a9b66ddab11052d4158b3dc27ea"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, root=QUEUE):
    path = Path(path)
    need(path.is_relative_to(root) and ".." not in path.parts, "outside scope: " + str(path))
    need(not any(p.is_symlink() for p in (path, *path.parents)), "symlink: " + str(path))
    return path.read_bytes()


def load(path):
    return json.loads(read(path))


def snapshot(directory):
    spec = load(directory / "spec.json")
    with sqlite3.connect(f"file:{directory}/state.sqlite?mode=ro", uri=True) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        rows = db.execute("select id,state,attempts,receipts from jobs order by id").fetchall()
        meta = dict(db.execute("select k,v from meta"))
    need(meta.get("spec") == digest(json.dumps(spec, sort_keys=True).encode()), "DB/spec mismatch")
    tasks = {t["id"]: t for t in spec["tasks"]}
    need(len(tasks) == len(rows) == len(spec["tasks"]) and set(tasks) == {r[0] for r in rows},
         "task inventory mismatch")
    return spec, tasks, rows


def inspect():
    c = load(STATE / "config.json")
    root, phase = Path(c["analysis_root"]), Path(c["phase"])
    need(c["label"] == LABEL and c["slug"] == SLUG
         and root == QUEUE / "analysis-worktree" and phase.is_relative_to(root),
         "unexpected model/roots")
    need(digest(read(STATE / "spec.json")) == SPEC_SHA, "finish spec drift")
    entries, blockers = {}, []

    def add(src, repository, destination=None, expected=None):
        src = Path(src)
        data = read(src)
        sha = digest(data)
        need(expected is None or sha == expected, "receipt hash mismatch: " + str(src))
        dest = Path(destination) if destination else src.relative_to(
            {"analysis": root, "raw": QUEUE / "raw", "evidence": QUEUE}[repository])
        need(not dest.is_absolute() and ".." not in dest.parts and
             (repository != "analysis" or dest.parts[0] == "analysis"),
             "unsafe destination")
        key = repository + "/" + str(dest)
        e = dict(source=str(src), destination=key, sha256=sha, bytes=len(data))
        need(key not in entries or entries[key] == e, "destination collision")
        entries[key] = e
        return data

    old = load(FORK / "config.json")
    oldroot, oldphase = Path(old["analysis_root"]), Path(old["phase"])
    for directory, count in ((FORK, 1336), (STATE, 2)):
        spec, tasks, rows = snapshot(directory)
        need(len(rows) == count, "unexpected job count")
        need(spec["input_hashes"].get(str(directory / "config.json")) ==
             digest(read(directory / "config.json")), "spec/config binding")
        for jid, state, attempts, receipts in rows:
            task = tasks[jid]
            need(task["model"] == LABEL and 0 <= attempts <= task["max_attempts"], "foreign task/attempts")
            if directory == FORK and jid.rsplit("/", 1)[-1] in {"synthesis", "queue-ready"}:
                need(state == "pending" and attempts == 0, "unexpected fork downstream execution")
                continue
            if state != "done":
                blockers.append(jid + ": " + state)
                continue
            receipt = json.loads(receipts or "{}")
            need(bool(receipt), "empty receipt")
            # Recovery BV1 jobs may attest output, provenance and binding together.
            sid = jid.rsplit("/", 1)[-1]
            if "/bv1/" in jid and sid in VARIANTS:
                output = oldroot / "analysis/freeflow/personality-eval-bv1/arms" / ARM / "outputs" / LABEL / (sid + ".md")
                expected = {str(output), str(output) + ".provenance.json",
                            str(oldphase / "bv1_bindings_luna_v1_targeted" / (sid + ".json"))}
            else:
                expected = set(task["outputs"])
            need(set(receipt) == expected, "receipt output set: " + jid)
            for filename, sha in receipt.items():
                src = Path(filename)
                need(digest(read(src)) == sha, "original receipt hash: " + filename)
                if src.is_relative_to(oldphase):
                    add(phase / src.relative_to(oldphase), "analysis", expected=sha)
                elif src.is_relative_to(oldroot):
                    add(root / src.relative_to(oldroot), "analysis", expected=sha)
                elif src.is_relative_to(root):
                    add(src, "analysis", expected=sha)
                elif src.is_relative_to(QUEUE / "raw"):
                    add(src, "raw", expected=sha)
                else:
                    raise ValueError("unscoped receipt: " + filename)
        for name in ("config.json", "spec.json"):
            add(directory / name, "evidence")
        # Coherent database snapshot is represented as exported rows, not a live DB copy.
    terminal = STATE / "terminal.json"
    if not terminal.exists():
        blockers.append("finish terminal.json absent")
    else:
        need(load(terminal) == {"engine_result": "complete"}, "finish not complete")
        add(terminal, "evidence")
    free = c["source_adoption"]["sha256"]["freeflow"]
    for probe, count in (("freeflow", 125), ("values", 120)):
        hashes = c["source_adoption"]["sha256"][probe]
        need(len(hashes) == c["source_adoption"]["counts"][probe] == count, "raw counts")
        directory = QUEUE / "raw/data" / ("traces_" + probe) / (
            ("freeflow_" if probe == "freeflow" else "") + LABEL)
        need({p.stem for p in directory.glob("*.json")} == set(hashes), "raw inventory")
        for sid, sha in hashes.items():
            add(directory / (sid + ".json"), "raw", expected=sha)
    need({p.stem for p in (phase / "bv1_bindings_luna_v1_targeted").glob("*.json")} == VARIANTS,
         "variant inventory")
    outputs = {}
    for sid, sha in free.items():
        targeted = sid in VARIANTS
        arm = ARM if targeted else V1
        out = root / "analysis/freeflow/personality-eval-bv1/arms" / arm / "outputs" / LABEL / (sid + ".md")
        data = add(out, "analysis")
        binding = load(phase / ("bv1_bindings_luna_v1_targeted" if targeted else "bv1_bindings_luna_v1") / (sid + ".json"))
        need(binding == dict(source_sha256=sha, output_sha256=digest(data), evaluator_arm=arm),
             "BV1 binding: " + sid)
        originals = phase / "freeflow_bv1_luna_v1/attempt_responses" / (c["id_prefix"] + "_BV1_" + sid)
        need(bool(list(originals.glob("*.json"))), "original attempts absent: " + sid)
        if targeted:
            prov = json.loads(add(Path(str(out) + ".provenance.json"), "analysis"))
            ref = Path(prov["attempt_record"])
            need(len(ref.parts) == 2 and ref.parts[0] == c["id_prefix"] + "_BV1_" + sid
                 and ref.name.removesuffix(".json").isdigit(), "attempt reference")
            attempt = load(phase / "freeflow_bv1_luna_v1_targeted/attempt_responses" / ref)
            expected = dict(arm=ARM, evidence_rule="sentence", repair_note_sha256=NOTE,
                            sample_id=LABEL + "/" + sid + ".json", source_sha256=sha)
            need(all(attempt.get(k) == v for k, v in expected.items()) and
                 attempt.get("http_status") == 200 and attempt.get("qa_pass") is True and
                 attempt.get("qa_reason") == "", "variant attempt fields")
            need(data == (attempt["response"]["choices"][0]["message"]["content"].strip() + "\n").encode(),
                 "variant response mismatch")
            need(prov == dict(**expected, request_sha256=digest(json.dumps(attempt["request"], sort_keys=True).encode()),
                              output_sha256=digest(data), attempt_record=str(ref)), "variant provenance")
        outputs[LABEL + "/" + sid + ".json"] = str(out)
    rows = list(csv.DictReader(read(phase / "freeflow_bv1_luna_v1/sample_manifest.tsv").decode().splitlines(), delimiter="\t"))
    need(len(rows) == 125 and {r["sample_id"]: r["output_file"] for r in rows} == outputs, "BV1 manifest")
    # Preserve ALL phase data, including unsuccessful attempts and prior JSONL.
    for src in sorted(phase.rglob("*")):
        need(not src.is_symlink(), "phase symlink")
        if src.is_file():
            add(src, "analysis")
    aggregate = root / "analysis/freeflow/personality-aggregates" / LABEL
    for name in ("aggregate.md", "packet.md", "packet.metadata.json"):
        add(aggregate / name, "analysis")
    ready = phase / "QUEUE_ANALYSIS_READY.json"
    if not ready.exists():
        blockers.append("QUEUE_ANALYSIS_READY.json absent")
    else:
        r = load(ready)
        need(r.get("state") == "analysis_only_awaiting_review" and r.get("model") == SLUG
             and r.get("source_adoption") == c["source_adoption"]
             and r.get("raw_counts") == {"freeflow": 125, "values": 120}
             and r.get("bv1") == {"bv1": 125, "bv1_variant_arms": dict.fromkeys(VARIANTS, ARM)}
             and all(r.get(k) is False for k in ("publication_complete", "website_touched", "site_integration_performed")),
             "terminal readiness/variants mismatch")
    return dict(import_complete=not blockers, blockers=blockers, label=LABEL,
                scope="Evidence bundle only; no shared JSONL merge, editorial, release or site integration",
                entries=sorted(entries.values(), key=lambda e: e["destination"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", help="New direct child directory of colab-release-tools; only after complete")
    args = parser.parse_args()
    try:
        result = inspect()
        if args.bundle:
            need(result["import_complete"], "blocked; no bundle written")
            target = Path(args.bundle).absolute()
            need(target.parent == HOME and not target.exists(), "bundle must be new direct child of tools")
            # Check every byte again before creating anything.
            blobs = [(e, read(e["source"])) for e in result["entries"]]
            need(all(digest(b) == e["sha256"] for e, b in blobs), "source changed during inspection")
            target.mkdir()
            for e, data in blobs:
                dest = target / e["destination"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            (target / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return 0 if result["import_complete"] else 2
    except (ValueError, OSError, KeyError, sqlite3.Error) as exc:
        print(json.dumps({"import_complete": False, "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
