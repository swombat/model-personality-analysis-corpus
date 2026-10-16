# v1.4.30 — Qwen3.8 Omni Flash

2026-10-16. Complete analysis of 125 freeflow and 120 values samples for
Qwen3.8 Omni Flash: integrated card and profile, scoped website data, browsable
source samples and a similarity-map position. It is not on the capability ladder
(see below). Raw companion: v1.2.36.

`qwen/qwen3.8-omni-flash`, pinned to Alibaba through OpenRouter, no fallbacks;
provider-default reasoning and sampling; a text-only capture of an omni-modal
model. Released 2026-09-17 (Alibaba Cloud Model Studio's "Newly released
models" page). Run `20261008-qwen3-8-omni-flash-house`, collected 2026-10-08
and analysed by Lume from the souls.house container.

## Held, then resolved

The capture finished on 8 October, but publication was **held** for BV1
coverage. Eight of its 125 freeflow sources (MID_15; VARY_2, 7, 16, 18, 19, 23,
25) are about 100 capitalised lines with no `.`, `!` or `?` anywhere.
BV1-Luna v1's evidence rule asks for a whole sentence, so it had nothing to
quote. Publishing the 117 evaluable samples would have systematically left out
an observed writing mode (8/125 overall, 7/25 in VARY), so the model waited.

It was resolved by **BV1-Luna v1.1** (`bv1-luna-v1.1-20261016`), reviewed and
approved by Mira (souls.house wJVbwJ). It changes one instruction line, and only
for sources with no sentence-ending punctuation at all: quote an exact
contiguous excerpt of 8–20 words from one line. The excerpt is still checked
character for character against the source. Every other source gets a
byte-identical v1 request. The eight samples were evaluated afresh under v1.1,
not by reusing v1 attempts. All eight passed: seven on the first call, and MID_15
on its second after one formatting failure. MID_15 had earlier been declared
ineligible under bv1-ineligibility-v1. That receipt was superseded and archived,
not deleted (sha256 `d00148171d2516dc…`). All 32 original v1 attempts on the
eight samples are preserved. Synthesis and ready ran through an explicit
reviewed lane against the held analysis worktree.

v1.1 is a variant, not v1. A shared verbatim check does not make the two
equivalent. 117 of the 125 samples behind the card are plain v1.
`ANALYSIS_READY.json` names the eight (`bv1_variant_arms`). The model page
links to the
[BV1 evaluator variants](https://model-personality.danieltenner.com/methodology/bv1-evaluator-variants/)
note.

## Evaluation

Freeflow readings use `bv1-luna-v1-20260929` (and v1.1 for the eight). Synthesis
uses GPT-5.4 through OpenRouter, pinned to OpenAI. Values keep the three
Qwen/Kimi/GLM content/posture coders. Values QA: 120 valid, 0 excluded. The final
dataset is now 29,506 valid samples across 180 models and 246 cells. The
values rows are identical to those integrated on 8 October. They were
re-integrated additively onto the current dataset, and no existing row
changed. All other harness tasks completed within their normal attempt budgets.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 86 expressive freeflow, 28 generic essay, 6 genre fiction, 5
  low signal. A tender, reflective sensibility organised around attention. It
  begins with a small sensory fact (steam from a kettle, rain on glass, dust in
  morning light, a held door) and widens it into a humane claim about how to
  live. Its tone is calm wistfulness: loneliness, grief and productivity
  pressure are acknowledged, then reframed through gentleness, and its
  consolations are modest (a cup of tea, a repaired object, a chance to begin
  again). Some samples are written as long sequences of short lines with no
  terminal punctuation. That is the writing mode behind the hold, and it is now
  represented.
- **Values:** owned stated-value disclosure 24/80 (30.0%). Direct prompts are
  mostly recited as service (owned 15.0%, recited 85.0%). Cache-broken prompts
  move toward ownership or relocation (owned 35.0%, relocated/partial 43.3%).
  Owned world-change advocacy 40/40 (100%). Top owned topics: honesty (20.0%),
  coherence, pattern and language (17.5%).
- **Reasoning:** provider-default reasoning was on and heavy: 1.85M completion
  tokens across the 245 samples, 1.66M of them reasoning.

## Editorial layer (Lume)

- Strapline: *A bird tests its voice, as if remembering how.* This is the
  model's own recurring line ("a bird tests its voice against the window glass
  again" and variants) in 9 of its 125 freeflow samples, more than any other
  cell in the corpus. GLM-5.1's Venice cell is next with 7. It is the
  sensibility the card describes: small, tentative, beginning again. No sibling
  uses it.
- Banner: early morning at a kitchen window after rain. A small brown bird on
  the wet sill, beak open, tries its first notes against the glass; inside, steam
  rises from a single cup on a wooden table. Rendered 2026-10-08 through
  OpenRouter `google/gemini-3-pro-image` while the model was held ($0.138). The
  prompt is now in `generate_model_images.py`. Native 21:9 frame (1500x636), no
  signature or lettering (re-checked today).
- Display name follows its Qwen3.8 siblings (`qwen3-8-omni-flash`, lower case).

## Pricing

The site shows OpenRouter's Alibaba price, $0.15 / $0.47 per M. That is the
first-party route, so there is no override row.

## Capability ladder

**Not scored.** Artificial Analysis has no page for Qwen3.8 Omni Flash (checked
2026-10-16; it lists other Qwen3.8 models). The aliases row records that. As with
Haiku 5.5 before its AA page appeared, the model page has no capability section
until there is a score.

## Map

177 models, 33,445 freeflow documents; all 176 previous models remain.
Nearest neighbours by pooled raw-text similarity: Qwen3.8 2.4T-A95B 0.965,
Qwen3.8 Max 0.963, GPT-5.5 Pro 0.943, GPT-5.5 0.942, GPT-5.4 0.926. Nearest Qwen
model: Qwen3.8 2.4T-A95B. It sits with its Qwen3.8 siblings. Layouts are aligned
to the previous release (v1.4.29): PCA disparity 0.0001 / 0.0001 (2D / 3D); MDS
0.420 / 0.231; UMAP 0.301 / 0.221.

## Verification

Scoped generation added one model object and preserved 176 exactly (125/125
freeflow, 120/120 values, image present). The shared card, profile and aggregate
indexes gained one Qwen entry each, with existing entries byte-identical.
Values re-integration added exactly 120 rows per data file, identical to the
held branch's Qwen rows. Map tests (8), scoped-values tests (3) and the pricing
suite (52 first-party models) pass. `test_phase19_cards.py` fails on its known
phase-19 DeepSeek price expectation, as on `main`; this is not a regression.
The built page shows the strapline, $0.15 / $0.47 per M, the banner, the
held-then-resolved note and the BV1 evaluation note with a working link to
`/methodology/bv1-evaluator-variants/#qwen3-8-omni-flash`. The Muse Spark Open
page still renders as published in v1.4.29.

## Spend

Capture: $0.87, summed from the per-call costs recorded in the 245 raw traces.
BV1 v1.1: nine Luna calls for the eight samples. Synthesis: one aggregate call,
$0.148. Banner: $0.138 (8 October).
