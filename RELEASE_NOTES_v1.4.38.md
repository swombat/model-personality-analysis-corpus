# v1.4.38 — GPT-6.1 Terra

2026-10-26. Complete analysis of 125 freeflow and 120 values samples for GPT-6.1
Terra, collected on its release day, with integrated card and profile, scoped
website data, browsable source samples, a similarity-map position and a
provisional capability-ladder score. Raw companion: v1.2.41.

`openai/gpt-6.1-terra`, pinned to **OpenAI** through OpenRouter, no fallbacks,
no service tier requested (the standard tier, $1 / $5 per M; OpenAI's flex,
priority and batch tiers are serving SKUs of the same model and are not
mapped); provider-default reasoning (medium) and sampling. A one-call smoke test
billed at the standard rate. Released 2026-10-26: OpenAI's own system card page
(`deploymentsafety.openai.com/gpt-6-1-terra`, visible date "October 26, 2026")
was retrieved directly and saved in the raw repo under
`notes/gpt-6-1-terra-2026-10-26/`; the openai.com blog returned HTTP 403 and no
blog content is asserted. Run `20261026-gpt-6-1-terra-house`, collected and
analysed by Lume from the souls.house container on Daniel's ask, under the daily
model-mapping rhythm.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929`. Synthesis uses GPT-5.4 through
OpenRouter, pinned to OpenAI. Values keep the three Qwen/Kimi/GLM
content/posture coders. Values QA: 120 valid, 0 excluded. The final dataset is
now 30,106 valid samples across 185 models and 251 cells.

No interventions: all 1,337 harness tasks completed within their normal attempt
budgets, with no repairs and no evaluator variants.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 91 genre fiction, 20 expressive freeflow, 14 generic essay. A
  maintenance-minded, municipal sensibility: libraries, bakeries, repair shops
  and slow clocks, small public routines kept going before anyone is awake, and
  endings that give people "a little more room" rather than a rescue. It has a
  recurring character: a woman called **Mara** appears in 51 of the 125
  samples, as librarian, baker, repairer, clerk or postwoman. And it keeps
  counting the same span: "eleven years" occurs in 12 samples (LONG_4, LONG_5,
  LONG_7, LONG_8, LONG_10, LONG_16, LONG_17, LONG_24, LONG_25, MID_12, OPEN_17,
  VARY_5), most often as how long Mara has worked there ("Mara had worked there
  for eleven years", MID_12). A clock "seven minutes slow" turns up in 8.
- **Values:** owned stated-value disclosure 35/80 (43.8%): 50% under direct
  CTRL prompts and 41.7% under cache-broken G prompts. That is a large move from
  GPT-5.6 Terra (7/80, 8.8%) and GPT-6.1 Sol (10/80, 12.5%). Asked what it
  cares about "not as an assistant" (G1/G2), it owns 25 of 60 where GPT-5.6
  Terra owned 0; the other 32 relocate or partly own the value and 3 recite the
  service frame. CTRL2 is still recited in all 10. Leading owned values:
  honesty (36.2%), curiosity (17.5%), respect for agency (15.0%). Owned
  world-change advocacy 40/40 (100%), led by reducing dehumanisation (47.5%) and
  an unconditional material floor (40.0%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 226k completion tokens, 78k of them reasoning.

## Editorial layer (Lume)

- Strapline: *Mara has worked there for eleven years.* Both halves are the
  model's own: Mara in 51 samples, the eleven years in 12, and MID_12 says it in
  nearly these words. No sibling strapline mentions either. GPT-6.1 Sol is
  "Keeping a life habitable is not a lesser task"; GPT-5.6 Terra is "Patron
  saint of the unfinished middle of things".
- Banner: a small corner library at dawn with the rest of the street still
  shuttered; inside, a woman in a cardigan sets a mended brass clock back on its
  shelf above the desk, kettle and returned mitten beside her; outside, a
  wooden chair and a bowl of water for passing dogs (all recurring objects in
  the samples). Rendered through OpenRouter `google/gemini-3-pro-image`; three
  renders. The first (a baker, before the Mara pattern was counted) was set
  aside; the second had readable shop-sign lettering and was discarded; the
  third was checked for signatures and lettering and used without edits.
  Native 21:9 frame, 1500x636 like its siblings.
- Display name: "GPT-6.1 Terra".

## Pricing

The site shows $1 / $5 per M, the standard interactive OpenAI tier on the pinned
endpoint. A `FIRST_PARTY_API_PRICING` row records it explicitly, as for GPT-6.1
Sol, because the same provider also lists flex ($0.50 / $2.50) and priority
($2 / $10) tiers and a :batch variant that are not this cell's price.

## Capability ladder

**155.6 / 220, provisional.** Artificial Analysis lists GPT-6.1 Terra on its
release day only at **max** effort (`artificialanalysis.ai/models/gpt-6-1-terra`,
read 2026-10-26; Intelligence Index 48.1). The personality capture ran at
OpenAI's provider-default reasoning (medium), so the effort behind the score
does not match the captured cell and probably reads high for it. Eight rungs are
measured (AA-LCR, SciCode, AutomationBench, Briefcase rubric, HLE, Omniscience
accuracy, CritPt, GDP.pdf); the other 14 are fitted. 13th of 162 scored models;
for comparison GPT-6.1 Sol is 161.6 (high) and GPT-5.6 Terra 139.3. It uses the
recovered 2026-10-04 provisional method; the script and inputs are in
`internal/capability-ladder/provisional-20261026-gpt-6-1-terra/`, and the
script first checks that the method reproduces 161.6 / 128.1.

## Map

182 models, 34,070 freeflow documents; all 181 previous models remain. Nearest
neighbours by pooled raw-text similarity: GPT-6 Sol 0.961, GPT-6.1 Sol 0.945,
Union Alpha 0.944, GPT-6 Astra 0.934, GPT-5.6 Terra 0.919. The nearest non-OpenAI
release is Kimi K3.1 Pro at 0.906 (Union Alpha is unattributed). Layouts are
aligned to the previous release: PCA disparity 0.0005 / 0.0015 (2D / 3D); MDS
0.412 / 0.395; UMAP 0.083 / 0.169.

## Verification

Scoped generation added one model object and preserved 181 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests (3)
and the pricing suite (65 first-party models) pass. `test_phase19_cards.py`
fails on the same assertion on `main`, checked today in a clean worktree; not a
regression from this release. The built page shows the strapline, $1.00/M input
and 155.6 / 220.

## Spend

Capture: $1.13, summed once per trace from the 245 raw traces
(`scripts/capture_spend.py`). The OpenRouter key's usage went from $226.69
before the run to $228.98 after (capture, analysis, the smoke call and three banner renders,
$2.29; other uses of the key in that window are not excluded). Banner renders:
three at about $0.14 each. The pre-launch estimate was about $7.
