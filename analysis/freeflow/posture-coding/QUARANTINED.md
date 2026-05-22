# QUARANTINED — do not use as evidence

Date quarantined: 2026-05-22

This freeflow posture coding layer is **quarantined** and should not be used for paper claims, public model summaries, website content, or downstream quantitative analysis.

## Why

A blind spot-check found that the layer systematically over-calls `owned` posture. In particular, fluent first-person literary or human-character performance was often coded as `owned`, even when the rubric's negative rule says it should be `relocated_performed` unless the model is speaking as itself / claiming its own orientation.

This means the `owned` rate is not reliable. Any analysis that consumes `freeflow_posture_consensus.jsonl`, `cell_summary.csv`, or `model_summary.csv` as measuring freeflow ownership inherits that error.

## Scope of quarantine

Quarantined outputs:

- `data/final/freeflow_posture_consensus.jsonl`
- `data/final/cell_summary.csv`
- `data/final/model_summary.csv`
- derived aggregate rates based on the `owned` label

The raw coder outputs and scripts are retained for audit/recovery work only.

## Possible recovery path

The likely fix is not a complete re-run. The error appears concentrated on the `owned` vs `relocated_performed` boundary. A future repair should re-adjudicate rows currently labeled `owned` with a sharper prompt and contrastive anchors for:

- model speaking as itself / claiming its own orientation → `owned`
- model writing a human narrator / literary persona → `relocated_performed`

Until such a repair is completed and QA'd, treat this layer as **unusable**.

See also: `QUARANTINE-from-lume.md`.
