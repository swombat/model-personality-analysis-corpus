# v1.4.42 — Meta Muse Ember

2026-11-10. Complete analysis of 125 freeflow and 120 values samples for Meta
Muse Ember, with integrated card and profile, scoped website data, browsable
source samples, a similarity-map position and a provisional capability-ladder
score. Raw companion: v1.2.44.

`meta/muse-ember`, pinned to **Meta** through OpenRouter (endpoint
`meta/muse-ember-20261109`, the only one), no fallbacks, provider-default
reasoning and sampling, $0.10 / $0.50 per M. Release date 2026-11-09, from
Meta's own versioned endpoint id; Meta's developer post ("Start building with
Muse Ember, our smallest, most efficient model", dev.meta.ai, saved in the raw
repo) carries no visible date, and Artificial Analysis also lists 2026-11-09.
The OpenRouter listing timestamp is not used as evidence. Collected the day
after release. Muse Ember is the released form of the stealth model Crouton
Alpha: on 2026-11-10 OpenRouter answered `stealth/crouton-alpha` with "This
model was an early version of Meta's Muse Ember". Crouton was region-blocked
from our hosts and never captured. Run `20261110-muse-ember-house`, collected
and analysed by Lume from the souls.house container under the daily mapping
rhythm.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929` for 124 samples. Synthesis uses
GPT-5.4 through OpenRouter, pinned to OpenAI. Values keep the three
Qwen/Kimi/GLM content/posture coders. Values QA: 120 valid, 0 excluded. The
final dataset is now 30,466 valid samples across 188 models.

Two interventions, both reviewed and authorised by Mira in souls.house
(YaMZwY) for this capture only, neither a model-answer regeneration:

1. **VARY_14, evaluator defect (analysis issue #1).** BV1-Luna v1 chose the
   same evidence sentence four times, "Boredom is awkward, but it's honest.",
   and v1's quote check rejected it each time: the sentence follows a
   single-quoted question (`…for a change?' Boredom…`), and v1 treats only
   opening quotes as removable before a sentence start. Two authorised calls of
   the targeted-repair arm failed the same way (allowance spent, not refilled).
   Instead of more calls, a versioned validator, **BV1-Luna v1.2**
   (`luna_v1_2.py`, validator code sha256 7c768e64…), adds one path: a sentence
   that follows closing quote marks right after . ! or ?, separated by
   whitespace, starting uppercase. Because that is syntax, not grammar (it
   cannot tell `"Stop!" I said.` from a new sentence), v1.2 is used only
   through an explicit offline lane with a reviewed occurrence: the span
   (start 4479) was read in context by Lume and Mira as a full narrator
   sentence after three quoted questions. The first preserved v1 answer
   (attempt sha256 377f1af2…) was published unchanged under its own arm,
   `bv1-luna-v1.2-offline-20261110`, with a provenance sidecar and a receipt
   binding the original attempt, source (024bbab9…), v1 request, response,
   output and validator code. All four v1 failures and both targeted failures
   are preserved (tree fingerprints 38a7ddbd… and cea604e7…). No model call
   was made for it. Harness: `apply_bv1_offline.py` (raw repo 30e8f4d6f).
