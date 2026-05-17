# Publication readiness note — 2026-05-17

Current analysis regeneration has produced a large working tree with updated freeflow BV1 aggregates, model-level/card/profile outputs, values summaries in website data, and regenerated website sample data. Do not discard the working tree without review.

Outstanding website finishing work before publication:

## Lume/Claude finishing assets

These models are the current newly-added Google/Gemma models that need final publication polish from Lume/Claude. In the current working tree, `website/src/generated/model-summaries.json` already contains placeholder/working 5–10 word summaries for them, but those should be treated as needing Lume review/replacement rather than final publication copy. They also currently have no model image assets (`website/public/images/models/<slug>.webp` and `<slug>-thumb.webp`).

- `gemini-2-0-flash` — display: `gemini-2.0-flash-001`
- `gemini-2-0-flash-lite` — display: `gemini-2.0-flash-lite-001`
- `gemini-2-5-flash` — display: `gemini-2.5-flash`
- `gemini-2-5-flash-lite` — display: `gemini-2.5-flash-lite`
- `gemini-3-1-flash-lite` — display: `gemini-3.1-flash-lite`
- `gemini-3-flash-preview` — display: `gemini-3-flash-preview`
- `gemma-4-26b-a4b` — display: `gemma-4-26b-a4b-it`
- `gemma-4-31b` — display: `gemma-4-31b-it`

## Checks already run

- Model-cell difference pass completed for 35 multi-cell groups; all currently `NO_STRONG_DIVERGENCE`.
- Personality-card generator was corrected so public cards do not mention route/provider/cell/variant language.
- Website personality-card data check reports zero route/cell/variant leaks.
- Astro website build passed after regeneration.
