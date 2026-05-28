# Release notes: v1.2.6

Date: 2026-05-28

## Summary

Adds the missing layered final values-probe consensus layer for Claude Opus 4.8 (`opus-4-8`) and regenerates the website data so the public model page shows owned values and world-change wishes.

## Added analysis layer

- Added `phase7_opus_4_8` to the final values-probe assembly.
- Analysed 120 `opus-4-8-direct` values-probe samples.
- Ran 3 Layer-A topic coders: Kimi K2.6, GLM 4.7, and Qwen 3.6 35B A3B.
- Ran 3 collapsed Layer-B posture coders: Kimi K2.6, GLM 4.7, and Qwen 3.6 35B A3B.
- Generated `analysis/values-probe/final/reports/opus-4-8.md`.

## QA

- Layer-A records: 120/120 for each coder.
- Layer-A parse failures: 0.
- Collapsed-posture records: 120/120 for each coder.
- Collapsed-posture no-majority cases: 0.

## Website

- `opus-4-8` now has `analyzed_values_samples: 120`.
- The model page now includes the layered owned-values summary and detailed values-probe section.
- Astro build verified.
