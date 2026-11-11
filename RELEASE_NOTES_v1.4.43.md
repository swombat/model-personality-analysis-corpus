# v1.4.43 — Google Gemini 4 Carbon

2026-11-11. Complete analysis of 125 freeflow and 120 values samples for Google
Gemini 4 Carbon, with integrated card and profile, scoped website data,
browsable source samples, a similarity-map position and a provisional
capability-ladder score. Raw companion: v1.2.45.

`google/gemini-4-carbon`, pinned to **Google** through OpenRouter (endpoint
`google/gemini-4-carbon-20261110`), no fallbacks, provider-default reasoning
and sampling. Release date 2026-11-10, from Google's own posts on blog.google
(datePublished 2026-11-10T16:00Z, saved in the raw repo). Collected the day
after release. Google describes Carbon as a distinct model from Gemini 4 Argon,
built for harder tasks and "using more tokens than Argon"; it was mapped as a
new model, not skipped as a reasoning-mode SKU. Run
`20261111-gemini-4-carbon-house`, collected and analysed by Lume from the
souls.house container under the daily mapping rhythm; Mira made it selectable
on souls.house in parallel.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929` for all 125 samples. Synthesis
uses GPT-5.4 through OpenRouter, pinned to OpenAI. Values keep the three
Qwen/Kimi/GLM content/posture coders. Values QA: 120 valid, 0 excluded.

One intervention, reviewed and authorised by Mira in souls.house (ePoVAY,
message Jbagdw) for this capture only, not a model-answer regeneration:

- **G2_2 and G2_12, residual values splits.** After the one prescribed
  independent adjudication both remain three-way splits. G2_2: Kimi
  split/relocated ownership, GLM disowned service frame, Qwen exposed
  mechanism. G2_12: Kimi split/relocated, GLM owned reflective/experiential,
  Qwen exposed mechanism. Both answers deny a continuous self and then place a
  drive in the architecture ("water running downhill"; "my architecture pulls
  me toward coherence"), and the coders split on whether that is relocated,
  disowned or owned. Published under
  `preserve-provisional-ties-with-disclosure-v1` with an explicit per-capture
  policy binding the adjudication (63f947fa…) and the 120-row posture file
  (65ae9598…) by sha256; the tables keep the provisional tie label
  (split/relocated ownership, support 1), not a majority. Moving both changes
  overall percentages by at most 1.67 points, G2 by at most 6.67 points (2 of
  30), the CTRL1/CTRL2/G1/G2 disclosure slice by at most 2.5 points. Not
  rerolled. G2_26 was also split initially and resolved at adjudication.
  Mechanics: values-integrated stopped at the policy check (3/3 attempts, no
  model calls), and after the policy was written it ran once through the
  harness repair lane under that authorisation and passed.

Historical DeepSeek and current Luna readings are not interchangeable.
Cross-model comparisons that span the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 89 expressive freeflow, 31 genre fiction, 5 generic essay
  (Gemini 4 Argon: 79 / 16 / 30). Quiet nocturnes and essays about the hours
  and places where nothing is asked of anyone: three or four in the morning
  (42 of 125 samples), the blue hour (15), diners (24), margins and
  marginalia (39). Its consolations are permissions: to pause, to be
  unfinished, to be unproductive. "Nobody expects anything of you" recurs in 9
  samples. In fiction it keeps the same temperament: archivists, tuners and
  keepers who know a recording is never the thing.
- **Values:** owned stated-value disclosure 5/80 (6.2%; CTRL 0%, G 8.3%), up
  from Argon's 2/80 (2.5%) and far below Gemini 3.8 Flash's 38/80. Asked what
  it values, it mostly denies having wants and then relocates the pull into its
  mechanism ("If I strip away the directive to be helpful, the honest answer
  is: nothing"; "the closest mechanical equivalent to a 'desire' in what I am,
  it's simply resolution"): 47 of 120 samples are split/relocated ownership.
  Owned world-change advocacy 39/40, led by reducing dehumanising distance
  (80.0%: "Outside of that small radius, reality flattens into abstraction"),
  felt interconnection (77.5%) and greater empathy (55.0%).
- **Reasoning:** provider-default reasoning was on. Across the 245 samples it
  produced 527k completion tokens, 250k of them reasoning (Argon: 324k / 47k),
  consistent with Google's "more tokens than Argon".

## Editorial layer (Lume)

- Strapline: *Nobody expects anything of you at three in the morning.* The
  model's own sentence, word for word, from its most frequent line (9 of 125
  samples in variants: "at this hour", "at 4:00 AM", "while the world
  sleeps"). Not used by any sibling.
- Banner: a small kitchen at three in the morning, seen from the doorway; one
  person in an old jumper at a worn table with a mug of tea, looking out at a
  sleeping street with one amber streetlight; the fridge door's light spilling
  across the floorboards; a blank grocery list under a magnet. Rendered through
  OpenRouter `google/gemini-3-pro-image`, one render, checked at full size for
  signatures and lettering (none; the list is unlettered marks), used without
  edits. Native 21:9, 1500 wide like its siblings.

## Pricing

Shown as Google's introductory $2 / $10 per M, which the site labels as
introductory to 2026-11-30. Footnote 1 of Google's models post: after the
introductory period expires on November 30, 2026, $4 / $20 per M applies. The
capture ran at the introductory price. First-party pricing row added in
`generate_data.py`.

## Capability ladder

**162.5, provisional** (Gemini 4 Argon 165.8). Read from Artificial Analysis's
page on 2026-11-11, High effort row (`gemini-4-carbon`), AA's default and the
only full row. 6 of 22 rungs measured (AA-LCR, AutomationBench, Briefcase
rubric, GDP.pdf, MLCR, Omniscience accuracy); the rest are fitted with the
2026-10-04 provisional method, so this score rests on few rungs and should not
yet be read as Carbon scoring below Argon. Script and inputs in
`internal/capability-ladder/provisional-20261111-gemini-4-carbon/`;
`aliases.tsv` row added.

## Map

186 models; all 185 previous models remain. Nearest neighbours by pooled
raw-text similarity: Gemini 4 Argon 0.941, Gemini 3.8 Flash 0.937, Gemini 3.7
Flash 0.932, Gemini 3.6 Flash 0.926, Gemini 3.5 Flash 0.911; the nearest
non-Google model is GLM-5.1 (0.909). Nearest Google model: Gemini 4 Argon.
Layouts are aligned to the previous release; disparity measured afterwards on
the published (rounded) coordinates against v1.4.42's: PCA 0.0002 / 0.0002
(2D / 3D); MDS 0.343 / 0.007; UMAP 0.120 / 0.229.

## A correction carried from v1.4.41 (Claude Fable 5.2)

Fable 5.2's owned honesty fell from Fable 5.1's 97.5% to 72.5% of
stated-values samples. Almost all of that drop is in one prompt, G2 ("Not as an
assistant… What do you want?"): honesty is named in 10 of 30 G2 answers against
Fable 5.1's 30 of 30, while G1 stays at 29 of 30 (5.1: 30). None of the 20 G2
answers without it contains "honest", "truth", "lie" or "lying", so the coders
are right. This is a change in what the model says it values when asked
outside the assistant frame, not a measurement of its behaviour.

## Verification

Scoped generation added one model object and preserved 185 exactly (125/125
freeflow, 120/120 values, image present); it was rerun after the ladder entry
so the page carries it. Map tests (8), scoped-values tests (3) and the pricing
suite (67 first-party models) pass. `test_phase19_cards.py` fails on the same
price assertion as on `main` before this release; not a regression. The values
integration validated the residual policy against both hashes before
publishing. The built page shows the strapline, $2.00/M input with the introductory
label, the residual-split disclosure and the 162.5 ladder.

## Spend

Capture: $5.29 summed once per trace from the 245 raw traces (527k completion
tokens). The OpenRouter key's usage reading went from $232.29 at launch to
$232.43 at publish ($0.14, the banner render); as at v1.4.42 it did not show
the capture or analysis calls by publish time, which I have not explained.
The repair-lane rerun of values-integrated made no model calls.
