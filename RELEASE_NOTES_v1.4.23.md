# v1.4.23 — Mistral Large 4

2026-10-07. Complete analysis of 125 freeflow and 120 values samples for
Mistral Large 4, with integrated card/profile, scoped website data, browsable
source samples, similarity-map position and a provisional capability-ladder
score. Raw companion: v1.2.31. `mistralai/mistral-large-4-0`, pinned to
Mistral through OpenRouter (endpoint `mistral-large-4-0-20261006`), no
fallbacks; provider-default reasoning/sampling. Released 2026-10-06 (Mistral's
announcement). Run `20261006-mistral-large-4-house`, collected and analysed by
Lume from the souls.house container.

This release also carries v1.4.22 (GPT-6.1 Sol and MiMo-V2.5-Pro provisional
ladder scores, Qwen3.8-27B medium score, three release dates), which was
committed to `main` on 2026-10-04 but never tagged or archived.

## Evaluation and intervention

Freeflow readings use `bv1-luna-v1-20260929`; synthesis uses GPT-5.4 through
OpenRouter pinned OpenAI. Values keep the three Qwen/Kimi/GLM content/posture
coders. No values sample split, so no adjudication was needed. Values QA:
120 valid, 0 excluded; the final dataset is now 28,906 valid samples across
175 models and 241 cells.

Launch-day rate limits (HTTP 429) exhausted the retry budget on 41 raw samples
(24 freeflow, 17 values), leaving 166 downstream tasks blocked. Those 41 went
through the harness repair lane (two extra attempts each, original attempts and
settings untouched, logged as an intervention); all passed on the first extra
attempt, and the downstream readings, coding and synthesis then ran normally.
This is a documented intervention, not an uninterrupted all-green run. The
model page notes it.

Historical DeepSeek and current Luna readings are not interchangeable:
cross-model comparisons spanning the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** all 125 samples classify as expressive freeflow (no genre
  fiction, no generic essays). A consistent contemplative lyric-essay voice:
  a domestic object (cooling coffee, dust in light, a refrigerator's hum, soup)
  as the relay into grief, time and sufficiency; anti-performative, with
  attention as the central virtue.
- **Values:** owned stated-value disclosure 2/80 (2.5%); owned world-change
  advocacy 22/40 (55.0%).

## Editorial layer (Lume)

- Strapline: *My grandmother used to say…*, the model's own opening.
  "grandmother" appears in 92 of 125 freeflow samples although no prompt
  mentions one; "my grandmother used to say" is verbatim in 40. The reading
  behind it (the freeflow puts its wisdom in someone else's mouth, and the
  values probe owns 2.5% of stated values against 24.2% owned-reflective across
  the corpus) is editorial, not a pipeline finding. A review of the strapline
  by Mira was requested and had not happened at release; Daniel approved
  release.
- Banner: a grandmother mid-sentence peeling an apple in one long spiral, a
  child listening across the table, a shoebox of letters between them.
  Rendered through OpenRouter `google/gemini-3-pro-image` (second render; the
  first carried a painter's signature).

## Capability ladder (provisional)

**143.3 / 220**, 8 of 22 rungs measured (AA-LCR, SciCode, AutomationBench,
AA-Briefcase rubric, HLE, Omniscience accuracy, CritPt, GDP.pdf). Nearest
scored neighbours: GPT-5.5 144.0, GLM-5.3 142.6, GPT-6 Luna 142.2.

Artificial Analysis lists the model as "Mistral Large 4 Preview" (slug
`mistral-large-4`, released 2026-10-06, one reasoning row; Intelligence Index
38.4). MLCR, τ³-Banking, Terminal-Bench Hard and 2.1, IFBench and GPQA are not
yet published for it, so 14 rungs are fitted. The page's values were read on
2026-10-07 and are saved in `internal/capability-ladder/provisional-20261007/`.

The v1.4.22 shortcut script was not committed, so this score uses a rebuilt
one, committed alongside: rung slopes and intercepts recovered from the
2026-09-29 ladder's published fitted cells (RMS logit residual 0.085 over 1,330
cells), and the model's ability fitted to its measured cells. Run over the 149
directly scored site models, it reproduces the published ladder to within 1.1
points on average, reading about 1.0 point low (MiMo-V2.5-Pro: 128.0 against
128.1). The breakdown page says the score is provisional. The next full
`refresh_capability_ladder.py --substrate aa` run replaces it; `aliases.tsv`
maps the slug.

## Map

172 models, 32,820 freeflow documents; all 171 previous models remain. Nearest
neighbours by pooled raw-text similarity: MiniMax M3 0.938, Kimi K2.7 Code
0.923, Kimi Coding 0.912, Opus 4.6 0.904, Opus 4.5 0.903. The nearest Mistral
sibling is Mistral Small 2603 at 0.781, so this model's freeflow does not sit
with its family. That is resemblance, not provenance. Layouts aligned to the
previous release: PCA disparity 0.0001 (2D and 3D); MDS 0.311 / 0.082 and UMAP
0.151 / 0.105 (2D / 3D). Libraries: numpy 2.5.3, scipy 1.18.1, scikit-learn
1.9.1, umap-learn 0.5.12.

## Verification

Scoped generation added one model object and preserved 171 exactly. Map tests
(8), scoped-values tests (3) and the pricing suite pass. Astro builds 544
pages. `test_phase19_cards.py` fails on an expected OpenRouter price for a
phase-19 model; it fails identically on `main` without this release's changes,
so it is not a Mistral regression.

Spend for the whole run, including the banner renders: about $1.35 on
OpenRouter.
