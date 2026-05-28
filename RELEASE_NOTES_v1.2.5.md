# Release notes: v1.2.5

Date: 2026-05-28

## Summary

Adds Claude Opus 4.8 (`opus-4-8`) to the analysis corpus and website data, based on the v1.2.4 raw corpus release.

## Added model

- `opus-4-8` / `claude-opus-4.8`

## Included analysis layers

- 125 BV1 per-sample freeflow personality readings for `opus-4-8-direct`, QA passing with zero known bad outputs.
- Deterministic freeflow marker tables updated; `opus-4-8-direct` has raw composite 537, register-stripped composite 421, and 4 topic-artifact-flagged samples.
- Per-cell aggregate packet and aggregate synthesis for `opus-4-8-direct`.
- Model-level personality card and rich profile for `claude-opus-4.8`.
- Rule-based values-probe extraction for `opus-4-8` from 120 values samples.
- Website generated data and sample bundle for `opus-4-8`; Astro build verified.

## Notes

The layered final values-probe consensus layer has not yet been extended for `opus-4-8`; the website therefore includes the rule-based values extraction and raw values samples, while the layered owned-values summary remains unavailable for this model.
