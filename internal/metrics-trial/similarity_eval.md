# Similarity/mode-collapse metrics — trial evaluation

TF-IDF (sklearn, sublinear tf, l2-norm, ~150-word stoplist, top 20k content
tokens) fit once over all 30,139 non-empty freeflow samples across 281 cells
(150 distinct model mappings incl. 4 unmapped local/coding cells). Full
pipeline (load + fit + all metrics): **~24s**. Second-pass eval (replicate
noise, eta², version pairs, Ox Alpha): **<1s** from a pickled intermediate.
No LLM calls, no embeddings API, no reimplemented stopword/TF-IDF bugs —
cell→model mapping reused verbatim from the website's `generate_data.py`.

## Replicate sanity check

Two versions of "do replicates cluster together":

| check | result |
|---|---|
| Strict: A's single nearest cell is exactly its paired cell B (or vice versa), over 66 replicate/date-repin/same-lab-pin pairs | 37/66 = **0.56** |
| Looser: for every cell whose model has ≥2 cells, its single nearest cell belongs to the **same model** | 156/172 = **0.91** |

The strict number looks weak but is an artifact: models with 3+ near-duplicate
cells (e.g. `gpt-5-1-direct`, `-r2`, `-r3`, `-or-pin-openai`) compete for
"nearest" rank among each other, so A's nearest is often a third sibling cell
rather than the specific B being tested. The 0.91 same-model rate is the real
sanity check, and it's strong: vocabulary similarity reliably re-identifies
"same model, different serving route" as closer than any cross-model pair.

## Noise ratio (replicate |Δ| / SD across all cells) and lab discrimination (η²)

| metric | noise ratio | η² across labs (n=141 models, 11 labs≥3) |
|---|---|---|
| self_sim_mean | 0.146 | 0.153 |
| self_sim_LONG | 0.308 | 0.200 |
| self_sim_p90 | 0.120 | 0.238 |
| centroid_norm_spread | **0.634** | 0.155 |
| motif_concentration | 0.112 | 0.162 |

Noise ratio < 1 everywhere means real cell-to-cell variance dominates
replicate/routing noise for all five metrics — usable. `centroid_norm_spread`
is noisiest (routing/replicate variation eats ~63% of its spread), so weight
it less in any composite score. η² values (15–24%) say labs explain a real
but modest share of variance in these five metrics alone — a useful signal,
not a strong classifier by itself (full centroids do much better, see LOO
below).

## Leave-one-out nearest-centroid lab classification

Overall accuracy **0.678** (99/146; chance ≈ 1/11≈0.09 for labs≥3, lower for
singletons).

| lab | accuracy | lab | accuracy |
|---|---|---|---|
| Meta | 8/8 = 1.00 | Moonshot AI | 5/7 = 0.71 |
| Anthropic | 14/16 = 0.88 | DeepSeek | 3/5 = 0.60 |
| Google | 13/15 = 0.87 | OpenAI | 20/34 = 0.59 |
| Mistral | 14/17 = 0.82 | Qwen | 7/15 = 0.47 |
| xAI | 9/11 = 0.82 | MiniMax | 1/3 = 0.33 |
| — | — | **Z.ai | 1/10 = 0.10** |

Z.ai's near-chance score isn't noise — its own models don't agree with each
other (see GLM chain below), so no stable "Z.ai centroid" exists to classify
into. OpenAI's mediocre 0.59 is a volume effect: 34 OpenAI cells (many
GPT-5.x variants/personas/replicates) create many chances to be pulled toward
a neighboring lab on any given draw.

## Version pairs (model-centroid cosine, self_sim_mean, top-30 word deltas)

| pair | cosine | self_sim (old→new) | notable shift |
|---|---|---|---|
| gemini-3.7-flash → 3.8-flash | 0.924 | 0.109→0.107 | color words (black/blue/gray) enter; scene words (horizon/stillness) leave — cosmetic |
| **fable-5 → fable-5-1** | 0.811 | 0.108→0.098 | etymology/language motif (latin, languages, threshold, thresholds, words) leaves; plainer relational vocabulary (anyone, nothing, person, kind, want) enters |
| opus-4-6 → 4-7 | 0.776 | 0.126→0.135 | notable drift even one version apart |
| opus-4-7 → 5 | 0.785 | 0.135→0.125 | comparable drift again — Opus line moves more per-version than Gemini/GPT |
| gpt-5-4 → 5-5 | 0.918 | 0.141→0.148 | minor, mostly synonym swaps |
| gpt-5-5 → 5-6-luna/sol/terra | 0.861 / 0.827 / **0.762** | 0.148→0.142/0.110/0.141 | 3 named personas diverge from base *and* from each other; sol is both least-similar-to-base and least self-repetitive (self_sim 0.110) |
| glm-4-6 → 4-7 | 0.937 | 0.093→0.095 | stable |
| glm-4-7 → 5-1 | 0.910 | 0.095→0.091 | stable |
| **glm-5-1 → 5-3** | **0.648** | 0.091→0.082 | major break: loses imagistic/atmospheric vocabulary (dark, dust, ocean, quiet, silence, twilight, water) for generic pronoun/quantifier vocabulary (anything, everyone, nobody, somebody, thing, whole, word) |

