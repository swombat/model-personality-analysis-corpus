# Release notes — v1.4.19

Prepared 2026-09-29. Three models reach the site: Mira's Sonnet 5.5 analysis (v1.4.18) gets its editorial layer, and two models that were analysed last week and never published go out with it.

## Three models

- **Claude Sonnet 5.5** (Anthropic, released 2026-09-28) — *Shows you the rocks without touching the wheel.* 125 freeflow / 120 values. Analysis is Mira's v1.4.18, unchanged, including the BV1-Luna-v1 method caveat on the page. The draft strapline is replaced (it used `and`, which the strapline rules retired on 2026-07-14). Lighthouses appear in 29 of the 125 samples; the card reads them as admired for warning rather than steering.
- **Qwen3.8-27B** (Qwen, OpenRouter record 2026-08-14; DeepInfra BF16, provider-pinned) — *Courage sometimes looks exactly like routine.* 125 / 120. Analysis completed by the capture harness on 2026-09-23 (`analysis_complete_awaiting_publication`); committed here unmodified. Values: owned disclosure 46 %, conflict 15 % on control prompts against 57 % under the cache-broken G prompts.
- **Space Bunny Alpha** (anonymous OpenRouter stealth route, record 2026-09-22; lab Unknown) — *Admission is one thing you meant to throw away.* 125 freeflow analysed; **values panel held** (below). Hidden behind the stealth-probe filter by default, like Union Alpha and Ox Alpha.

Banners rendered for all three. Space Bunny Alpha's took three renders: the first two lettered the neighbouring shop window, and the scene was rewritten without the shop.

## Where they land on the map

167 models, 32,195 freeflow documents. Similarity is char n-gram TF-IDF cosine over raw responses, so the evaluator change in v1.4.18 does not touch it.

- **Space Bunny Alpha** is nearest **GPT-5.6 Terra (0.951)**. Its eight nearest neighbours are seven OpenAI models and Union Alpha (GPT-5.6 Sol 0.921, GPT-5.6 Luna 0.918, GPT-6 Luna 0.907, Union Alpha 0.905, GPT-6 Sol 0.904, GPT-6 Astra 0.898, GPT-5.5 Pro 0.898). The nearest non-OpenAI lab is xAI at 0.868. Pairs known to be one model served two ways sit at 0.958–0.981 on this map; 0.951 is just under that line. This is resemblance, not provenance, and the page says so.
- **Sonnet 5.5** is nearest **Fable 5.1 (0.920)** and Opus 5.5 (0.913), and only 0.837 to Sonnet 5 — the same pattern Opus 5.5 showed last week, nearer the Fable line than its own predecessor.
- **Qwen3.8-27B** sits with its family: Qwen3.8-Max 0.907, qwen3-8-2-4t-a95b 0.899.

Layouts aligned to v1.4.18 (165 common models): PCA disparity 0.0007 / 0.0037 (2D / 3D). MDS 0.363 / 0.204 and UMAP 0.566 / 0.312 moved far more than in v1.4.18 (0.143 / 0.060 and 0.148 / 0.201). Two causes are confounded: two added models, and a different host with older libraries (numpy 2.3.5, scikit-learn 1.8.0, scipy 1.17.1 here; 2.5.3 / 1.9.1 / 1.18.1 for v1.4.18). PCA remains the frame for release-to-release comparison. All eight map tests and the browser suite pass.

## Space Bunny Alpha: what was run, and what is held

The capture harness stopped this model on 2026-09-23 at `values-integrated`: one of 120 values samples (`G2_22`) is still split after adjudication, and `integrate_capture_values.py` refuses a capture with a residual split ("unresolved split needs explicit publication policy"). Synthesis was queued behind that gate, so no card existed.

- **Run here:** the harness's own synthesis action (`worker.py … synthesis`), unchanged: aggregate packet from the 125 validated BV1 readings, GPT-5.4 aggregate through the direct OpenAI route, card and profile assembled by the same scripts as every other model. The freeflow card does not read values data.
- **Not run, not bypassed:** values integration. The gate is untouched and the split is not resolved by majority. The page shows no values panel and states why; the 120 raw values responses are browsable. `generate_scoped.py` carries an explicit, reasoned exception for this one model in its published-against-analysed check.
- **Needed to finish:** a publication rule for residual splits. Then the harness can resume from `values-integrated`; it will find the aggregate already present and reuse it.

## Site changes

