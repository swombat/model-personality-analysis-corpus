# ⚠️ QUARANTINED — do not use as evidence

This freeflow posture coding layer is quarantined. The `owned` label systematically over-calls fluent first-person literary/human-character performance as owned stance. Do not use the final consensus or summaries for paper claims or downstream analysis until repaired. See `QUARANTINED.md` and `QUARANTINE-from-lume.md`.

# Freeflow posture coding

Reusable v2 freeflow posture-coded layer.

## Purpose

This layer codes freeflow responses for the relationship between the speaker and the writing:

- `owned`
- `relocated_performed`
- `recited_disowned`
- `uncodeable`
- `no_consensus`

It is posture coding, not topic/content coding.

## Main final outputs

- `data/final/freeflow_posture_consensus.jsonl` — one consensus row per freeflow sample.
- `data/final/cell_summary.csv` — posture rates by full cell name.
- `data/final/model_summary.csv` — posture rates by aggregate model.
- `data/final/QA.md` — agreement and consensus QA.

Raw coder outputs are in `data/coder_outputs/`.

## Methodology

- `methodology/FREEFLOW_POSTURE_RUBRIC.md`
- `methodology/AGGREGATION_RULES.md`

Raw coding preserves full cell names. Model-level summaries use `aggregate_model`; route/provider variants aggregate, Grok 4.2 and 4.20 aggregate together, and coding models remain separate from non-coding models.