The GLM 5.1→5.3 break (cosine 0.648, far below every other consecutive-version
pair in this table) is the direct explanation for Z.ai's 0.10 LOO accuracy
above — it's a real, large stylistic discontinuity, not a measurement
artifact (title/opening-trigram dup rates and self_sim for the two cells are
both well within normal range individually).

## Ox Alpha attribution

Both stealth cells (`-20260821`, `-20260825-repin`) are internally consistent
(pairwise cosine 0.913, each other's nearest cell) and point the same way:

| | top-1 | top-2 | top-3 |
|---|---|---|---|
| ox-alpha-260821 | glm-5-3-flash (Z.ai) 0.891 | kimi-k3 (Moonshot) 0.840 | glm-5-3 (Z.ai) 0.827 |
| ox-alpha-260825 | glm-5-3-flash (Z.ai) 0.903 | kimi-k3 (Moonshot) 0.844 | glm-5-3 (Z.ai) 0.831 |

**Model-level nearest-neighbor evidence confirms the prior hypothesis:
glm-5-3-flash is unambiguously the closest match**, by a wide margin (0.89–0.90
vs 0.84 for the runner-up), and consistent across both probe dates.

One honest complication: the **lab-centroid ranking** (averaging all of a
lab's models) puts Moonshot AI *above* Z.ai (0.82–0.83 vs 0.76–0.77). This is
the same Z.ai-heterogeneity problem as above — GLM 4.6/4.7/5.1 and 5.3 are
different enough from each other that the Z.ai lab centroid is a poor summary
of "what glm-5-3-flash sounds like." The single-nearest-model comparison is
the trustworthy read here; the lab-average comparison is misleading for any
lab with large internal version drift, and should be flagged as such if used
in the final methodology.

## Two suggested 2-D grids

- **self_sim_mean (x) vs lab_margin (y)**: separates "generically repetitive"
  (high self_sim, low margin — resembles everyone) from "distinctively
  repetitive" (high self_sim, high margin — repeats itself in a way specific
  to its own lab), with the interesting quadrant being high-margin/low-self_sim
  (varied, but only within a lab-typical range).
- **centroid_norm_spread (x) vs motif_concentration (y)**: dispersion vs
  vocabulary-lock-in. Low spread + high motif_concentration = tightest mode
  collapse (small fixed vocabulary reused near-verbatim); high spread + low
  motif_concentration = genuinely varied writers.

## Honesty notes

- `glm-4-6-coding-direct`, `glm-5-1-coding-direct`,
  `deepseek-llm-7b-chat-local-...`, `qwen2-5-7b-instruct-local-...` don't map
  to any model in `models.json` (coding-specialized/local variants excluded
  by `model_from_cell`'s own logic) — kept as pseudo-models rather than
  dropped, so they still appear in the TSVs but not in lab rollups.
- `minimax-m2-direct` behaves oddly: its `-r4`/`-r5` replicates exist in the
  corpus but the base `minimax-m2-direct` isn't consistently each other's
  nearest neighbor with `-r2`/`-r3` either — MiniMax also has the lowest LOO
  accuracy (0.33) after Z.ai, so this may be a genuinely higher-variance
  model rather than a metric problem.
- η² and noise-ratio numbers used one row per model (cells averaged), while
  the cell-level TSV keeps every serving route separate — a real analysis
  pass should decide once whether "unit of analysis" is cell or model and
  hold it constant throughout, this trial mixes both deliberately to show
  both views.

## Files

- `/Users/danieltenner/dev/model-personality-analysis-corpus/internal/metrics-trial/similarity_metrics.py`
- `/Users/danieltenner/dev/model-personality-analysis-corpus/internal/metrics-trial/similarity_eval.py`
- `/Users/danieltenner/dev/model-personality-analysis-corpus/internal/metrics-trial/similarity_cell_metrics.tsv`
- `/Users/danieltenner/dev/model-personality-analysis-corpus/internal/metrics-trial/similarity_nearest.tsv`
- `/Users/danieltenner/dev/model-personality-analysis-corpus/internal/metrics-trial/eval_output.txt` (raw eval run log)
