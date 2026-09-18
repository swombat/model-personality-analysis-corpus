#!/usr/bin/env python3
"""Validate semantic record identity, taxonomy, chain separation and vote support."""
import importlib.util
import json
import sys
from collections import Counter
from run import PHASE, LAYERED, CODERS, MANIFEST, rows, coverage


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    layer = module("phase36_layer_a", LAYERED / "run_layer_a_coders.py")
    posture = module("phase36_posture", LAYERED / "run_posture_coder_collapsed.py")
    manifest = {r["layered_id"]: r for r in rows(MANIFEST)}
    expected = set(manifest)
    per = {}
    evidence_warnings = []
    for folder in ["layer_a", "posture_collapsed"]:
        coverage(PHASE / folder, expected)
        for coder in CODERS:
            data = rows(PHASE / folder / f"{coder}.jsonl")
            per[folder, coder] = {r["layered_id"]: r for r in data}
            if folder == "layer_a":
                attempts = rows(PHASE / folder / f"{coder}.attempts.jsonl")
                assert {r["layered_id"] for r in attempts if r.get("raw_text", "").strip()} >= expected
            for rec in data:
                source = manifest[rec["layered_id"]]
                assert rec["coder_key"] == coder
                assert rec["coder_model"] == layer.CODERS[coder]
                for key in ["model", "condition", "processing_chain"]:
                    assert rec[key] == source[key], (rec["layered_id"], key)
                if folder == "posture_collapsed":
                    assert rec["primary_label"] in posture.LABELS
                    assert rec["value_holding"] == posture.HOLDING[rec["primary_label"]]
                    assert rec["raw_text"].strip()
                    continue
                chain = source["processing_chain"]
                assert not rec["value_topics" if chain == "world_change_wishes" else "wish_topics"]
                for field, allowed in [("value_topics", layer.VALUE_TOPICS), ("wish_topics", layer.WISH_TOPICS)]:
                    for topic in rec[field]:
                        assert topic["topic_key"] in allowed
                        span = topic.get("evidence_span", "")
                        assert isinstance(span, str) and span.strip()
                        if " ".join(span.split()) not in " ".join(source["response"].split()):
                            evidence_warnings.append({"coder": coder, "layered_id": rec["layered_id"],
                                                      "topic": topic["topic_key"], "span": span})
    for rec in rows(PHASE / "layer_a/consensus_300.jsonl"):
        assert set(rec["eligible_coders"]) == set(CODERS)
        field = "wish_topics" if rec["processing_chain"] == "world_change_wishes" else "value_topics"
        for topic in rec[field]:
            voters = {c for c in CODERS if topic["topic_key"] in
                      {t["topic_key"] for t in per["layer_a", c][rec["layered_id"]][field]}}
            assert len(voters) >= 2 and voters == set(topic["supporting_coders"])
    for rec in rows(PHASE / "posture_collapsed/consensus.jsonl"):
        votes = Counter(per["posture_collapsed", c][rec["layered_id"]]["primary_label"] for c in CODERS)
        assert dict(votes) == rec["collapsed_primary_label_votes"]
        assert rec["collapsed_primary_label_support"] == votes[rec["collapsed_primary_label"]]
    (PHASE / "evidence-span-warnings.json").write_text(json.dumps(evidence_warnings, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: identities, taxonomy, chain separation, coder evidence and consensus votes. "
          f"Non-verbatim evidence spans for review: {len(evidence_warnings)}")


if __name__ == "__main__":
    main()