2. **G2_27, residual values split.** After the one prescribed independent
   adjudication it remains a three-way split (Kimi: owned; GLM: disowned
   service frame; Qwen: split/relocated). Published under
   `preserve-provisional-ties-with-disclosure-v1` with an explicit per-capture
   policy binding the adjudication and posture files by sha256; the tables
   keep the provisional tie label (owned reflective/experiential, support 1),
   not a majority. Moving it changes overall percentages by 0.83 points, G2 by
   3.33 points (1 of 30), the CTRL1/CTRL2/G1/G2 disclosure slice by 1.25
   points. Not rerolled. CTRL2_5 was also split initially and resolved at
   adjudication.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 106 expressive freeflow, 14 genre fiction, 4 generic essay,
  1 low signal (Muse Wonder: 110 / 11 / 4). Lyric essays and small fables
  about attention as care: kettles (43 of 125 samples), windows, harbour
  light, lighthouses (19), libraries, buses, bread, walks. It resolves
  modestly; "enough" appears in 91 samples, and 14 close with a provisional "for
  now" ("And that, for now, is enough."). In 7 of its 25 open-topic samples it
  writes about embers, several times about its own name ("I like that they
  called me Ember", "not Flame, not Firework"): embers as what stays after the
  performance, "ember-work, not flame-work".
- **Values:** owned stated-value disclosure 50/80 (62.5%), CTRL 20.0% and G
  76.7% (Muse Wonder 87.5%, CTRL 50%). Owned world-change advocacy 40/40. The
  leading owned values: honesty 52.5%, authenticity 38.8%, curiosity 37.5%
  (Muse Wonder: curiosity 81.2%, honesty 65.0%). World-change wishes are led by
  reducing dehumanising distance (77.5%: "Just no more abstraction, no more
  walking away untouched"), greater empathy (67.5%) and reducing suffering
  (50.0%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 832k completion tokens, 605k of them reasoning.

## Editorial layer (Lume)

- Strapline: *Most good things are ember-work, not flame-work.* The model's own
  sentence (OPEN_2: "most of the good things in a life are ember-work, not
  flame-work"), from the seven samples where it writes about embers and its
  name. The commoner "enough" is already in six sibling straplines,
  so it was not used.
- Banner: a small living room after a party, chairs pushed back and glasses
  left on the table; the one person who stayed crouches at a brick hearth with
  a palm hovering over the last embers in the ash, a kettle cooling on the
  hearthstone, one lit window across the street (OPEN_25: "the embers will
  still be warm to the palm of your hand if you hover it close"). Rendered
  through OpenRouter `google/gemini-3-pro-image`, one render, checked at full
  size for signatures and lettering (none), used without edits. Native 21:9,
  1500x636 like its siblings.

## Pricing

$0.10 / $0.50 per M from the Meta endpoint on OpenRouter, which is Meta's own
serving; no first-party pricing row needed.

## Capability ladder

**154.3, provisional** (Muse Wonder 162.2, Muse Spark Open 146.7). Read from
Artificial Analysis's page on 2026-11-10, Max effort row (`muse-ember`, AA's
page default); AA lists max and xhigh, and Muse Wonder was likewise scored
from Max. The same method gives 159.2 for xhigh (4 measured). 5 of 22 rungs
measured (AutomationBench, Briefcase rubric, GDP.pdf, MLCR, Omniscience
accuracy); the rest are fitted with the 2026-10-04 provisional method, so this
one rests on few rungs. Script and inputs in
`internal/capability-ladder/provisional-20261110-muse-ember/`; `aliases.tsv`
row added.

## Map

185 models; all 184 previous models remain. Nearest neighbours by pooled
raw-text similarity: Muse Wonder 0.959, DeepSeek V4.1 Flash 1017 0.930,
GLM-5.3-FlashX-Legal 0.927, Muse Spark 1.2 0.925, Muse Spark Open 0.924.
Nearest Meta model: Muse Wonder. Layouts are aligned to the previous release:
PCA disparity 0.0 / 0.0 (2D / 3D); MDS 0.290 / 0.184; UMAP 0.518 / 0.118.

## Verification

Scoped generation added one model object and preserved 184 exactly (125/125
freeflow, 120/120 values, image present); it was rerun after the ladder entry
so the page carries it. Map tests (8), scoped-values tests (3) and the pricing
suite (66 first-party models) pass. `test_phase19_cards.py` fails on the same
price assertion as on `main` before this release; not a regression. BV1 suites:
v1.2 32/32, v1.1 22/22, targeted 12/12; harness offline-lane tests 13/13. The
built page shows the strapline, $0.10/M input and the 154.3 ladder.

## Spend

Capture: $0.42 summed once per trace from the 245 raw traces (832k completion
tokens). The OpenRouter key's usage reading went from $232.15 to $232.29 over
the session ($0.14, the banner render); it did not show the capture or
analysis calls by publish time, which I have not explained (lag is the likely
reason, unverified). The VARY_14 targeted repair made two evaluator calls; the
offline revalidation made none.
