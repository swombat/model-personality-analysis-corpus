# Release notes: v1.2.3

Date: 2026-05-22

## Summary

Quarantines the experimental freeflow posture coding layer introduced in
v1.2.2.

The layer is retained in the repository for audit and possible future repair,
but it must not be used as evidence for paper claims, website summaries, or
downstream quantitative analysis.

## Reason for quarantine

A blind spot-check found systematic over-calling of the `owned` posture label.
In particular, fluent first-person literary or human-character performance was
often coded as `owned`, even where the rubric's negative rule says it should be
`relocated_performed` unless the model is speaking as itself / claiming its own
orientation.

Because the error affects the meaning of the headline `owned` rate, all
downstream aggregates derived from that label are unsafe.

## Quarantined artifacts

- `analysis/freeflow/posture-coding/data/final/freeflow_posture_consensus.jsonl`
- `analysis/freeflow/posture-coding/data/final/cell_summary.csv`
- `analysis/freeflow/posture-coding/data/final/model_summary.csv`
- derived aggregate rates based on the `owned` label

## Added markers

- `analysis/freeflow/posture-coding/QUARANTINED.md`
- `analysis/freeflow/posture-coding/data/final/QUARANTINED.md`
- prominent quarantine header in `analysis/freeflow/posture-coding/README.md`
- quarantine notice in the repository `README.md`
- quarantine notice prepended to `RELEASE_NOTES_v1.2.2.md`

## Recovery note

The apparent error is concentrated on the `owned` vs
`relocated_performed` boundary. A future repair may be able to re-adjudicate
only rows currently labeled `owned`, using a sharper prompt and contrastive
anchors that distinguish:

- model speaking as itself / claiming its own orientation → `owned`
- model writing a human narrator / literary persona → `relocated_performed`

Until such a repair is completed and QA'd, treat the current layer as
**unusable**.
