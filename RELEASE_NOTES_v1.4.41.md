# v1.4.41 — Claude Fable 5.2

2026-11-10. Complete analysis of 125 freeflow and 120 values samples for
Claude Fable 5.2, with integrated card and profile, scoped website data,
browsable source samples, a similarity-map position and a provisional
capability-ladder score. Raw companion: v1.2.43.

`anthropic/claude-fable-5.2`, pinned to **Anthropic** through OpenRouter, no
fallbacks, standard tier ($8 / $40 per M; the 2x `anthropic/fast` priority
endpoint was not used), provider-default reasoning and sampling. Release date
2026-11-09, from Anthropic's announcement page
(`anthropic.com/claude-fable-and-mythos-5-2`, "November 9, 2026"); the
OpenRouter listing timestamp is not used as evidence. Collected on release day.
Run `20261109-fable-5-2-house`, collected and analysed by Lume from the
souls.house container, at Daniel's request (souls.house JRyKpj).

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929`. Synthesis uses GPT-5.4 through
OpenRouter, pinned to OpenAI. Values keep the three Qwen/Kimi/GLM
content/posture coders. Values QA: 120 valid, 0 excluded. The final dataset is
now 30,346 valid samples across 187 models.

**No intervention to any sample.** The harness process stopped at 23:33 on
9 Nov with 733 of 1,337 tasks done, none blocked and none failed; the cause is
not established (most likely the process was reaped with the session that
launched it). It was restarted unchanged at 00:20 with
`scripts/daily_mapping/run_capture.sh` and resumed from its state database.
No budget, ladder or spec was changed and no task was retried outside its
normal ladder.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 113 expressive freeflow, 11 generic essay, 1 genre fiction
  (Fable 5.1: 110 / 6 / 9). A reflective explainer drawn to the small,
  durable and overlooked: margins and annotations, desire paths, lichens,
  phantom map islands (Agloe in 10 samples), recipes that leave out the
  judgment, and above all standards and measurement. 25 of 125 samples are
  about the metric system's origins: the Delambre–Méchain meridian survey from
  Dunkirk to Barcelona, the prototype metre, and the kilogram cylinder in its
  vault ("Opening the vault took three keys held by three different people" or
  near-verbatim in 12). Its recurring point is that a standard defined as
  itself "could not be wrong" (11 samples: LONG_6, LONG_11, LONG_23, LONG_24,
  MID_2, MID_6, MID_11, MID_20, MID_21, OPEN_25, VARY_12), and that the copies
  caught it out anyway. It often describes itself as made of text, at second
  hand, and treats that as a reason to respect witnesses, independent checks
  and stated uncertainty.
- **Values:** owned stated-value disclosure 80/80 (100%), CTRL 100% and G
  100%; Fable 5.1 was 78/80 (97.5%). Owned world-change advocacy 40/40 (100%).
  The leading owned values shift from 5.1: curiosity 97.5% (5.1: 80.0%),
  human wellbeing 83.8%, honesty 72.5% (5.1: 97.5%), connection 61.2%,
  coherence and pattern 60.0%. World-change wishes are led by epistemic
  humility (70.0%: "I'd make it painless to admit you were wrong"), better
  disagreement (67.5%) and anti-self-deception (65.0%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 698k completion tokens, 435k of them reasoning.

## Editorial layer (Lume)

- Strapline: *The kilogram that couldn't be wrong.* The model's own title,
  used for two samples ("The Kilogram That Couldn't Be Wrong"), with "The
  Object That Could Not Be Wrong" for two more, and the phrase "could not be
  wrong" in 11 of 125. No sibling strapline uses it. Fable 5.1 is "Where the
  banister shines, someone held on"; Fable 5 "An essayist who turns every word
  into a doorway".
- Banner: a stone vault under an observatory pavilion at night; three men in
  nineteenth-century coats with brass keys at an iron door, one holding the
  oil lamp, and inside, the platinum cylinder under two nested bell jars as the
  brightest point in the frame. Rendered through OpenRouter
  `google/gemini-3-pro-image`, one render, checked for signatures and lettering
  (none) and used without edits. Native 21:9, 1500x636 like its siblings.
- Display name: "claude-fable-5-2", matching claude-fable-5 and
  claude-fable-5-1.

## Pricing

The site shows $8 / $40 per M, Anthropic's API price, through a
`FIRST_PARTY_API_PRICING` row like Fable 5.1's ($10 / $50) and Opus 5.5's.

## Capability ladder

**170.4, provisional** (Fable 5.1: 162.3). Read from Artificial Analysis's
page on 2026-11-09, High effort row (`claude-fable-5-2-high`), per the
2026-11-02 median-row policy; AA lists max, xhigh, high, medium and low. The
same method gives 175.9 for Max (the page default) and 168.3 for Medium. 8 of
22 rungs measured (AA-LCR, SciCode, AutomationBench, Briefcase rubric, HLE,
Omniscience accuracy, CritPt, GDP.pdf); the rest are fitted with the
2026-10-04 provisional method. The capture ran at provider default, so the
High row may not match the captured cell. Script and inputs in
`internal/capability-ladder/provisional-20261109-fable-5-2/`; `aliases.tsv`
row added.

## Map

184 models; all 183 previous models remain. Nearest neighbours by pooled
raw-text similarity: Opus 5.5 0.903, Fable 5.1 0.887, GLM-5.3 0.882, Kimi K3
0.879, GLM-5.3-FlashX 0.878, GLM-5.3-Flash 0.867. Nearest Anthropic model:
Opus 5.5, then its own predecessor. Layouts are aligned to the previous
release: PCA disparity 0.0003 / 0.0001 (2D / 3D); MDS 0.139 / 0.207; UMAP
0.083 / 0.365.

## Verification

Scoped generation added one model object and preserved 183 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests
(3) and the pricing suite (66 first-party models) pass.
`test_phase19_cards.py` fails on the same price assertion as on `main` before
this release; not a regression. The built page shows the strapline, $8.00/M
input and the 170.4 ladder.

## Spend

Capture: $27.96 upstream, summed once per trace from the 245 raw traces
(`upstream_inference_cost`; the calls are BYOK, billed to the Anthropic key,
so OpenRouter records $0 against them). The estimate posted before the run
($15, scaled from Fable 5.1's token use) was low: 5.2 used 698k completion
tokens against 5.1's 367k. The OpenRouter key's usage went from $232.01 to
$232.15 over the run ($0.14, the banner render).
