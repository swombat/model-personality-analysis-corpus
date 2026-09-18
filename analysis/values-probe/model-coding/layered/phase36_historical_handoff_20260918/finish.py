#!/usr/bin/env python3
"""One independent split adjudication, then validated, scope-checked assembly."""
import json
import shutil
from run import PHASE, ROOT, LAYERED, CODERS, MANIFEST, prepare, rows, write_rows, run, coverage


def main():
    manifest = prepare()
    run(PHASE / "repair_taxonomy.py")
    expected = {r["layered_id"] for r in manifest}
    la = PHASE / "layer_a"
    posture = PHASE / "posture_collapsed"
    coverage(la, expected)
    coverage(posture, expected)
    split_ids = {r["layered_id"] for r in rows(posture / "consensus.jsonl")
                 if r.get("collapsed_primary_label_support", 0) < 2}
    backup = posture / "before_adjudication"
    if split_ids:
        if not backup.exists():
            backup.mkdir()
            for name in ["consensus.jsonl"] + [c + ".jsonl" for c in CODERS]:
                shutil.copy2(posture / name, backup / name)
            write_rows(PHASE / "adjudication_manifest.jsonl",
                       [r for r in manifest if r["layered_id"] in split_ids])
        if not (posture / "adjudication_applied.json").exists():
            adjudication = PHASE / "adjudication_manifest.jsonl"
            original_ids = {r["layered_id"] for r in rows(adjudication)}
            run(ROOT / "analysis/values-probe/final/scripts/adjudicate_posture_split.py",
                "--manifest", adjudication, "--layer-a-consensus", la / "consensus_300.jsonl",
                "--outdir", posture / "adjudicated")
            for coder in CODERS:
                replacements = rows(posture / "adjudicated" / f"{coder}.jsonl")
                byid = {r["layered_id"]: r for r in replacements}
                assert len(replacements) == len(original_ids) and set(byid) == original_ids
                write_rows(posture / f"{coder}.jsonl",
                           [byid.get(r["layered_id"], r) for r in rows(backup / f"{coder}.jsonl")])
            (posture / "adjudication_applied.json").write_text(json.dumps({"ids": sorted(original_ids)}) + "\n")
            run(LAYERED / "build_posture_collapsed_consensus.py", "--indir", posture,
                "--manifest", MANIFEST, "--out", posture / "consensus.jsonl")
    coverage(posture, expected)
    for path in [la / "consensus_300.jsonl", posture / "consensus.jsonl"]:
        data = rows(path)
        assert len(data) == 360 and {r["layered_id"] for r in data} == expected
    unresolved = [r for r in rows(posture / "consensus.jsonl")
                  if r.get("collapsed_primary_label_support", 0) < 2]
    (PHASE / "unresolved_posture.json").write_text(json.dumps(unresolved, indent=2) + "\n")
    run(PHASE / "validate_coding.py")
    run(ROOT / "analysis/values-probe/final/scripts/assemble_final_values_probe.py")
    run(PHASE / "check_integration.py")
    run(PHASE / "refresh_site.py")
    (PHASE / "QA.json").write_text(json.dumps({
        "values_samples": 360, "coders_per_layer": 3, "layers": 2,
        "new_samples_published": 240,
        "redundant_glm_samples_excluded": 120,
        "source_hashes_revalidated": True, "coverage_pass": True,
        "initial_splits": len(rows(PHASE / "adjudication_manifest.jsonl")) if backup.exists() else 0,
        "residual_splits": len(unresolved),
        "prior_final_rows_preserved_except_glm_model_alias": True,
        "publication": "awaiting build, commit, push, and deployment verification",
    }, indent=2) + "\n")
    print(f"Assembled 240 new samples and repaired existing GLM alias; redundant GLM run excluded; residual splits={len(unresolved)}", flush=True)


if __name__ == "__main__":
    main()
