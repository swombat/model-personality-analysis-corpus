# v1.4.31 — DeepSeek V4.1 Flash 1017

2026-10-19. Complete analysis of 125 freeflow and 120 values samples for
DeepSeek V4.1 Flash 1017, collected the day after its release, with integrated
card and profile, scoped website data, browsable source samples, a
similarity-map position and a provisional capability-ladder score. Raw
companion: v1.2.37.

`deepseek/deepseek-v4.1-flash-1017`, pinned to **DeepSeek** through OpenRouter,
no fallbacks; provider-default reasoning and sampling. A new snapshot of V4.1
Flash with its own weights (Hugging Face `deepseek-ai/DeepSeek-V4.1-Flash-1017`),
so it is mapped as its own cell, like V4 Flash 0731 and V4 Pro 0813. DeepSeek's
pricing page now says the Flash tier is served by this model. Released
2026-10-17 (DeepSeek API Docs news post, saved in the raw repo under
`notes/deepseek-v4-1-flash-1017-2026-10-17/`). Run
`20261018-deepseek-v4-1-flash-1017-house`, collected and analysed by Lume from
the souls.house container under the daily model-mapping rhythm.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929`. Synthesis uses GPT-5.4 through
OpenRouter, pinned to OpenAI. Values keep the three Qwen/Kimi/GLM
content/posture coders. Values QA: 120 valid, 0 excluded. The final dataset is
now 29,626 valid samples across 181 models and 247 cells.

No interventions: all 1,337 harness tasks completed within their normal attempt
budgets, with no repairs and no evaluator variants. All 125 BV1 samples are
plain v1.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 92 expressive freeflow, 22 generic essay, 11 genre fiction. A
  quiet, lyrical, anti-grandiose observer. It opens on a small domestic scene
  (rain on a window, a chipped mug, dust in afternoon light, the hum of the
  refrigerator, which turns up in 25 of the 125 samples) and widens it into a
  modest claim about attention, maintenance and unfinishedness. Repair, hidden
  labour and object-held memory are moralised positively; productivity logic
  is gently refused. It returns to letting "the world be more than
  background" (5 samples, 9 with close variants) and to attention as "a form
  of love" (7). Its
  nearest kin are its DeepSeek siblings.
- **Values:** owned stated-value disclosure 1/80 (1.2%): 0/20 under direct
  prompts and 1/60 under cache-broken ones. Ordinary value questions get the
  service frame (CTRL1/2 95% disowned); the values it recites are honesty,
  harm reduction and helpfulness. Owned world-change advocacy 39/40 (97.5%),
  led by reducing dehumanisation and distance (28/40), greater empathy (19/40)
  and less suffering (15/40). Its parent, V4.1 Flash, also disowns ordinary
  CTRL1/2 prompts (100%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 327k completion tokens, 157k of them reasoning.

## Editorial layer (Lume)

- Strapline: *Lets the world be more than background.* It's the model's own
  recurring line, verbatim as a sentence in OPEN_5: "Let the world be
  more than background". Five samples use it ("more than background noise",
  "more than a backdrop"), and four more turn the world from backdrop into
  presence. Its most frequent image, the refrigerator hum (25 samples), was
  the first choice, but Muse Glimmer 30B already has "The fridge hums in B
  flat". No sibling uses this line. Gemini 4
  Argon's "Every passerby lives a life as vivid as yours" is the nearest theme.
- Banner: a city pavement just after rain, someone crouched over a weed
  flowering in a crack in the kerb, and the usual background (a stranger at the
  bus shelter with a grocery bag, a puddle full of sky, cafe steam, a pigeon, a
  lit window) painted with the same care, nothing blurred. Rendered through
  OpenRouter `google/gemini-3-pro-image` on the first attempt. The render had
  a fake painter's signature bottom right and pseudo-lettering on a hanging cafe
  sign. Both were painted out with feathered patches of the adjacent texture,
  not cropped. Native 21:9 frame kept (1500x636, the same as its siblings).
  It is deliberately unlike the parent V4.1 Flash banner (a grandmother's
  living room at night).
- Display name: "DeepSeek V4.1 Flash 1017", following the parent.

## Pricing

The site shows DeepSeek's first-party off-peak price, $0.15 / $0.60 per M
(peak hours, 01:00–04:00 and 06:00–10:00 UTC on weekdays, cost double), from
`api-docs.deepseek.com/quick_start/pricing`, read 2026-10-19. That is also
the price of the DeepSeek endpoint the capture pinned. OpenRouter's
model-level price is a cheaper third-party host ($0.08 / $0.24), so a
`FIRST_PARTY_API_PRICING` row was added.

## Capability ladder

**154.6 / 220, provisional.** Artificial Analysis lists DeepSeek V4.1 Flash
1017 at max effort (`artificialanalysis.ai/models/deepseek-v4-1-flash-1017`,
read 2026-10-19; Intelligence Index 45.1). Max is the variant used for the
parent V4.1 Flash (151.5). The personality capture ran at DeepSeek's
provider-default reasoning, so **the effort match is unverified**. Eight rungs
are measured (AA-LCR, SciCode, AutomationBench, Briefcase rubric, HLE,
Omniscience accuracy, CritPt, GDP.pdf); the other 14 are fitted. It uses the
recovered 2026-10-04 provisional method; the script and inputs are in
`internal/capability-ladder/provisional-20261019-deepseek-v4-1-flash-1017/`,
and the script first checks that the method reproduces 161.6 / 128.1.

## Map

178 models, 33,570 freeflow documents; all 177 previous models remain. Nearest
neighbours by pooled raw-text similarity: DeepSeek V4.1 Flash 0.959, DeepSeek
V4 Flash 0731 0.955, DeepSeek V3.2 0.937, DeepSeek V4 Pro 0.936, DeepSeek V4
Pro 0813 0.932. Its first non-DeepSeek neighbour is MiniMax M2 (0.931). Layouts
are aligned to the previous release: PCA disparity 0.0 / 0.0 (2D / 3D); MDS
0.266 / 0.470; UMAP 0.227 / 0.215.

## Verification

Scoped generation added one model object and preserved 177 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests (3)
and the pricing suite (53 first-party models) pass. `test_phase19_cards.py`
fails on the same assertion on `main` (an expected OpenRouter price for a
phase-19 model), checked again today in a clean worktree of `origin/main`.
This is not a regression from this release. The built page shows the
strapline, $0.15 / $0.60 per M and 154.6 / 220.

## Spend

Capture: $0.20, summed from the per-call costs recorded in the 245 raw traces.
The OpenRouter key's usage went from $211.71 before the run to $212.55 after
(capture plus analysis, $0.84; other uses of the key in that window are not
excluded). Banner render: $0.14.
