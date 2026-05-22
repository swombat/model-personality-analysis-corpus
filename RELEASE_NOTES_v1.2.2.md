# Release notes: v1.2.2

Date: 2026-05-22

## Summary

Adds the v2 freeflow posture coded layer under `analysis/freeflow/posture-coding/`.

This layer codes the relationship between each freeflow response and its speaker/writing posture, preserving full cell identity while also providing aggregate-model summaries for paper-level analyses.

## Included artifacts

- `analysis/freeflow/posture-coding/methodology/FREEFLOW_POSTURE_RUBRIC.md`
- `analysis/freeflow/posture-coding/methodology/AGGREGATION_RULES.md`
- `analysis/freeflow/posture-coding/data/freeflow_posture_manifest.jsonl`
- `analysis/freeflow/posture-coding/data/coder_outputs/*.jsonl`
- `analysis/freeflow/posture-coding/data/final/freeflow_posture_consensus.jsonl`
- `analysis/freeflow/posture-coding/data/final/cell_summary.csv`
- `analysis/freeflow/posture-coding/data/final/model_summary.csv`
- `analysis/freeflow/posture-coding/data/final/QA.md`

## Coverage

- 17,850 v2 freeflow samples
- 182 full cells
- 57 aggregate models after model-name aggregation (`grok-4-2`/`grok-4-20` combined)
- raw coding preserves full cell names for product-tier and route/cell analyses
- coding and non-coding models are kept separate

## Coders

Final triple-coder set:

- `qwen/qwen3.6-35b-a3b`
- `z-ai/glm-4.7`
- `google/gemini-2.5-flash-lite`

Kimi K2.6 passed the smoke test but returned empty outputs on full-length freeflow prompts and was replaced by Gemini 2.5 Flash Lite for the full run.

## QA headline

- total rows: 17,850
- unanimous: 9,319 (52.2%)
- majority: 8,395 (47.0%)
- no consensus: 136 (0.8%)
- incomplete: 0

Pairwise agreement:

- Gemini vs GLM: 64.8%
- Gemini vs Qwen: 62.8%
- GLM vs Qwen: 76.0%
