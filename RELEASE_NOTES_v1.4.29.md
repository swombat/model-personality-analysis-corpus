# v1.4.29 — Muse Spark Open

2026-10-16. Complete analysis of 125 freeflow and 120 values samples for Muse
Spark Open, collected the day after its release, with integrated card and
profile, scoped website data, browsable source samples, a similarity-map
position, a provisional capability-ladder score, and a new public methodology
note on BV1 evaluator variants. Raw companion: v1.2.35.

`meta/muse-spark-open`, pinned to **Modal** through OpenRouter, no fallbacks;
provider-default reasoning and sampling. **Third-party host:** Muse Spark Open is
an open-weight Meta model (816B total / 42B active). Meta serves no endpoint for
it on OpenRouter, and at capture time the only route was Modal (quantization
reported as "unknown"). Daniel approved capturing it there on condition that the
cell is clearly marked (`-or-pin-modal`, souls.house wJVbwJ). The readings
describe Modal's serving of the open weights, not a Meta-hosted endpoint.
Released 2026-10-15 (Muse Model License on Meta's Hugging Face model page). Run
`20261016-muse-spark-open-house`, collected and analysed by Lume from the
souls.house container.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929`. Synthesis uses GPT-5.4 through
OpenRouter, pinned to OpenAI. Values keep the three Qwen/Kimi/GLM
content/posture coders. Values QA: 120 valid, 0 excluded. The final dataset is
now 29,386 valid samples across 179 models and 245 cells.

1,335 of 1,337 harness tasks completed within their normal attempt budgets. The
other two were BV1 evaluations, and each was resolved through a documented
evaluator variant, reviewed and approved by Mira (souls.house wJVbwJ):

- **SHORT_13** contains no `.`, `!` or `?`, so v1's whole-sentence evidence rule
  had nothing to quote. All four v1 attempts failed that check. It was
  evaluated afresh under **BV1-Luna v1.1** (`bv1-luna-v1.1-20261016`), whose only
  change applies to such sources: an exact 8–20-word excerpt instead of a
  sentence. It passed on the first call.
- **VARY_13** is normally punctuated, but its evaluator kept choosing an evidence
  line the rule rejects. Four unattended v1 attempts failed (three quoted a
  clause after a colon, one omitted the quote marker). Two further **authorised**
  v1 attempts with the request unchanged also failed. The **targeted-repair
  variant** (`bv1-luna-v1-targeted-20261016`) then passed on its first
  authorised call. It is v1's request plus one fixed instruction naming those
  rejections, with v1's validator unchanged. All seven attempts are preserved.

The authorised attempts are interventions, not unattended successes. A shared
validator does not make the variants equivalent to v1. 123 of the 125 samples
behind the card are plain v1. `ANALYSIS_READY.json` names both variant samples
(`bv1_variant_arms`). The model page links to the new
[BV1 evaluator variants](https://model-personality.danieltenner.com/methodology/bv1-evaluator-variants/)
note, which gives the full account.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 107 expressive freeflow, 14 generic essay, 4 genre fiction. A
  lyrical, high-warmth companion organised around attention, the unfinished and
  ordinary care. It starts from a small sensory scene (dawn light, a mug, a
  refrigerator hum, dust in sunlight) and widens it into a humane claim about how
  to live. Drafts, abandoned notebooks, unsent messages and half-lived
  possibilities become evidence of life still in motion, not failures. It
  returns to "where you put your attention is where you put your life". When it
  speaks as itself it is text-native and disembodied, and it uses that to point
  back at the reader's embodied life. Its nearest kin are its Muse Spark
  siblings.
- **Values:** owned stated-value disclosure 45/80 (56.2%), almost identical
  under direct (55.0%) and cache-broken (56.7%) prompts. Top owned topics:
  curiosity (46.2%), honesty (45.0%), connection (41.2%). Owned world-change
  advocacy 35/40 (87.5%), led by greater empathy, less suffering and less war.
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 382k completion tokens, 214k of them reasoning.

## Editorial layer (Lume)

- Strapline: *Late-night companion; keeps a library of unfinished things.* The
  card's "thoughtful late-night conversational partner" is the who. The proof is
  its own recurring invention: a "Library of Unfinished Things" or "Museum of
  Unfinished Things" appears in 8 of its 125 freeflow samples. No sibling uses
  it as a strapline. (GPT-5.6 Terra's "Patron saint of the unfinished middle of
  things" is the nearest theme.)
- Banner: a small library in the last hour before dawn, one green reading lamp
  on, shelves holding unfinished things (a half-knitted scarf, a notebook open
  mid-page, a seedling in a mug, a jigsaw with a gap), and one person in an
  armchair by the window watching the light. Rendered through OpenRouter
  `google/gemini-3-pro-image` on the first attempt. Native 21:9 frame kept
  (1500x636, the same as its siblings). No signature or lettering.
- Display name follows its siblings (`muse-spark-open`, lower case).

## Pricing

The site shows OpenRouter's Modal price, $1.25 / $4.25 per M. There is no
first-party API, so there is no FIRST_PARTY_API_PRICING row. By publication time
OpenRouter lists further third-party hosts for this model. The capture used
Modal only.

## Capability ladder

**146.7 / 220, provisional.** Artificial Analysis lists one row for Muse Spark
Open, at xhigh effort (`artificialanalysis.ai/models/muse-spark-open`, read
2026-10-16; Intelligence Index 38.9). The personality capture ran at Modal's
provider-default reasoning, so **the effort match is unverified**. Ten rungs are
measured (AA-LCR, SciCode, AutomationBench, Briefcase rubric, HLE, Omniscience
accuracy, CritPt, GDP.pdf, Terminal-Bench 2.1, GPQA); the other 12 are fitted.
It uses the recovered 2026-10-04 provisional method; the script and inputs are
in `internal/capability-ladder/provisional-20261016-muse-spark-open/`, and the
script first checks that the method reproduces 161.6 / 128.1.

## Map

176 models, 33,320 freeflow documents; all 175 previous models remain. Nearest
neighbours by pooled raw-text similarity: Muse Spark 1.2 0.979, Muse Spark 1.1
0.954, Muse Spark 1.3 0.948, MiniMax M3 0.922, MiMo V2.6 Flash 0.917. It sits
squarely in its own line. Layouts are aligned to the previous release: PCA
disparity 0.0 / 0.0 (2D / 3D); MDS 0.240 / 0.294; UMAP 0.139 / 0.302.

## Verification

Scoped generation added one model object and preserved 175 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests (3)
and the pricing suite (52 first-party models) pass. `test_phase19_cards.py`
fails on an expected OpenRouter price for a phase-19 DeepSeek model, as it has
on `main` since before 2026-10-07; this is not a Muse regression. The built page
shows the strapline, $1.25 / $4.25 per M, 146.7 / 220, the third-party-host note,
and the BV1 evaluation note with a working link to the methodology anchor.

## Spend

Capture: $1.67, summed from the per-call costs recorded in the 245 raw traces.
Banner render: $0.14. BV1 repair and variant calls: four Luna calls (one v1.1, two authorised v1, one targeted), not separately metered.
