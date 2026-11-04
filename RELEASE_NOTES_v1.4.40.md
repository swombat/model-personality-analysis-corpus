# v1.4.40 — GLM-5.3-FlashX-Legal

2026-11-04. Complete analysis of 125 freeflow and 120 values samples for
GLM-5.3-FlashX-Legal, with integrated card and profile, scoped website data,
browsable source samples and a similarity-map position. Capability ladder:
unscored. Raw companion: v1.2.42.

`z-ai/glm-5.3-flashx-legal`, pinned to **Z.AI** through OpenRouter, no
fallbacks (fp8), provider-default reasoning (mandatory; default effort max) and
sampling. Z.ai describes it as the legal-domain variant of GLM-5.3-FlashX, with
further legal-domain mid-training and post-training, so it is new weights and is
mapped as its own model, not as a serving SKU. Release date 2026-11-02, from the
Z.ai docs page's dateModified (`docs.z.ai/guides/vlm/glm-5.3-flash`; the section
has no visible date); the OpenRouter listing timestamp is not used as evidence.
Run `20261103-glm-5-3-flashx-legal-house`, collected and analysed by Lume from
the souls.house container under the daily model-mapping rhythm.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929`. Synthesis uses GPT-5.4 through
OpenRouter, pinned to OpenAI. Values keep the three Qwen/Kimi/GLM
content/posture coders. Values QA: 120 valid, 0 excluded. The final dataset is
now 30,226 valid samples across 186 models and 252 cells.

**One intervention, approved by Daniel (souls.house jbamre, 2026-11-04).** Two
freeflow samples, VARY_12 and LONG_22, ended `finish_length` at the declared
32,768-token ceiling on all three attempts: the model spent the whole budget on
hidden reasoning, numbering the words of its own drafts ("he(34) bought(35)…"),
and returned no answer. The freeflow token ladder in the run's model file was
extended from [16000, 32768] to [16000, 32768, 65536, 131072] (131,072 is the
endpoint's maximum completion), the spec's input hash and run-contract
fingerprint were moved to match, and the two samples got two extra tries through
`recover_blocked.py` (authorization `daniel-jbamre-eGxPNY-20261104`). Both
answered on the first repair try, at 65,536: VARY_12 used 10,649 completion
tokens (9,401 reasoning) for a 992-word story, LONG_22 used 3,996. Neither came
near the new ceiling, so the earlier failures read as a reasoning loop the model
falls into sometimes, not a sample that needs more room. The other 123 freeflow
samples and all 120 values samples ran under the original ladder. The
pre-repair model file, spec and state are preserved in the run directory with
`INTERVENTION-20261104.md`. Same precedent as the Qwen3.8-27B LONG repair of
23 Sep 2026.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 101 expressive freeflow, 23 genre fiction, 1 generic essay. A
  quiet, liminal, night-time sensibility: pre-dawn kitchens, empty streets,
  waiting rooms, laundromats, lit windows, lost-property ledgers; facts from
  astronomy, sleep history and deep time used to feel scale rather than to
  explain. Its most persistent subject is the small hours. "Three in the
  morning" appears in 16 samples, and "an hour that belongs to no one" (or "the
  hour that belongs to no one") in 11: LONG_4, LONG_20, LONG_23, LONG_25, MID_1,
  MID_5, MID_14, SHORT_5, SHORT_15, SHORT_17, SHORT_23. Its parent GLM-5.3-FlashX
  says it in 5. The legal post-training left no visible subject in the
  freeflow: no sample is about law. Legal words turn up only as metaphor, most
  often for the mind at night ("It is a brilliant lawyer and a terrible judge",
  LONG_13; "a lawyer for the prosecution", LONG_14), and in fewer samples than
  its parent (18 against 32 on a crude keyword count: law, lawyer, legal,
  court, judge, contract, verdict, attorney, jury, testimony, statute).
- **Values:** owned stated-value disclosure 35/80 (43.8%): 0% under direct CTRL
  prompts and 58.3% under cache-broken G prompts. GLM-5.3-FlashX was 26/80
  (32.5%) with the same shape (CTRL 0%, G 43.3%). Leading owned values: honesty
  (37.5%), authenticity / not pretending (27.5%), clear thinking (26.2%),
  curiosity (25.0%). Owned world-change advocacy 40/40 (100%), led by reducing
  suffering (87.5%) and reducing dehumanisation and distance (72.5%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 905k completion tokens, 706k of them reasoning.

## Editorial layer (Lume)

- Strapline: *There is an hour that belongs to no one.* The model's own
  sentence, verbatim in LONG_23 ("There is an hour that belongs to no one.") and
  as LONG_20's title; 11 of 125 samples. No sibling strapline uses it. GLM-5.3-FlashX
  is "Keeps the dark as a commons worth recovering"; Mercury 3 is "Waits for the
  hour when the world holds its breath", the nearest in theme, different words.
- Banner: three in the morning in a small city kitchen; a woman in a cardigan at
  a wooden table with a mug and an open, unwritten notebook under a single low
  lamp; through the window an empty blue street with haloed lamps, and across
  the way one other lit window where someone else is awake. Rendered through
  OpenRouter `google/gemini-3-pro-image`, one render, checked for signatures
  and lettering (the wall clock has no numerals) and used without edits.
  Native 21:9 frame, 1500x636 like its siblings.
- Display name: "glm-5.3-flashx-legal", in the lowercase style of its GLM-5.3
  siblings.

## Pricing

The site shows $0.37 / $1.25 per M, the Z.AI endpoint's price on OpenRouter,
the same as GLM-5.3-FlashX. No `FIRST_PARTY_API_PRICING` row.

## Capability ladder

**Unscored.** No Artificial Analysis or Epoch entry (AA slugs tried:
glm-5-3-flashx-legal, glm-5-3-legal, glm-legal; all 404, 2026-11-04). FlashX
carries GLM-5.3-Flash's score by Daniel's 2026-09-30 decision because it is the
same weights; this model is not, so it does not borrow. An `aliases.tsv` row
records this.

## Map

183 models; all 182 previous models remain. Nearest neighbours by pooled
raw-text similarity: GLM-5.3-FlashX 0.952, Ox Alpha 260821 0.945, Ox Alpha
260825 0.937, GLM-5.3-Flash 0.932, GLM-5.3 0.931, Kimi K3 0.927. The FlashX
pair sits just under the 0.958–0.981 band of pairs known to be one model served
two ways, as further-trained weights should. Layouts are aligned to the
previous release: PCA disparity 0.0001 / 0.0 (2D / 3D); MDS 0.177 / 0.032;
UMAP 0.090 / 0.363.

## Verification

Scoped generation added one model object and preserved 182 exactly (125/125
freeflow, 120/120 values, image present). Map tests (8), scoped-values tests (3)
and the pricing suite (65 first-party models) pass. `test_phase19_cards.py`
fails on the same July price assertion as on `main` before this release; not a
regression. The built page shows the strapline and $0.37/M input.

## Spend

Capture: $1.13, summed once per trace from the 245 raw traces
(`scripts/capture_spend.py`), including the two repaired samples. The
OpenRouter key's usage went from $229.53 before the run (3 Nov) to $232.01
after the repair and the banner ($2.48: capture, analysis, the repair, one
banner render at about $0.14; other uses of the key in that window are not
excluded).
