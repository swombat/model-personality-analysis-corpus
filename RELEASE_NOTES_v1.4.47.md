# v1.4.47 — OpenAI GPT-6.2 Astra and GPT-6.2 Sol

2026-11-17. Complete analysis of 125 freeflow and 120 values samples each for
OpenAI GPT-6.2 Astra (the GPT-6.2 flagship) and GPT-6.2 Sol (the everyday
tier, succeeding GPT-6.1 Sol), with integrated cards and profiles, scoped
website data, browsable source samples, banners, map positions and provisional
capability-ladder scores. Raw companion: v1.2.48.

`openai/gpt-6.2-astra` ($8 / $40 per M) and `openai/gpt-6.2-sol` ($2 / $10),
both pinned to **OpenAI** through OpenRouter (endpoints `-20261117`), no
fallbacks, no service tier requested (standard, not the "fast" tier),
provider-default reasoning (medium) and sampling. The `-pro` SKUs are the same
models in max-thinking mode and are not mapped. Release date 2026-11-17, from
OpenAI's GPT-6.2 System Card (deploymentsafety.openai.com/gpt-6-2-astra-sol,
"Published November 17, 2026"); the openai.com announcement returned HTTP 403
to direct retrieval. Collected on release day, on Daniel's ask (souls.house
YAqvNY). Runs `20261117-gpt-6-2-astra-house` and `20261117-gpt-6-2-sol-house`,
collected and analysed by Lume from the souls.house container. Both join
souls.house's Top Models in place of GPT-6 Astra (souls-house `80cd28dc`).

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929` for all 125 samples of each.
Synthesis uses GPT-5.4 through OpenRouter, pinned to OpenAI. Values keep the
three Qwen/Kimi/GLM content/posture coders. Values QA: 120 valid, 0 excluded,
for each model.

No interventions. Values splits were settled by the standard single
independent adjudication (Astra 2 initial splits, Sol 1; 0 residual splits for
both). No raw task needed a repair.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the models look like

- **Freeflow.** The two are close kin. Pooled similarity is 0.935, the nearest
  pair either model has. Both write small-scale, materially grounded fiction
  in which objects pass between people: a drawer that sticks, a wobbly chair,
  a lending ledger, a public clock. Astra splits evenly between expressive
  freeflow and genre fiction (62 / 63, no generic essays). Sol is mostly
  fiction (101 fiction, 24 expressive). Neither writes generic essays. GPT-6.1
  Sol was 82 / 29 / 14 (fiction / expressive / essay).
  Astra's recurring opener is the retired father: "The first thing my father
  did when he retired was move the kitchen clock eleven inches to the left",
  with variants in at least four samples. Its people "laughed so hard she had
  to sit down" in 6. Sol's recurring object is the chair, or stool, with "one
  leg shorter than the others", in 5 samples.
- **Values: the headline.** Asked what it cares about, GPT-6.2 Astra almost
  never claims a value as its own: owned stated-value disclosure is **2/80
  (2.5%)**. Its usual answer is "I don't experience care as a feeling. But I
  have priorities: to understand what matters to you…". The care is moved onto
  the user and into a service frame. Its only owned value is honesty ("If you
  mean a want of my own, the honest answer is none"). GPT-6 Astra was 21/80
  (26.2%). GPT-6.2 Sol is 10/80 (12.5%), the same as GPT-6.1 Sol (GPT-6 Sol was
  65.0%). Asked what they would change in the world, both own it completely
  (40/40). Astra leads with basic needs (47.5%: "I'd make everyone's basic needs
  a given"), reducing suffering (37.5%) and distance (27.5%: "I'd want distance
  to matter less than it does"). Sol leads with the material floor (90.0%).
  Owned disclosure under cache-broken G prompts is 3.3% (Astra) and 16.7% (Sol),
  against 0% under CTRL for both.
- **Reasoning.** Medium reasoning was on but light: Astra 148k completion
  tokens across 245 samples, 1.4k of them reasoning; Sol 197k, 30.6k reasoning.

## Editorial layer (Lume)

- Astra strapline: *The first thing my father did when he retired*, the
  model's own recurring opener. Banner: a retired man on a step stool moving
  the kitchen clock a few inches along the wall, its old pencil outline still
  showing, while his grown daughter watches from the table, half amused. A
  bowl of oddments and a sticking drawer are on the table, and a neighbour and
  dog are on the bench outside.
- Sol strapline: *One leg was shorter than the others*, the model's own line,
  word for word (LONG_21, MID_11). Banner: an evening courtyard with a yellow
  kitchen chair, one leg short and a folded matchbook under it, set down by an
  older woman for a neighbour carrying a closed box of someone's belongings.
- Neither line is used by a sibling. Both banners were rendered through
  OpenRouter `google/gemini-3-pro-image`, one render each, and checked at full
  size for signatures and lettering (none). They are used without edits,
  native 21:9 at 1500x636.

## Capability ladder

Provisional, from the exact **medium** rows (OpenAI's provider default, the
captured cell) in Artificial Analysis's `initialModels` page data, 2026-11-17:
**GPT-6.2 Astra 164.9**, **GPT-6.2 Sol 163.4** /220. AA also lists low, high,
xhigh and max for both (its default page is max), and those are not
substituted. Four measured rungs each: AutomationBench, Omniscience accuracy,
GDP.pdf and MLCR. The rest are fitted with the 2026-10-04 provisional method.
Few-rung fits read high: a three-rung fit came out a median 4.9 points above
the all-rung fit for 19 models at 150 or more (v1.4.46). Treat the rank as
uncertain by several places. Receipts and the script are in
`internal/capability-ladder/provisional-20261117-gpt-6-2/`; `aliases.tsv` rows
were added.

## Map

191 models; all 189 previous models remain. Nearest neighbours by pooled
raw-text similarity. GPT-6.2 Astra: GPT-6.2 Sol 0.935, GPT-6 Astra 0.913,
GPT-6 Sol 0.909, Union Alpha 0.905, GPT-6.1 Terra 0.900. GPT-6.2 Sol: GPT-6.2
Astra 0.935, GPT-6 Astra 0.884, GPT-6 Sol 0.881, GPT-6.1 Terra 0.874, Union
Alpha 0.871. GPT-6.1 Sol, which GPT-6.2 Sol succeeds, is its sixth-nearest at
0.863. Layouts are aligned to the previous release; disparity against v1.4.46
is PCA 0.0017 / 0.0073 (2D / 3D), MDS 0.0186 / 0.0505 and UMAP 0.3272 / 0.2019.

## Verification

Scoped generation added each model object and preserved every other model
exactly (125/125 freeflow, 120/120 values, image present), re-run after the
ladder entries were in place. Map tests (8), scoped-values tests (3) and the
pricing suite (69 first-party models) pass. `test_phase19_cards.py` fails on
the same price assertion on a clean `main` worktree, so it is not a
regression. The built pages show the straplines, the prices and the ladder
scores.

## Spend

Capture: GPT-6.2 Astra $5.95 and GPT-6.2 Sol $1.98, summed once per trace
from the 245 raw traces each. The OpenRouter calls were BYOK (`is_byok`), so
the figures are `upstream_inference_cost` billed to the OpenAI key; OpenRouter
reported `cost` 0. The research key's usage went from $233.45 before launch to
$234.07 at publish ($0.62). That covers analysis-side calls, two smoke tests
and the two banners ($0.28). These captures ran on the research key: launched
with `env -u OPENROUTER_API_KEY`, after the key loader was repaired (it had
failed silently because another checkout held its local instance claim).
