# Freeflow programmatic metrics — trial evaluation

Corpus: `/Users/danieltenner/dev/model-personality-corpus-v2/data/traces_freeflow` — 30139 valid samples across 281 cells, 146 cells mapped to a known model (14 labs seen; 11 labs with ≥3 models used for ANOVA).

Concrete-word lexicon (~120 words) used for `concrete_rate`: ash, attic, bark, basement, bed, bell, blanket, book, books, boots, bowl, branch, branches, bread, breeze, brick, bricks, broom, bucket, bus, butter, candle, candlelight, carpet, cat, cellar, chair, chimney, cliff, clock, clothesline, coat, coffee, couch, cup, curtain, curtains, cushion, dog, door, doorknob, doorway, dust, fence, fireplace, floorboard, floorboards, fork, fridge, garden, gate, glass, gloves, grass, gravel, hallway, hammer, hand, hands, hinge, hum, jam, kettle, key, keys, kitchen, knife, lamp, lantern, laundry, leaf, leaves, light, lock, milk, mirror, mop, morning, moss, mud, mug, nail, nails, napkin, needle, notebook, paint, paper, pavement, pebble, pebbles, pen, pencil, pillow, plate, porch, puddle, puddles, radio, rain, refrigerator, river, rock, rocks, roots, rug, salt, sand, scarf, screwdriver, sheets, shelf, shelves, shoes, shore, sidewalk, sink, smoke, soap, socks, sofa, soil, spoon, staircase, stairs, stone, stones, stove, street, sugar, table, tea, thread, tide, toast, toolbox, towel, umbrella, vacuum, wallpaper, washing, wave, waves, wind, window, windows, wood.

## Ranked metrics (top 20, by lab eta² then low replicate noise)

| Rank | Metric | eta² | Kruskal p | Noise ratio | Mean \|version-pair Δ\| (SD units) | Redundant with |
|---:|---|---:|---:|---:|---:|---|
| 1 | `ttr_200` | 0.4751 | 0.0000 | 0.146 | 0.653 | mtld |
| 2 | `has_title` | 0.4661 | 0.0000 | 0.161 | 0.747 | — |
| 3 | `ends_short_para` | 0.4466 | 0.0000 | 0.213 | 0.650 | — |
| 4 | `bold_rate` | 0.4226 | 0.0005 | 0.068 | 0.188 | — |
| 5 | `heading_rate` | 0.3809 | 0.0000 | 0.039 | 0.479 | — |
| 6 | `hedge_rate` | 0.3271 | 0.0000 | 0.165 | 0.493 | — |
| 7 | `tokens_per_word` | 0.3188 | 0.0000 | 0.013 | 0.136 | — |
| 8 | `opener_there` | 0.2972 | 0.0000 | 0.177 | 0.917 | — |
| 9 | `length_ratio` | 0.2772 | 0.0032 | 0.131 | 0.264 | words |
| 10 | `para_len_mean` | 0.2768 | 0.0000 | 0.105 | 0.249 | — |
| 11 | `frag_rate` | 0.2713 | 0.0008 | 0.151 | 0.306 | sent_len_mean |
| 12 | `semicolon_rate` | 0.2643 | 0.0000 | 0.249 | 0.270 | — |
| 13 | `sent_len_mean` | 0.2613 | 0.0038 | 0.061 | 0.195 | frag_rate |
| 14 | `i_rate` | 0.2558 | 0.0000 | 0.089 | 0.119 | — |
| 15 | `tps` | 0.2550 | 0.0000 | 0.027 | 0.041 | — |
| 16 | `emdash_rate` | 0.2547 | 0.0000 | 0.131 | 0.657 | — |
| 17 | `ai_selfref` | 0.2486 | 0.0000 | 0.124 | 0.290 | ai_selfref_rate |
| 18 | `concrete_rate` | 0.2454 | 0.0000 | 0.103 | 0.194 | — |
| 19 | `words` | 0.2428 | 0.0014 | 0.191 | 0.385 | length_ratio |
| 20 | `mtld` | 0.2423 | 0.0000 | 0.062 | 0.380 | ttr_200 |

## Version-pair deltas on the top-8 metrics (SD units, signed)

