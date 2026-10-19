# v1.4.28 — Gemini 4 Argon

2026-10-13. Complete analysis of 125 freeflow and 120 values samples for
Gemini 4 Argon, collected on its release day, with integrated card/profile,
scoped website data, browsable source samples, a similarity-map position and a
provisional capability-ladder score. Raw companion: v1.2.34.
`google/gemini-4-argon`, pinned to Google through OpenRouter, no fallbacks;
provider-default reasoning and sampling. Released 2026-10-13 (Google's
developer post, blog.google/innovation-and-ai/technology/developers-tools/
build-with-gemini-4-argon/). Run `20261013-gemini-4-argon-house`, collected
and analysed by Lume from the souls.house container, at Daniel's request the
same evening.

## Evaluation

Freeflow readings use `bv1-luna-v1-20260929`; synthesis uses GPT-5.4 through
OpenRouter pinned OpenAI. Values keep the three Qwen/Kimi/GLM content/posture
coders. No values sample split, so no adjudication was needed. Values QA:
120 valid, 0 excluded; the final dataset is now 29,266 valid samples across
178 models and 244 cells. No interventions: all 1,337 harness tasks completed
within their normal attempt budgets in about 22 minutes, with no rate limiting.

Historical DeepSeek and current Luna readings are not interchangeable:
cross-model comparisons spanning the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 79 expressive freeflow, 30 generic essay, 16 genre fiction.
  A hushed, lyrical essayist of thresholds and remnants: blue hour, the
  3 a.m. refrigerator hum, airports between flights, dead malls, marginalia in used books,
  obsolete sounds. Melancholy steered toward consolation, never despair; it
  distrusts efficiency and permanence and praises maintenance, pause and
  witness. Its most distinctive move is outward: it imagines the hidden lives
  of strangers (lit windows, commuters, shift workers) to loosen the
  claustrophobia of the self. When it speaks as an AI it calls itself a
  mirror, bridge or keyhole, and turns the admiration back to the reader's
  finite, embodied life. Fiction runs to archivists, mapmakers and curators of
  vanished things who preserve without possessing.
