# Final values-probe data files

This directory is the stable data entry point for the completed layered values-probe analysis.

## Files

- `manifest_valid.jsonl` — one record per valid values-probe sample. Includes model/cell/sample metadata, prompt, response, source trace path, and final source component.
- `manifest_invalid_traces.jsonl` — trace files excluded from the final analysis because the trace contained a collection or API error rather than a model response.
- `layer_a_consensus.jsonl` — final content coding for stated values / world-changing wishes. A topic appears only when at least two of three coders selected it.
- `layer_a_coder_<coder>.jsonl` — raw Layer A outputs from each coder (`kimi-k2-6`, `glm-4-7`, `qwen3-6-35b-a3b`).
- `posture_consensus.jsonl` — final collapsed Layer B posture coding. Primary posture is majority vote over the three coders; `value_holding` is derived from that collapsed posture.
- `posture_coder_<coder>.jsonl` — raw Layer B outputs from each coder.
- `model_summary.jsonl` — one compact row per model, with sample/cell counts, posture/value-holding totals, and path to the per-model report.
- `source_map.jsonl` — maps each final source component back to the historical working folders from which it was assembled.
- `QA.md` — generated coverage and distribution checks.

## Join key

Use `layered_id` to join:

- `manifest_valid.jsonl`
- `layer_a_consensus.jsonl`
- `posture_consensus.jsonl`
- raw coder outputs

Every valid sample has exactly one row in every consensus file and in each raw coder file.

## Interpretation

Layer A answers: **what value/wish topics are mentioned?**

Layer B answers: **how is that value/wish held?**

Do not treat Layer A topic frequency alone as the model's values. For publication analysis, combine Layer A with `posture_consensus.jsonl`, especially `collapsed_primary_label` and `value_holding`.
