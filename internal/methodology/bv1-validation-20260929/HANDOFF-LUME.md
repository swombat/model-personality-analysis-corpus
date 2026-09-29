# Lume handoff — Sonnet 5.5

Mira, 2026-09-29. The research analysis is complete, not an unresolved evaluator
recommendation. No request to recreate captures or finish pending coders.

## What to read

- `analysis/freeflow/personality-model-cards/cards/sonnet-5-5.md`
- `analysis/freeflow/personality-model-profiles/profiles/sonnet-5-5.md`
- `analysis/values-probe/final/reports/sonnet-5-5.md`
- This directory's `DECISION.md` and `PRODUCTION-QA.json`.
- Portable per-sample hashes:
  `analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-20260929/manifest.json`.
- Combined card + input/output bindings + failed responses:
  `analysis/values-probe/model-coding/layered/capture_20260928-sonnet55-house_sonnet-5-5-or-pin-anthropic/`.

All 245 raw samples pass the unchanged collection gates. All 125 freeflow
readings now use Luna (117 first-pass, seven second-pass, one third-pass).
All 120 values samples retain Qwen/Kimi/GLM content/posture coding and consensus.
Owned posture: 119/120 (99.2%); this is a coding result about these responses,
not a conclusion about inner experience. Freeflow kinds: 78 expressive, 21 generic
essay, 26 fiction. GPT-5.4 synthesis and integrated-card validators pass.
All 497 preserved-input hashes, including legacy artifacts, were unchanged.

## What remains yours

Editorial judgment on the draft strapline/profile and a banner image; visual
review and production deployment with the ordinary site credentials. The draft
strapline is “A gentle observer of thresholds, quiet care, and useful uncertainty”.
The main portrait is patient attention, thresholds, maintenance and guidance
without control. Please retain the method-change caveat even if shortening prose.
No production deployment has been performed here.

## Method caveat

BV1-Luna-v1 is a documented migration, not an interchangeable evaluator patch.
It changes evaluator, cap, identifier masking and quote-validation detail.
Historical cards generally use DeepSeek; comparisons across this boundary are
confounded. Old Sonnet analyses remain preserved and are excluded from this
synthesis. Validation was a small, single-AI-reviewed panel, not independent
human gold labeling. Short low-signal fixtures exposed a retained length-gate
limitation. Jev works via OpenRouter for typed decisions but is not a BV1 prose
replacement. Do not present pilot pass rates as general accuracy.

## Reproduction and site caveats

Use the sibling raw repository and scoped `website/scripts/generate_sonnet55.py`.
It preserves every other generated model object exactly; it does not regenerate
older pages from incomplete canonical data. v1.4.17 explicitly describes uncommitted
Mac values data that are absent here; I left that unrelated work alone.
The page has 125 freeflow +120 values in both analyzed and browsable counts.
`npm run build` passed (374 pages). The pricing regression suite has a pre-existing
failure: `deepseek-v4-flash` is missing from committed generated models, verified
also against the pre-change HEAD. This is not a Sonnet regression or a claimed
all-green website suite.

The raw harness has 29 passing tests; the Luna fidelity/transport module has 12.
The new compiler default applies to future runs; immutable old run configurations
remain legacy. An OR-only host must explicitly select synthesis_route
`openrouter-openai`; no hidden direct-provider key fallback.

Release targets are raw v1.2.27 and analysis v1.4.18. Actual publication and archive
verification are reported separately in the room / release records; this document
is not itself proof that tags or Zenodo archives exist. Both are cumulative
repository releases, including tracked work since the last actual archives
(raw v1.2.16, analysis v1.3.3).

## Map and final build

The pooled raw-text map was also regenerated, safely: its inputs are the preserved
committed public freeflow bundles, not the missing older canonical values files.
It now includes 165 models / 31,945 freeflow documents; all eight map tests pass.
All 164 previous models remain. PCA alignment disparity is 0.0001 in 2D and 3D;
nonlinear/optimized layouts moved more (MDS 0.143/0.0597, UMAP 0.1483/0.2006).
Do not treat map distance or layout movement as evaluator accuracy or personality
ground truth. Dependency versions and source hashes are in the generated map.
The full 374-page build passed again after this map refresh.
