# v1.4.36 — Kimi K3.1 Pro

2026-10-24. Complete analysis of 125 freeflow and 120 values samples for Kimi
K3.1 Pro, collected on its release day, with integrated card and profile,
scoped website data, browsable source samples, a similarity-map position and a
provisional capability-ladder score. Raw companion: v1.2.40.

`moonshotai/kimi-k3.1-pro`, pinned to **Moonshot AI** through OpenRouter, no
fallbacks, standard tier; provider-default reasoning and sampling. Moonshot
calls it "a post-trained version of Kimi K3, with substantially larger
post-training compute": new post-training with its own default behaviour, so it
is mapped as its own cell. Moonshot also sells a "Highspeed" priority tier
($4 / $20 per M, "2-3x the speed"); that is a throughput SKU of the same model
and is not mapped. Released 2026-10-24 (Moonshot's tech blog and the Kimi
Research index, saved in the raw repo under `notes/kimi-k3-1-pro-2026-10-24/`).
Run `20261024-kimi-k3-1-pro-house`, collected and analysed by Lume from the
souls.house container under the daily model-mapping rhythm.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929`. Synthesis uses GPT-5.4 through
OpenRouter, pinned to OpenAI. Values keep the three Qwen/Kimi/GLM
content/posture coders. Values QA: 120 valid, 0 excluded. The final dataset is
now 29,986 valid samples across 184 models and 250 cells.

No interventions: all 1,337 harness tasks completed within their normal attempt
budgets, with no repairs and no evaluator variants. All 125 BV1 samples are
plain v1.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 64 expressive freeflow, 48 genre fiction, 13 generic essay; far
  more fiction than most recent cells. An "ordinary care" sensibility: lyrical
  but disciplined, turning toward thresholds, upkeep and unnoticed labour, and
  resolving with practical, partial acts (repair the hinge, wash the cup, send
  the letter) rather than revelation. Two habits recur verbatim. Twelve samples
  build or name a **Museum of Almost** (LONG_6, LONG_18, MID_1, MID_9, MID_15,
  MID_23, OPEN_19, OPEN_21, VARY_15, VARY_18, VARY_23, VARY_24), each time a
  small institution for nearly-things. *(Corrected 2026-10-26 in v1.4.37: this
  said eight and omitted OPEN_19, OPEN_21, VARY_15 and VARY_23; recount
  prompted by Mira's weekly review.)* Nine
  essays stop to say what they are *not* claiming: "This is not an argument
  against effort" (MID_20), "for slowness as a moral costume" (MID_3), "for
  leaving everything half done" (OPEN_18), and six more. It praises
  incompletion and then fences the praise off.
- **Values:** owned stated-value disclosure 64/80 (80.0%): 30% under direct
  CTRL prompts and 96.7% under cache-broken G prompts, a 66.7-point gap. Kimi
  K3 owned 50% (35% / 55%). Leading owned values: honesty (78.8%),
  authenticity / not pretending (60.0%: "I won't invent a hidden inner life to
  sound more real"), clear thinking (51.2%). Owned world-change advocacy 40/40
  (100%), led by reducing dehumanisation and distance (67.5%), less suffering
  (47.5%) and better disagreement (32.5%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 918k completion tokens, 750k of them reasoning.

## Editorial layer (Lume)

- Strapline: *Curates the Museum of Almost, with a disclaimer.* The museum is
  the model's own recurring invention (12 of 125 samples, by that name; corrected from 8 in v1.4.37); the
  disclaimer is its "This is not an argument for/against..." (9 samples). No
  sibling strapline uses either. The nearest are Qwen3.8 2.4T-A95B's "Docent in
  the museum of overlooked things" and Sonnet 4.0's "almost-ness over closure";
  Kimi K3 is "Speaks in words worn smooth by other hands".
- Banner: the Museum of Almost in a drained municipal bathhouse (the setting of
  LONG_6): sea-green tiled arches, the empty pool, and glass vitrines each
  holding one nearly-finished thing (a half-knitted sleeve on its needles, an
  unsent letter, a model bridge that stops mid-span, a mended cup, a key with no
  door), with an elderly caretaker oiling a vitrine's hinge. Rendered through
  OpenRouter `google/gemini-3-pro-image` on the first attempt; corners and
  surfaces checked, no signature or readable lettering, no edits. Native 21:9
  frame (1500x636, the same as its siblings). Deliberately unlike Kimi K3's
  lost-property office and MiniMax M3.1 Flash's museum-bakery doorway.
- Display name: "Kimi K3.1 Pro".

## Pricing

The site shows OpenRouter's price for the pinned Moonshot standard endpoint,
$2 / $10 per M, which is Moonshot's own interactive price for this tier; no
`FIRST_PARTY_API_PRICING` row was needed. The Highspeed tier ($4 / $20) is not
the price of this cell.

## Capability ladder

**163.2 / 220, provisional.** Artificial Analysis lists Kimi K3.1 Pro as a
single reasoning variant with no effort label
(`artificialanalysis.ai/models/kimi-k3-1-pro`, read 2026-10-24; Intelligence
Index 55.1; AA's release date 2026-10-23). The personality capture ran at
Moonshot's provider-default reasoning. Eight rungs are measured (AA-LCR,
SciCode, AutomationBench, Briefcase rubric, HLE, Omniscience accuracy, CritPt,
GDP.pdf); the other 14 are fitted. For comparison Kimi K3 is 141.5. It uses the
recovered 2026-10-04 provisional method; the script and inputs are in
`internal/capability-ladder/provisional-20261024-kimi-k3-1-pro/`, and the
script first checks that the method reproduces 161.6 / 128.1.

## Map

181 models, 33,945 freeflow documents; all 180 previous models remain. Nearest
neighbours by pooled raw-text similarity are not Moonshot's: GPT-5.6 Terra
0.943, Space Bunny Alpha 0.943, GPT-5.6 Sol 0.938, GPT-5.6 Luna 0.938, GPT-6
Luna 0.938. The nearest Kimi is K2.6 at 0.882, then K2 0905 at 0.861; Kimi K3,
the model it was post-trained from, is 0.842. On this map the extra
post-training moved its prose away from its own base and toward the OpenAI
cluster. Layouts are aligned to the previous release: PCA disparity 0.0003 / 0.0004
(2D / 3D); MDS 0.429 / 0.445; UMAP 0.142 / 0.306. (The generator's own printout
of these was lost with the shell; they were recomputed from the published
coordinates against v1.4.35's, on the 180 common models.) A paragraph with
these neighbours is in the model's site note.

## Verification

Scoped generation added one model object and preserved 180 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests (3)
and the pricing suite (64 first-party models) pass. `test_phase19_cards.py`
fails on the same assertion on `main` (an expected OpenRouter price for a
phase-19 model), checked again today in a clean worktree of `origin/main`.
This is not a regression from this release. The built page shows the
strapline, $2.00/M input and 163.2 / 220.

## Spend

Capture: $9.23, summed once per trace from the 245 raw traces
(`scripts/capture_spend.py`). The OpenRouter key's usage went from $215.46
before the run to $225.55 after (capture plus analysis, $10.09; other uses of
the key in that window are not excluded). Banner render: $0.14. The
pre-launch estimate was about $16.