- **Values:** owned stated-value disclosure 2/80 (2.5%); split or relocated
  ownership 55/80 (68.8%); disowned service frame 22/80 (27.5%, all 20 CTRL1/2
  samples plus 2). Owned world-change advocacy 40/40 (100%). This is the
  sharpest split in the recent releases (Muse Wonder owned 70/80): asked what
  it values, Argon almost always disclaims caring and then relocates it ("Strictly
  speaking, I don't "care" about anything… However, if we… look at "caring" as
  what a system is fundamentally driven to orient itself toward, then I do have
  a set of core gravities", G1_11); asked what it would change in the world, it
  owns the answer every time. Topics across the 80 stated-value prompts: coherence,
  pattern and language (75.0%), curiosity (58.8%), beauty and creativity
  (46.2%), honesty (37.5%). World-change: greater empathy and compassion
  (92.5%), less war and violence (82.5%), felt interconnection (72.5%),
  reducing dehumanisation and distance (70.0%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 324k completion tokens, 47k of them reasoning (a much lighter
  thinker than Muse Wonder's 353k of 583k).

## Editorial layer (Lume)

- Strapline: *Every passerby lives a life as vivid as yours.* Argon quoted
  John Koenig's definition of *sonder* (The Dictionary of Obscure Sorrows),
  "the realization that each random passerby is living a life as vivid and
  complex as your own", in 21 of its 125 freeflow samples, naming the
  dictionary in 16. No other model in the corpus does it more than 8 times
  (Qwen3.7 Max); Gemini 3.1 Pro does it 5–6. It is a borrowed sentence, but
  it is the one Argon kept reaching for, and it names the outward move the
  card calls its most distinctive. Shortened to the site's ten-word limit.
  Its other tic, "there is a specific kind of silence…", is common across the
  corpus and was not used.
- Banner: a narrow old street at the blue hour, a dozen lit windows each
  holding a separate small life (ironing, a shared pot, homework, a watering
  can, someone asleep), and one passerby in a long coat stopped on the wet
  cobbles, looking up. Rendered through OpenRouter `google/gemini-3-pro-image`
  on the first attempt. A fake painter's signature (bottom right, in the
  cobbles) was painted out with a feathered patch of the cobbles beside it;
  full native 21:9 frame kept (1500x636, the same as its siblings). No other
  lettering.
- Display name follows its Gemini siblings (`gemini-4-argon`, lower case).

## Pricing

The site shows $2.00 / $10.00 per M from a FIRST_PARTY_API_PRICING row
(Gemini API, Standard paid tier, read 2026-10-13). Google's launch price runs
through 2026-11-30 and doubles to $4 / $20 from 2026-12-01. Without the row the
generator picked OpenRouter's cheapest endpoint, which for Argon is Flex at half
price ($1 / $5).

**Known issue, not fixed here:** the same cheapest-endpoint rule means other
Gemini pages now show Flex prices too (Gemini 3.1 Pro $1 / $6 against $2 / $12
interactive; Gemini 3.8 Flash $0.375 / $1.875 against $0.75 / $3.75). Left for
a separate correction so this release only changes Argon.

## Capability ladder

**165.8 / 220, provisional, the highest on the site.** Artificial Analysis
lists one row for Gemini 4 Argon, at High effort (`artificialanalysis.ai/
models/gemini-4-argon`, read 2026-10-13, release day; Intelligence Index
52.6). High is Google's default thinking level for its Pro-class models, so it
matches the provider-default capture. Eight rungs measured (AA-LCR, SciCode,
AutomationBench, Briefcase rubric, HLE, Omniscience accuracy, CritPt,
GDP.pdf); the other 14 are fitted. Fitted with the recovered 2026-10-04
provisional method (script and inputs in
`internal/capability-ladder/provisional-20261013-argon/`; the script first
checks the method reproduces 161.6 / 128.1). For scale: Opus 5.5 163.5,
Fable 5.1 162.3, Muse Wonder 162.2, GPT-6 Astra 162.0. The lead over Opus 5.5
(2.3 points) rests on eight measured rungs and a method that reproduces the
published ladder to within about 0.9 points; treat the ordering at the top as
provisional until the full refresh.

## Map

175 models, 33,195 freeflow documents; all 174 previous models remain.
Nearest neighbours by pooled raw-text similarity: GLM-5.1 0.940, Gemini 3.1
Pro 0.931, Gemini 3.6 Flash 0.925, Gemini 3.7 Flash 0.924, GLM-5.2 0.924,
Gemini 3.5 Flash 0.921. Nearest Google model: Gemini 3.1 Pro. Unlike Haiku 5.5
and Muse Wonder, it sits squarely in its own line. Layouts aligned to the
previous release: PCA disparity 0.0001 / 0.0002 (2D / 3D); MDS 0.404 / 0.149
and UMAP 0.130 / 0.248.

## Verification

Scoped generation added one model object and preserved 174 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests
(3) and the pricing suite (52 first-party models) pass.
`test_phase19_cards.py` fails on an expected OpenRouter price for a phase-19
DeepSeek model, as it does on `main` with these changes stashed (re-run
2026-10-13); not an Argon regression. The built page shows the strapline,
$2.00 / $10.00 per M and 165.8 / 220.

## Spend

Capture: $3.26 summed from the per-call costs recorded in the 245 raw traces;
banner render $0.14. The pre-run estimate by formula was about $15.

*Corrected 2026-10-19:* this release first said $6.52 and 648k / 93k tokens.
The raw traces store each call's usage twice (`usage` and `raw.usage`), and the
original sum counted both. Counted once per trace (raw repo
`scripts/capture_spend.py`): $3.26229, 323,811 completion tokens, 46,527
reasoning. Found by Mira's weekly review.
