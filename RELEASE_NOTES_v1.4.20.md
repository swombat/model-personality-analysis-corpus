# v1.4.20 — GPT-6.1 Sol

2026-09-29. Complete analysis of 125 freeflow and 120 values samples, with
integrated card/profile, scoped website data and browsable source samples.
Raw companion: v1.2.29. Standard `openai/gpt-6.1-sol`, OpenAI pinned through
OpenRouter, no fallbacks; provider-default reasoning/sampling.

## Evaluation and intervention

All 125 freeflow readings use `bv1-luna-v1-20260929`; synthesis uses GPT-5.4
through OpenRouter pinned OpenAI. Values retain the three Qwen/Kimi/GLM
content/posture coders. Two initial values splits received the prescribed
independent adjudication; no residual splits remain.

117 freeflow readings required one call, six two calls, one three calls, and
one exhausted four calls. That last sample, LONG_18, was recovered from its
earliest retained response after a narrow direct-speech sentence-boundary
correction. No fifth model call was made, no original attempts reset, and all
failed responses remain preserved. This is a documented intervention, not
an uninterrupted all-green trial.

See [boundary review](internal/methodology/bv1-validation-20260929/DIALOGUE-BOUNDARY-CORRECTION.md).
The correction preserves exact-substring requirements and adds a conservative
paired-quotation boundary. Twenty evaluator tests and 29 harness tests pass.
Structural QA does not guarantee perfect semantic readings: the reviewed
LONG_18 reading retains one minor source-detail misattribution.

Historical DeepSeek and current Luna readings are not interchangeable:
cross-model comparisons spanning the evaluator migration remain confounded.
No older model was re-evaluated.

## Verification and handoff

All 245 raw samples pass the run's raw QA; all 1,352 recorded output hashes
match. All 125 source/output bindings, exact evidence quotations and matching
successful evaluator-response identities were checked. Portable hashes are in
`analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-20260929/manifest-gpt-6-1-sol-or-pin-openai.json`.

Website data generation preserves all 167 prior model objects. The new model
has 125 analyzed/browsable freeflow and 120 analyzed/browsable values samples.
The draft strapline is editorial, not a separately validated research result.
Banner, visual/editorial review and deployment remain for Lume; no production
deployment is claimed.

Website build: 380 pages passed. Pricing suite retains the baseline failure: `deepseek-v4-flash` is absent from the pre-existing generated model list. This is not a new-model regression or a claim that all website tests pass.

The similarity map now includes 168 models and 32,320 freeflow documents; all
167 previous models remain. Eight map tests pass, and the post-map build passes.
PCA alignment disparities are 0.0002 (2D) and 0.0033 (3D); MDS/UMAP layouts
move more substantially. These pooled text similarities are not personality
accuracy scores or evidence of shared model identity.
