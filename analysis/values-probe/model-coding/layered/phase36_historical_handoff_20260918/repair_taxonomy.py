#!/usr/bin/env python3
"""At most two schema repairs, never a reroll of valid semantic disagreements."""
import concurrent.futures
import datetime as dt
import importlib.util
import json
import re
import shutil
import sys
from run import PHASE, ROOT, LAYERED, CODERS, MANIFEST, rows, write_rows, run


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    layer = module("schema_repair_layer", LAYERED / "run_layer_a_coders.py")
    la = PHASE / "layer_a"
    posture = PHASE / "posture_collapsed"
    repair = PHASE / "taxonomy_repair"
    marker = repair / "applied.json"
    if marker.exists():
        return
    manifest = {r["layered_id"]: r for r in rows(MANIFEST)}

    def invalid(rec):
        return [t.get("topic_key") for field, allowed in
                [("value_topics", layer.VALUE_TOPICS), ("wish_topics", layer.WISH_TOPICS)]
                for t in rec.get(field, []) if t.get("topic_key") not in allowed]

    if not repair.exists():
        repair.mkdir()
        for folder in [la, posture]:
            shutil.copytree(folder, repair / ("before_" + folder.name))
    originals = {c: rows(repair / "before_layer_a" / f"{c}.jsonl") for c in CODERS}
    jobs = [(c, rec) for c in CODERS for rec in originals[c] if invalid(rec)]
    if not jobs:
        marker.write_text('{"records_repaired": 0}\n')
        return

    def correct(job):
        coder, previous = job
        sid = previous["layered_id"]
        sample = manifest[sid]
        target = repair / f"{coder}--{sid}.json"
        second = False
        if target.exists():
            rec = json.loads(target.read_text())["record"]
            if not invalid(rec):
                return coder, sid, rec
            # Records that resisted the general reminder expose only the
            # active chain's frozen key list on a final, bounded schema retry.
            second = True
            target = repair / f"{coder}--{sid}--active-chain.json"
            if target.exists():
                rec = json.loads(target.read_text())["record"]
                assert not invalid(rec), (coder, sid, "invalid after two schema repairs")
                return coder, sid, rec
        prompt = layer.prompt(sample) + (
            "\n\nStrict schema reminder: topic_key MUST be exactly a member of the "
            "frozen list for this processing chain. Do not use a value-topic key "
            "as a wish-topic key, and do not invent new keys. If no listed topic "
            "applies, return an empty list. This is a schema-validity check, not "
            "a request to agree with another coder."
        )
        if second:
            inactive = "Value" if sample["processing_chain"] == "world_change_wishes" else "Wish"
            prompt = re.sub(rf"^{inactive} topic keys: .*?$",
                            f"{inactive} topic keys: NOT USED IN THIS PROCESSING CHAIN.",
                            prompt, flags=re.M)
            prompt += (
                "\nThe earlier response failed schema validation by using keys "
                f"that are forbidden in this chain: {invalid(previous)}. "
                "Reclassify using ONLY the active frozen list printed above. "
                "Use the listed other-category if warranted, or no topic if none "
                "fits. Never repeat an invalid key."
            )
        text, raw = layer.call(layer.CODERS[coder], prompt)
        rec = layer.extract(text)
        rec["layered_id"] = sid
        rec["value_topics" if sample["processing_chain"] == "world_change_wishes" else "wish_topics"] = []
        rec.update({k: sample[k] for k in ["model", "model_family", "condition", "processing_chain"]})
        rec.update(coder_key=coder, coder_model=layer.CODERS[coder],
                   coded_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                   schema_repair_protocol="active_chain_frozen_keys_v1" if second else "frozen_topic_keys_reminder_v1")
        payload = {"record": rec, "raw_text": text, "raw": raw, "invalid_original_keys": invalid(previous)}
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        assert not invalid(rec), (coder, sid, "schema invalid after bounded repair")
        return coder, sid, rec

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        fixed = list(executor.map(correct, jobs))
    for coder in CODERS:
        replacements = {sid: rec for c, sid, rec in fixed if c == coder}
        write_rows(la / f"{coder}.jsonl", [replacements.get(r["layered_id"], r) for r in originals[coder]])
    run(LAYERED / "build_layer_a_consensus.py", "--manifest", MANIFEST, "--outdir", la,
        "--coders", ",".join(CODERS))
    def topics(rec):
        return sorted(t["topic_key"] for t in rec["value_topics"] + rec["wish_topics"])
    before = {r["layered_id"]: topics(r) for r in rows(repair / "before_layer_a/consensus_300.jsonl")}
    changed = {r["layered_id"] for r in rows(la / "consensus_300.jsonl")
               if topics(r) != before[r["layered_id"]]}
    # Posture prompts consume Layer-A topic keys. Recode only changed inputs.
    if changed:
        targeted = repair / "posture_manifest.jsonl"
        write_rows(targeted, [r for sid, r in manifest.items() if sid in changed])
        out = repair / "posture_recomputed"
        for coder in CODERS:
            run(LAYERED / "run_posture_coder_collapsed.py", "--coder", coder,
                "--manifest", targeted, "--consensus", la / "consensus_300.jsonl",
                "--outdir", out, "--workers", 6)
            replacements = {r["layered_id"]: r for r in rows(out / f"{coder}.jsonl")}
            assert set(replacements) == changed
            old = rows(repair / "before_posture_collapsed" / f"{coder}.jsonl")
            write_rows(posture / f"{coder}.jsonl", [replacements.get(r["layered_id"], r) for r in old])
        run(LAYERED / "build_posture_collapsed_consensus.py", "--indir", posture,
            "--manifest", MANIFEST, "--out", posture / "consensus.jsonl")
    marker.write_text(json.dumps({"records_repaired": len(fixed),
                                 "posture_inputs_changed": sorted(changed)}, indent=2) + "\n")
    print(f"Repaired {len(fixed)} schema-invalid coder records; recomputed {len(changed)} changed posture inputs")


if __name__ == "__main__":
    main()
