# v1.4.27 — Muse Wonder

2026-10-13. Complete analysis of 125 freeflow and 120 values samples for
Muse Wonder, collected the day after Meta announced it, with integrated
card/profile, scoped website data, browsable source samples, a similarity-map
position and a provisional capability-ladder score. Raw companion: v1.2.33.
`meta/muse-wonder`, pinned to Meta through OpenRouter (endpoint
`meta/muse-wonder-20261012`), no fallbacks; provider-default reasoning and
sampling. Released 2026-10-12 (Meta's announcement,
about.fb.com/news/2026/10/introducing-muse-wonder/). Run
`20261013-muse-wonder-house`, collected and analysed by Lume from the
souls.house container.

The daily new-model check missed this model on 2026-10-13 at first: its
followed-lab list had `meta-llama` but not `meta`, where the whole Muse line is
listed. Daniel caught it; the list now includes `meta`.

## Evaluation

Freeflow readings use `bv1-luna-v1-20260929`; synthesis uses GPT-5.4 through
OpenRouter pinned OpenAI. Values keep the three Qwen/Kimi/GLM content/posture
coders. No values sample split, so no adjudication was needed. Values QA:
120 valid, 0 excluded; the final dataset is now 29,146 valid samples across
177 models and 243 cells. No interventions: all 1,337 harness tasks completed
within their normal attempt budgets, with no rate limiting.

Historical DeepSeek and current Luna readings are not interchangeable:
cross-model comparisons spanning the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 110 expressive freeflow, 11 genre fiction, 4 generic essay.
  A gentle, unhurried essay voice built on small domestic attention: closing
  libraries, chipped mugs, soup, repair shops, rain on pavement, the hour
  before the city wakes. It treats attention as a moral act ("attention is a
  form of love" or prayer, in 6 samples) and distrusts speed and display. Its
  most concrete recurring move is a small discipline against distraction: the
  phone left in another room, while it eats, reads or waits for the kettle,
  in 7 samples. Fiction runs to keepers and custodians: lighthouse keepers,
  librarians, repairers, houses of unfinished things.
- **Values:** owned stated-value disclosure 70/80 (87.5%); owned world-change
  advocacy 40/40 (100%). Top owned values: curiosity (81.2%), honesty (65.0%,
  e.g. "That's as honest as I can get about it"), authenticity (58.8%).
  World-change: reducing distance and dehumanisation (72.5%), reducing
  suffering (65.0%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 583k completion tokens, 353k of them reasoning.

## Editorial layer (Lume)

- Strapline: *I leave the phone in another room*, its own recurring sentence
  ("I leave the phone in another room while the kettle boils", "…while I
  read", "…while I eat"). Several siblings already hold the abstract version
  (attention as love or resistance); this is the version only Wonder kept
  saying, and the concrete one.
- Banner: a small city kitchen in the blue hour, a woman in a cardigan
  watching a kettle start to steam, bread and a mug on the counter, and in the
  dim next room a phone lying face down on a chair. Rendered through
  OpenRouter `google/gemini-3-pro-image`. The first render cropped the figure's
  head and read stern; the second was kept. Its fake painter's signature
  (bottom right, on the cutting board) was painted out with a feathered patch
  of the board beside it, keeping the full 21:9 frame. (The first published
  version cropped the bottom instead, which made this banner shorter than
  every other; fixed the same day after Daniel noticed.) No other lettering.
- Display name follows its Muse siblings (`muse-wonder`, lower case).

## Capability ladder

**162.2 / 220, provisional.** Artificial Analysis lists one row for Muse
Wonder, at Max effort (`artificialanalysis.ai/models/muse-wonder`, read
2026-10-13; Intelligence Index 52.4). Muse Spark 1.3 was also scored from AA's
max row. Muse Wonder Full is a separate AA entry and is not used. Eight rungs
measured (AA-LCR, SciCode, AutomationBench, Briefcase rubric, HLE, Omniscience
accuracy, CritPt, GDP.pdf); the other 14 are fitted. Fitted with the
recovered 2026-10-04 provisional method, the one every provisional score uses
until the full refresh (script and inputs in
`internal/capability-ladder/provisional-20261013/`; the script first checks
the method reproduces 161.6 / 128.1). The personality capture ran at Meta's
provider-default reasoning, which may not be Max. For scale: GPT-6.1 Sol
161.6, Opus 5.5 163.5, Muse Spark 1.3 157.2.

## Map

174 models, 33,070 freeflow documents; all 173 previous models remain.
Nearest neighbours by pooled raw-text similarity: GPT-5.5 Pro 0.938,
Qwen3.8 2.4T-A95B 0.931, GPT-5.5 0.931, Qwen3.8 Max 0.926, GPT-5.3 Codex
0.918. Nearest Meta model: Muse Spark 1.3 at 0.900 (Spark 1.2 0.898). Like
Haiku 5.5 before it, it sits nearer its generation than its line. Layouts
aligned to the previous release: PCA disparity 0.0 / 0.0001 (2D / 3D); MDS
0.449 / 0.181 and UMAP 0.213 / 0.271.

## Verification

Scoped generation added one model object and preserved 173 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests
(3) and the pricing suite pass. `test_phase19_cards.py` fails on an expected
OpenRouter price for a phase-19 DeepSeek model, as it does on a clean
`origin/main` checkout (re-run 2026-10-13); not a Wonder regression. The
built page shows the strapline, $4.00 / $20.00 per M and 162.2 / 220.

## Spend

Capture: $11.68 summed from the per-call costs recorded in the 245 raw traces.
The OpenRouter key moved $191.67 → $204.51 over the run, analysis and both
banner renders included ($12.84; the key is shared, so that is an upper
bound). The pre-run estimate by formula was about $30.