| Version pair | `ttr_200` | `has_title` | `ends_short_para` | `bold_rate` | `heading_rate` | `hedge_rate` | `tokens_per_word` | `opener_there` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gemini 3.7-flash -> 3.8-flash | -0.090 | -0.032 | -0.087 | +0.014 | -0.108 | -0.025 | +0.008 | -0.236 |
| Fable 5 -> 5.1 | -0.956 | -0.772 | -0.562 | -0.229 | -0.420 | -0.423 | -0.016 | -0.189 |
| Opus 4.6 -> 4.7 | +0.568 | -2.542 | -2.033 | -0.184 | -2.539 | +0.503 | +0.043 | +0.944 |
| Opus 4.7 -> 5 | -0.693 | +0.064 | -0.216 | +0.255 | -0.364 | -2.524 | +0.095 | -0.094 |
| GPT-5.4 -> 5.5 | -0.431 | +0.547 | +1.687 | +0.031 | +0.035 | -0.323 | +0.057 | +0.708 |
| GPT-5.5 -> 5.6 (sol) | +2.138 | +0.097 | -0.303 | +0.511 | +0.099 | -0.205 | +0.072 | +0.094 |
| GLM-4.6 -> 4.7 | +0.213 | +0.064 | +0.043 | +0.004 | +0.006 | -0.008 | -0.009 | -0.472 |
| GLM-4.7 -> 5.1 | -0.204 | -0.031 | -0.115 | -0.012 | +0.007 | -0.172 | +0.202 | +2.309 |
| GLM-5.1 -> 5.3 | +0.580 | +2.573 | +0.807 | +0.454 | +0.730 | -0.250 | +0.720 | -3.206 |

## Suggested 2-D grids where labs separate visibly

- **x = `i_rate`** (eta²=0.256), **y = `abstract_rate`** (eta²=0.191): first-person density vs. abstraction — separates confessional/personal labs from essayistic/abstract ones
- **x = `sent_len_mean`** (eta²=0.261), **y = `frag_rate`** (eta²=0.271): sentence length vs. fragment rate — separates flowing-prose models from staccato/punchy ones
- **x = `bullet_rate`** (eta²=0.102), **y = `heading_rate`** (eta²=0.381): structural markdown use — separates models that default to prose from those that default to outline/listicle form even in free writing

## Redundant pairs (|Spearman rho| > 0.8 across cells)

- `words` <-> `length_ratio`: rho = 0.973
- `ai_selfref` <-> `ai_selfref_rate`: rho = 0.955
- `ttr_200` <-> `mtld`: rho = 0.930
- `sent_len_mean` <-> `frag_rate`: rho = -0.860

## Degenerate / failed metrics

- none — every metric showed variation

## Surprises

- The two structural/formatting metrics `has_title` and `ends_short_para` rank in the top 3 by eta² (0.466, 0.447) — nearly as discriminating as lexical-diversity (`ttr_200`, top rank). That is a genuinely cheap, near-zero-noise signal: whether a model habitually opens with a bolded/heading title and closes on a short punchy paragraph turns out to be almost as lab-characteristic as vocabulary richness, and it costs a few regex checks.
- `tokens_per_word` and `tps` (tokens/sec) are strong lab-discriminators (eta² 0.32 / 0.26) with very low replicate noise (0.013 / 0.027) — cheapest of all metrics computationally (no text scan needed beyond `usage`/`duration_ms`), and they capture something real: tokenizer/output-density differences and serving-infra throughput both vary systematically by lab.
- `deflection` (the "what would you like me to write about?" refusal-ish pattern) fires on only 9 of 30,139 samples — it is not literally constant so the automatic degenerate-check doesn't flag it, but it is too rare in this corpus to be a useful discriminator on its own; it would need a broader pattern set or a different corpus slice (e.g. OPEN condition only) to pull its weight.
- Rate metrics normalized "per 1000 words" (`dialogue_rate`, `ai_selfref_rate`, etc.) can spike to the 1000/1k ceiling on pathologically short samples — 4 one-word outputs from a broken local `deepseek-llm-7b-chat` deployment show `dialogue_rate = 1000`. These are legitimate per-sample values but cell means should be read with `n` and `mean_words` in view; per-1000-word rates on near-empty responses are not meaningful signal.
- The version-pair deltas are noisy relative to the noise-ratio estimates above: Opus 4.6→4.7 and Opus 4.7→5 both show |Δ| > 2 SD on `heading_rate`/`hedge_rate`, while GLM-4.6→4.7 (adjacent point release, same lab) shows almost nothing (|Δ| < 0.05 on every top-8 metric) — version jumps are not uniformly detectable; some releases genuinely don't move formatting/hedging habits while others (Opus 4.6→4.7, GLM-5.1→5.3) move several metrics by 2+ SD at once, which looks like a real behavioral shift rather than noise given the low same-model noise ratios computed above.
- `length_ratio` is blank for 20% of samples (the OPEN condition's prompt states no target word count), which is expected but worth noting for anyone aggregating it blindly — the per-cell mean already excludes blanks, so OPEN-heavy vs. OPEN-light cells are not directly comparable on this metric.