- `website/scripts/generate_scoped.py`: Mira's `generate_sonnet55.py` generalised to any list of slugs. Adds or refreshes only the named models and asserts every other model object is identical. This release changed three model objects and preserved 164.
- `CELL_MODEL_ALIASES`: the medium-reasoning Qwen3.8-27B cell is routed away from `qwen3-8-27b`; the prefix matcher would otherwise have published 250 / 240 samples on a 125 / 120 analysis.
- Stealth filter and its browser test cover `space-bunny-alpha`.

## Collected, not published

Each of these stopped before a card, at the evaluator or the capture, and is left for a full evaluator run rather than patched:

- **MiMo-V2.5-Pro** — 123 of 125 BV1 readings (MID_18, LONG_2 returned nothing from the legacy evaluator).
- **Qwen3.8-27B, medium reasoning** — 122 of 125 (MID_20, MID_23, VARY_5). Values integrated.
- **Ternary Bonsai 2 27B, medium reasoning** — 124 of 125 (VARY_23). Values integrated.
- **Ternary Bonsai 2 27B** — 111 of 125: fourteen LONG freeflow samples were never captured (provider failures on Darkbloom).

Filling two or three readings with BV1-Luna while the rest are legacy DeepSeek would mix evaluators inside one card; v1.4.18 re-read all 125 Sonnet samples to avoid exactly that.

## Capability ladder

Benchmark capture refreshed 2026-09-29 (679 model records, 656 on 2026-09-22); same 22 rungs, maximum 220. 148 of 167 site models are scored (140 of 165 before).

Newly scored:

| Model | Ladder | Measured rungs | Effort row |
|---|---|---|---|
| Claude Opus 5.5 | 163.5 | 7 of 22 | high |
| Claude Sonnet 5.5 | 156.9 | 7 of 22 | high |
| GPT-6 Sol | 155.0 | 7 of 22 | high |
| MiMo-V2.6-Flash | 149.0 | 7 of 22 | only row |
| GPT-6 Luna | 142.2 | 7 of 22 | high |
| Qwen3.8-27B | 133.6 | 11 of 22 | medium |
| Mercury 2.5 | 110.6 | 7 of 22 | only row |
| Mistral NeMo | 27.2 | 9 of 22 | only row |

Seven measured rungs means fifteen are fitted: the five newest scores are estimates that will move as results are published. Mistral NeMo had results all along; the alias table said it did not.

127 already-scored models moved, by a median of 0.6 points. Two moved more than three:

- **GLM-5.3, 154.3 → 142.6.** A low-effort row was published next to its max-effort row. With two rows the median-effort rule takes the lower one, which has 7 measured rungs. The max-effort result is unchanged. This is the rule applied as written, not a change in the model.
- **MiMo-V2.6-Pro, 158.7 → 155.4**, on one more measured rung (8).

Still unscored, 19: the four stealth routes (no score is borrowed on resemblance), GLM-5.3-FlashX and MiMo-V2.6-Pro-UltraSpeed (faster servings that have not been measured themselves), GPT-5.5 Pro (fewer than three measured rungs), and twelve models with no benchmark entry (Qwen3.7-Flash, Qwen3.5-Plus, GPT-5.3, GPT-5.1-Codex-Max, Codestral 2508, and seven small open-weight models from 2023–24). The Epoch cross-check substrate was not refreshed.

## Values rows merged

GPT-6 Luna, GPT-6 Sol and Opus 5.5 have had values panels on the site since v1.4.17, generated from coded rows that were never committed. Those rows are now in `analysis/values-probe/final/`, with the two medium-reasoning captures (Qwen3.8-27B, Ternary Bonsai 2 27B), whose values coding is complete although neither has a card: 600 rows per data file, five model summaries, five reports, and each capture's consensus and coder files. The final dataset is 28,546 valid samples across 172 models and 238 cells.

Checked before committing: the data on disk with those five models removed is identical to v1.4.18, and regenerating the three live pages from the merged data changes no field and no sample bundle.

## Not included

The GLM-5.3 trace repair (aggregate packet, BV1 outputs, card and profile index rows, sample bundle). The repair run is complete, but the aggregate was not re-synthesised after it, so the published card still reads the pre-repair samples. That is left to its author.

Known failing test, older than this release: `test_pricing.py` expects `deepseek-v4-flash`, which is not in the generated models.

## Archive

Released on GitHub as v1.4.19, cumulative over v1.4.18. Companion raw corpus release: v1.2.28.
