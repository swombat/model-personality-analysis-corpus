# Freeflow posture aggregation rules

Date frozen: 2026-05-22

## Raw unit

The raw coding unit is the full freeflow cell/sample:

- `freeflow_id`
- `cell`
- `sample_id`
- `source_path`

Every raw coder record and consensus row must preserve the full cell name. Do not overwrite cell-level identity during coding.

## Aggregation key

For model-level analysis, aggregate cell-level rows using `aggregate_model`.

General rule: endpoint/provider/route variants of the same model aggregate together, while coding models and non-coding models remain separate.

Examples:

- `gpt-4o-direct-16k`, `gpt-4o-or`, and `gpt-4o-or-pin-openai` aggregate to `gpt-4o`.
- `grok-4-2-*` and `grok-4-20-*` are treated as the same underlying model/name variant and aggregate to `grok-4-20`.
- `glm-4-6-coding-direct` aggregates to `glm-4-6-coding`, **not** `glm-4-6`.
- `glm-5-1-coding-direct` aggregates to `glm-5-1-coding`, **not** `glm-5-1`.

## Reporting levels

Report posture at:

1. sample level (`freeflow_posture_consensus.jsonl`);
2. cell level (`cell_summary.csv`);
3. aggregate-model level (`model_summary.csv`).

The `values-under-fire` robustness scatterplot should use aggregate-model rates, with cell-level rates available for audit and product-tier reuse.
