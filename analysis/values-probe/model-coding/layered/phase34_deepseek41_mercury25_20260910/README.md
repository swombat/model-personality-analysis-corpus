# Phase 34 — DeepSeek V4.1 Flash and Inception Mercury 2.5

Completed mapping on 2026-09-10. Publication of website pages is pending Lume's editorial image/strapline work.

- Raw: 125 freeflow + 120 values per model; all 490 pass strict final-answer, exact identity, upstream and stop-finish audit.
- OpenRouter pinned to DeepSeek and Inception; fallbacks disabled, default reasoning retained.
- BV1: 250/250 QA-valid after targeted retries.
- Layer A: 3 coders × 240, complete consensus and no missing records.
- Posture: 3 coders × 240; seven initial splits independently adjudicated, six resolved.
- One remaining split: DeepSeek G2_30. Retained explicitly, not disguised as a majority. See unresolved_posture.json and LUME_HANDOFF.md.
- Complete isolated aggregates, cards, rich profiles, final values reports and legacy marker metrics.
- Original failed/ambiguous classifications and adjudication outputs preserved. Mercury's one provider-error raw response is preserved in the raw repository's discarded directory.

## Reproduction and custody

Collection manifest lives in corpus-v2. `audit_raw.py` checks the raw source; `run_freeflow_bv1.py` and `run_semantic_analysis.sh` reproduce the first pass. The latter intentionally fails on missing majority rather than silently approving it. `finish_classification.sh` records the bounded retry/adjudication pass; do not rerun adjudication simply to chase agreement. `validate_analysis.py` accepts exactly the one documented residual split, and no other unresolved cases. `build_aggregate_packets.py` and `assemble_models.py` update only these two models. Final values assembly explicitly retains the unresolved-classification warning.

The interrupted background stages and delayed follow-through are not evidence of continuous supervision. Completion was verified after interactive recovery.
