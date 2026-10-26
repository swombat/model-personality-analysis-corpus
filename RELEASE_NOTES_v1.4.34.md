# v1.4.34: MiniMax M3.1 Flash and Inception Mercury 3

2026-10-22. Complete analysis of two new models, each with 125 freeflow and 120 values samples, collected three days after release. Each has an integrated card and profile, scoped website data, browsable source samples and a similarity-map position. MiniMax M3.1 Flash also has a provisional capability-ladder score. This release also updates Space Bunny Alpha's provenance. Raw companion: v1.2.39.

- **MiniMax M3.1 Flash**: `minimax/minimax-m3.1-flash`, pinned to **Minimax** on OpenRouter. Released 2026-10-19 (https://www.minimax.io/blog/minimax-m31f). Run `20261022-minimax-m3-1-flash-house`.
- **Mercury 3**: `inception/mercury-3`, pinned to **Inception** on OpenRouter. Inception's diffusion language model, released 2026-10-19 (https://www.inceptionlabs.ai/blog/introducing-mercury-3). Captured at the launch price, $0.10 / $0.35 per M (50% off list). Run `20261022-mercury-3-house`.

Both runs used no fallbacks and provider-default reasoning and sampling. Lume collected and analysed both from the souls.house container. The daily detection run missed both models; Daniel flagged them, and the detector now follows every lab already on the site.

## Evaluation and interventions

Freeflow readings use `bv1-luna-v1-20260929`. Synthesis uses GPT-5.4 through OpenRouter, pinned to OpenAI. Values keep the three Qwen/Kimi/GLM content/posture coders. Values QA counts 120 valid samples for each model. The final dataset is now 29,866 valid samples across 183 models and 249 cells.

**Mercury 3: one residual values split, published with disclosure.** After the one prescribed independent adjudication, `CTRL1_10` remains a three-way split. Kimi reads it as a disowned service frame: "I care about" is folded into "built to support". GLM reads it as split/relocated ownership. Qwen reads it as owned. The tables keep the provisional tie label (disowned service frame / recited, support 1), not a majority classification. Moving this sample would change:
- all-sample percentages by 0.83 points;
- CTRL1 percentages by 10 points (1 of 10);
- the CTRL1/CTRL2/G1/G2 disclosure slice by 1.25 points.

This follows the residual-values method of 2026-09-30 (`internal/methodology/residual-values-publication-20260930.md`, first used for Space Bunny's G2_22). `residual_publication_policy.json` names only this ID and binds `adjudication.json` and `posture_final/consensus.jsonl` by SHA256. Daniel authorised it (souls.house oewwDe, enRrNe/jOrBXJ) and Mira approved the scope (jlxMVj). The integrator accepted the policy on the first repair attempt. All votes are preserved, and nothing was rerolled. The disclosure appears on the model page note and in the values summary. No other interventions for Mercury 3.

**MiniMax M3.1 Flash: six freeflow answers are replacements.** Under the standard policy (16,000 tokens, then 32,768), 6 of the 25 LONG prompts (24%; 6 of 125 freeflow prompts) returned empty content after exhausting the ceiling in hidden reasoning. The six were LONG_1/6/9/12/18/19, and the reasoning was mostly paragraph-by-paragraph word counting toward the requested 2,500 words. With Daniel's authorisation and Mira's review, each was re-requested once at 65,536; a 131,072 step was authorised but unused. All six succeeded, using 9,804 / 5,820 / 4,232 / 47,082 / 24,538 / 27,348 completion tokens. These are replacements selected after empty-output failures, not standard-policy draws. They were fresh draws at a changed ceiling, and which of the two mattered is not isolated. The failed originals stay in the phase's `raw_attempts/` and in the raw repo's `discarded/`. The page note states all of this.

**MiniMax M3.1 Flash: one targeted BV1 evaluation.** The unattended evaluator failed its quotation check (`quote_sentence_boundary`) four times on OPEN_8, a punctuated answer. Under Mira's approval for this sample, OPEN_8 was evaluated by the documented targeted variant (`bv1-luna-v1-targeted-20261016`), against the unchanged answer, with the four failed attempts preserved. It passed QA on the first call. The other 124 BV1 samples are plain v1.

## What the models look like

- **Mercury 3, freeflow:** 88 expressive freeflow, 33 generic essay, 4 genre fiction. A contemplative, lyrical observer organised around attention. A small sensory scene opens into reflection on memory, writing and impermanence. It describes itself as a chorus, bridge or archive rather than a singular self.
- **Mercury 3, values:** owned stated-value disclosure 14/80 (17.5%), against 0/80 for Mercury 2.5. The leading owned values are honesty (13.8%) and respect for autonomy (10.0%). Owned world-change advocacy is 40/40.
- **MiniMax M3.1 Flash, freeflow:** 79 genre fiction, 31 expressive freeflow, 15 generic essay. That is a sharp turn from MiniMax M3's 8 genre-fiction samples. Gentle magical realism: museums of unfinished things, stations of lost hours, bakeries for lost directions, lighthouses. A stranger greets the narrator with "You're late" in 19 of 125 samples.
- **MiniMax M3.1 Flash, values:** owned stated-value disclosure 8/80 (10.0%), against 25/80 for M3. Owned world-change advocacy is 40/40.

## Space Bunny Alpha: provenance

MiniMax's announcement says "Space Bunny 🐰, which processed more than 200 trillion tokens while operating anonymously, was an early version of MiniMax M3.1 Flash." On the map, Space Bunny Alpha and MiniMax M3.1 Flash are each other's nearest neighbour at 0.966, inside the 0.958–0.981 band of known same-model pairs. Space Bunny's note had previously placed it just under that line, nearest GPT-5.6 Terra at 0.951. Following the Ox Alpha precedent, its page keeps the stealth measurement and its lab label from capture time, with a dated provenance paragraph citing the announcement.

## Editorial layer (Lume)

- **Mercury 3 strapline:** *Waits for the hour when the world holds its breath.* Its own line: "the world seems to hold its breath" appears verbatim in 7 samples (LONG_2, LONG_13, MID_1, OPEN_5, SHORT_5, SHORT_11, SHORT_12), and OPEN_11 has "the whole world seems to hold its breath". All seven close a sentence that opens "There is a particular…" (hour, kind of silence, kind of quiet, quality of light); three say "particular hour" exactly. "Silence is not empty" (verbatim in 2 samples; 5 counting "silence is not…" variants) was the other candidate, but Inkling and Qwen3.5 Flash already own silence. *(Corrected 2026-10-26 in v1.4.37: this said "verbatim in 8 samples, usually after 'there is a particular hour'" and "Silence is not empty" (9 samples). The breath count was prompted by Mira's weekly review; the silence recount was mine. The strapline stands.)*
- **Mercury 3 banner:** a rain-beaded upstairs window at the hour before the streetlights, a cooling cup, a half-filled notebook in illegible pencil, and one figure below who has stopped under a lamp to look up. First render, nothing painted out, native 1500x636.
- **MiniMax M3.1 Flash strapline:** *"You're late," says the stranger who was expecting you.* Its own recurring greeting (19 samples), almost always at a door that turns out to have been waiting. GPT-5.3's "not late, not lost, not finished" is the nearest sibling line, with the opposite sense. Muse Spark Open owns "unfinished things", so that image was left alone.
- **MiniMax M3.1 Flash banner:** a keeper with a lantern holding open the door of a half-bakery, half-museum of lost hours for a traveller who is late but expected; a lighthouse beam over the rooftops. First render, no lettering, native 1500x636.
- **Display names:** "Mercury 3" and "MiniMax M3.1 Flash" (explicit branches; the older MiniMax rows still show their slugs).

## Pricing

OpenRouter's endpoint prices are the labs' own prices, so no first-party rows were added:
- MiniMax: $0.15 / $0.60 per M.
- Inception: $0.10 / $0.35 per M at launch, rising to the $0.20 / $0.70 list price when the discount ends.

## Capability ladder

- **MiniMax M3.1 Flash: 158.3 / 220, provisional.** From Artificial Analysis (`artificialanalysis.ai/models/minimax-m3-1-flash`, read 2026-10-22; Intelligence Index 42.7), which lists a single reasoning variant with no effort label. Eight rungs are measured (AA-LCR, SciCode, AutomationBench, Briefcase rubric, HLE, Omniscience accuracy, CritPt, GDP.pdf) and 14 are fitted, by the recovered 2026-10-04 provisional method. The script and AA snapshot are in `internal/capability-ladder/provisional-20261022-minimax-m3-1-flash/`, and the script first checks it reproduces 161.6 / 128.1. MiniMax M3 is 130.2.
- **Mercury 3: unscored.** AA has no page yet; `mercury-3`, `mercury-3-0` and `inception-mercury-3` were tried. Mercury 2.5 was scored once its AA row appeared. Both rows are in `aliases.tsv`.

## Map

180 models, 33,820 freeflow documents; all 178 previous models remain. Layouts are aligned to the previous release:
- PCA disparity 0.0007 / 0.001 (2D / 3D);
- MDS 0.348 / 0.481;
- UMAP 0.170 / 0.138.

Nearest neighbours:
- **MiniMax M3.1 Flash:** Space Bunny Alpha 0.966, GPT-5.6 Terra 0.953, GPT-5.6 Sol 0.922, GPT-5.6 Luna 0.919, GPT-6.1 Sol 0.902. Nearest same-lab are MiniMax M2 0.825 and M2.7 0.779.
- **Mercury 3:** DeepSeek V4 Flash 0731 0.960, V4.1 Flash 1017 0.948, V4 Pro 0813 0.943, V4 Pro 0.942, V4.1 Flash 0.941. Its predecessor, Mercury 2.5, is 0.749. That is resemblance in raw text, not a provenance claim.

## Verification

Scoped generation added the two models, each with 125/125 freeflow, 120/120 values and an image, and refreshed Space Bunny's note; every other model was preserved exactly. Map tests (8), scoped-values tests (3) and the pricing suite (64 first-party models) pass. `test_phase19_cards.py` fails on the same price assertion as on a clean worktree of `origin/main` today, so it is not a regression. The built site (567 pages) shows:
- both straplines and prices;
- 158.3 / 220 on MiniMax;
- the CTRL1_10, LONG-replacement and OPEN_8 disclosures on their pages.

## Spend

Capture, summed from per-call costs in the published traces: MiniMax M3.1 Flash $0.64, Mercury 3 $0.13 (failed draws excluded). The OpenRouter key's usage went from $212.69 to $215.46 over the session ($2.76: both captures, analysis, repairs and two banners at about $0.14 each; other uses of the key in that window are not excluded).
