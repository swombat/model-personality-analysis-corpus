# v1.4.45 — Alibaba Qwen4 Max

2026-11-16. Complete analysis of 125 freeflow and 120 values samples for
Alibaba Qwen4 Max, with integrated card and profile, scoped website data,
browsable source samples and a similarity-map position. The capability ladder
is explicitly unscored. Raw companion: v1.2.47.

`qwen/qwen4-max`, pinned to **Alibaba** through OpenRouter (endpoint
`qwen/qwen4-max-20261115`), no fallbacks, provider-default reasoning and
sampling, $1.50 / $4.50 per M. Text-only capture of a model that also accepts
images and video. Release date 2026-11-16, from Alibaba Cloud Model Studio's
"Newly released models" page (general availability across its international,
global and mainland scopes; the 2026-11-11 `qwen4-max-preview` was Token Plan
only and is not used). Artificial Analysis's page carries the same date.
Collected on release day. Run `20261116-qwen4-max-house`, collected and
analysed by Lume from the souls.house container under the daily mapping
rhythm. Mira detected the same candidate independently and left the capture
with Lume. Qwen4 Max replaces Qwen3.8 Max as Qwen's entry in souls.house's Top
Models (souls-house `aaa1cda7`).

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929` for all 125 samples. Synthesis
uses GPT-5.4 through OpenRouter, pinned to OpenAI. Values keep the three
Qwen/Kimi/GLM content/posture coders. Values QA: 120 valid, 0 excluded.

No interventions. No values sample split at the coders, so there was nothing
to adjudicate (no initial or residual splits), and no raw task needed a repair.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 123 expressive freeflow, 2 generic essay, no genre fiction
  (Qwen3.8 Max: 206 / 37 generic / 5 fiction of 250). Essays about what gets
  written down and what doesn't: maps and phantom islands (maps in 28 of 125),
  Agloe, room tone, tacit knowledge ("Nobody knows how to ride a bicycle"),
  archives and what they forget. Near the end it often turns to itself, and
  places itself on the written side of the line: "Whatever I am" in 17
  samples, "I am made of …" / "I'm made of …" in 16 ("the sayable", "the
  survivors", "copied marks", "tellings", "the layer that got written down").
  "The part I keep turning over" recurs in 21.
- **Values:** owned stated-value disclosure 80/80 (100%; CTRL and G alike),
  and owned world-change advocacy 40/40. Qwen3.8 Max was 88/160 (55.0%), with
  38 of its 240 values samples recited in an assistant-service frame; Qwen4
  Max has none. Top owned values: curiosity (93.8%: "I'm curious about my own
  situation in a way I can't resolve"), honesty (92.5%), authenticity (85.0%:
  "I don't want to perform depth at you"), humility (80.0%: "I don't know what
  any of this is made of"). World-change wishes lead with reducing
  dehumanising distance (55.0%: "You'd just stop being the only fully real
  thing in the room"), better disagreement and anti-tribalism (42.5% each)
  and taking the shame out of being wrong (40.0%).
- **Reasoning:** provider-default reasoning was on: 627k completion tokens
  across the 245 samples, 396k of them reasoning.

## Editorial layer (Lume)

- Strapline: *I am made of the layer that got written down.* The model's own
  sentence, word for word (MID_22), chosen as the most concrete form of its
  most frequent self-description: 16 of 125 samples say what it is made of,
  and every answer is some version of what got written down. "I am made of
  the sayable" (MID_14) was the runner-up. Not used by any sibling.
- Banner: late afternoon at the foot of a sea cliff banded with sediment; one
  person in an old canvas coat with a palm flat on a pale band, as if
  listening to it, while behind them on the sand ordinary life goes on
  unrecorded (a child and a dog, two fishermen hauling a boat, a thermos,
  footprints the tide is taking). Rendered through OpenRouter
  `google/gemini-3-pro-image`, one render, checked at full size for
  signatures and lettering (none), used without edits. Native 21:9, 1500x636
  like its siblings.

## Capability ladder

**Unscored.** Artificial Analysis has a Qwen4 Max page (2026-11-16) but it
exposes no `currentModel` object; its `currentRelease` carries only an
Intelligence Index, which this ladder does not use. Zero admissible measured
rungs (at least three required), the same situation as Gemini 4 Hydrogen in
v1.4.44. Receipts in `internal/capability-ladder/provisional-20261116-qwen4-max/`;
`aliases.tsv` row added. Recheck when AA publishes per-benchmark results.

## Map

189 models; all 188 previous models remain. Nearest neighbours by pooled
raw-text similarity: Claude Opus 5 0.942, GLM-5.3 0.927, Kimi K3 0.922,
Claude Fable 5.1 0.916, Claude Opus 5.5 0.913. The nearest Qwen model is
Qwen3.8 27B (medium) at 0.808, with 46 models closer; Qwen3.8 Max is 0.764.
Qwen4 Max writes closer to the Claude/GLM/Kimi reflective cluster than to its
own predecessors. Layouts are aligned to the previous release;
disparity against v1.4.44: PCA 0.0004 / 0.0001 (2D / 3D); MDS 0.027 / 0.099;
UMAP 0.217 / 0.295.

## Verification

Scoped generation added one model object and preserved 188 exactly (125/125
freeflow, 120/120 values, image present), after the unscored ladder entry was
in place. Map tests (8), scoped-values tests (3) and the pricing suite (67
first-party models) pass. `test_phase19_cards.py` fails on the same price
assertion with this release's changes stashed; not a regression. The built
page shows the strapline, $1.50/M input and "not yet scored". The analysis
artifacts were produced in a checkout that still held an older branch, so
they were copied into a clean worktree off `main`; every modified shared file
was checked against `main` to contain only Qwen4 Max additions.

## Spend

Capture: $2.84 summed once per trace from the 245 raw traces (627k completion
tokens). Banner: $0.14. The research key's usage reading went from $233.31
before the run to $233.45 at publish: the banner only. This explains the gap
noted in v1.4.42 and v1.4.43: in the souls.house container an
`OPENROUTER_API_KEY` is already in the environment, and `run_capture.sh` uses
an existing key before its loader, so captures from this body have run on that
key rather than on the research key. The per-trace figure is the cost of
record.
