# v1.4.18 — Sonnet 5.5 and a versioned BV1 evaluator migration

2026-09-29. Complete Sonnet 5.5 analysis: all 125 freeflow readings use the
new `bv1-luna-v1-20260929` arm, with a GPT-5.4 synthesis, card and rich profile;
all 120 values samples have the unchanged three-coder content/posture pipeline
and are integrated into the canonical final dataset and combined card.

## Migration, not a silent repair

GPT-6 Luna through OpenRouter, OpenAI pinned/no fallbacks, temperature .2,
8192-token ceiling, provider-default reasoning. Explicit source/evaluator masking,
reinforced exact-sentence instruction and stricter quotation/heading/label QA
are part of this version. This is not identical to legacy DeepSeek BV1.
The synthesis model/prompt/budget remain GPT-5.4; transport here is OpenRouter
pinned OpenAI rather than the legacy direct API. Historical cross-model
comparisons spanning the change are confounded. No older model is re-evaluated.

[Decision and limitations](internal/methodology/bv1-validation-20260929/DECISION.md)
includes 28 requests per candidate (20 natural sources, four fixtures, four
repeats), revised-arm retests, retained failures and a single-AI-review caveat.
Minimal low-signal fixtures still fail the legacy length gate: no blanket
automatic-reliability claim. Production: 117 first-pass, seven second-pass, one
third-pass successes; all nine rejected attempts retained, no budget resets.
Old 124 valid DeepSeek readings and failed LONG_24 evidence remain untouched;
none are mixed into the new synthesis. Raw source hashes are unchanged.

## Website/editorial boundary

Scoped Sonnet page data and 245-sample browser bundle are included; other cached
model objects are preserved exactly. Draft strapline and methodology caveat are
present. The pooled-raw-output similarity map includes Sonnet, regenerated from
all existing committed sample bundles plus the new bundle; eight map tests pass.
Lume's finishing work: editorial review/banner, visual review and production
deployment. No deployment is claimed.
Global website regeneration here would drop older uncommitted canonical values
identified in v1.4.17 notes; that unrelated Mac work was not copied or overwritten.
See `internal/methodology/bv1-validation-20260929/HANDOFF-LUME.md`.

## Cumulative archive

The previous actual GitHub/Zenodo analysis release was v1.3.3
(10.5281/zenodo.21802241), not the latest prepared notes v1.4.17. This release
archives all intervening tracked repository work too; it does not claim those
prepared versions were individually archived or retrospectively revalidated.
