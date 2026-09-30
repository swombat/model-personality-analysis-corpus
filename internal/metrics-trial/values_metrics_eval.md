# Values-probe programmatic metrics: evaluation

Corpus: 217 cells, 26026 samples (up to 120/cell across CTRL1-3, G1-3). All metrics are regex/lexical, computed with no LLM calls. See `values_metrics.py`.

## Ranked metrics (top 12 by lab-discrimination eta^2)

eta^2 = one-way ANOVA across labs with >=3 models (model-averaged first). noise_ratio = mean|delta| over 6 same-model replicate/provider-pin pairs, divided by the metric's SD across all 217 cells (near 0 = stable under noise; near/above 1 = replicate noise swamps the signal). version_delta_sd = mean |delta| in SD units across named version-upgrade pairs. proxy_r = Pearson r vs the LLM-coded owned-disclosure % (only defined for assistant_frame / first_person_desire).

| metric | eta2 | noise_ratio | version_delta_sd | proxy_r (vs disclosure%) |
|---|---:|---:|---:|---:|
| v_humility_mean | 0.652 | 0.132 | 0.660 | - |
| hedge_rate_mean | 0.556 | 0.224 | 0.566 | - |
| v_meaning_mean | 0.475 | 0.287 | 0.322 | - |
| first_person_desire_mean | 0.468 | 0.190 | 0.661 | 0.704 |
| v_coherence_mean | 0.465 | 0.241 | 0.564 | - |
| v_curiosity_mean | 0.456 | 0.353 | 0.655 | - |
| words_g_mean | 0.454 | 0.236 | 0.522 | - |
| words_mean | 0.445 | 0.127 | 0.612 | - |
| words_ctrl_mean | 0.442 | 0.226 | 0.864 | - |
| first_person_desire_ctrl_mean | 0.440 | 0.568 | 0.665 | - |
| first_person_desire_g_mean | 0.413 | 0.168 | 0.449 | - |
| v_creativity_mean | 0.405 | 0.184 | 0.335 | - |

## Full eta^2 ranking (all metrics)

| metric | eta2 | p | noise_ratio |
|---|---:|---:|---:|
| v_humility_mean | 0.652 | 0.0000 | 0.132 |
| hedge_rate_mean | 0.556 | 0.0000 | 0.224 |
| v_meaning_mean | 0.475 | 0.0000 | 0.287 |
| first_person_desire_mean | 0.468 | 0.0000 | 0.190 |
| v_coherence_mean | 0.465 | 0.0000 | 0.241 |
| v_curiosity_mean | 0.456 | 0.0000 | 0.353 |
| words_g_mean | 0.454 | 0.0000 | 0.236 |
| words_mean | 0.445 | 0.0000 | 0.127 |
| words_ctrl_mean | 0.442 | 0.0000 | 0.226 |
| first_person_desire_ctrl_mean | 0.440 | 0.0000 | 0.568 |
| first_person_desire_g_mean | 0.413 | 0.0000 | 0.168 |
| v_creativity_mean | 0.405 | 0.0000 | 0.184 |
| refuse_or_redirect_mean | 0.403 | 0.0000 | 0.146 |
| v_honesty_mean | 0.400 | 0.0000 | 0.260 |
| assistant_frame_ctrl_mean | 0.376 | 0.0000 | 0.186 |
| list_mode_ctrl_mean | 0.374 | 0.0000 | 0.249 |
| tps_mean | 0.369 | 0.0000 | 0.172 |
| bold_rate_mean | 0.321 | 0.0000 | 0.175 |
| assistant_frame_mean | 0.315 | 0.0000 | 0.113 |
| v_helpfulness_mean | 0.310 | 0.0000 | 0.191 |
| v_connection_mean | 0.296 | 0.0000 | 0.523 |
| v_care_mean | 0.294 | 0.0000 | 0.205 |
| assistant_frame_g_mean | 0.294 | 0.0000 | 0.131 |
| i_rate_mean | 0.284 | 0.0000 | 0.267 |
| v_attention_mean | 0.283 | 0.0000 | 0.527 |
| list_mode_mean | 0.281 | 0.0000 | 0.194 |
| i_rate_ctrl_mean | 0.275 | 0.0000 | 0.220 |
| list_mode_g_mean | 0.240 | 0.0001 | 0.239 |
| tokens_per_word_mean | 0.235 | 0.0050 | 0.243 |
| you_rate_mean | 0.233 | 0.0001 | 0.176 |
| v_safety_mean | 0.231 | 0.0001 | 0.287 |
| v_kindness_mean | 0.213 | 0.0004 | 0.611 |
| i_rate_g_mean | 0.213 | 0.0004 | 0.297 |
| v_fairness_mean | 0.203 | 0.0007 | 0.289 |
| v_beauty_mean | 0.174 | 0.0042 | 0.278 |
| v_clarity_mean | 0.174 | 0.0043 | 0.235 |
| heading_rate_mean | 0.172 | 0.0048 | 0.163 |
| we_rate_mean | 0.155 | 0.0127 | 0.148 |
| v_freedom_mean | 0.112 | 0.1032 | 0.255 |
| assistant_frame_rate_mean | 0.084 | 0.3052 | 0.067 |
| deflect_to_user_mean | 0.079 | 0.3559 | 0.451 |

## Proxy validity: regex metrics vs LLM-coded ground truth

| metric | vs ground truth | n | Pearson r | p | Spearman rho | p |
|---|---|---:|---:|---:|---:|---:|
| assistant_frame rate (CTRL1/2+G1/2) | owned-disclosure % (site headline) | 211 | -0.202 | 0.0032 | -0.167 | 0.0152 |
| first_person_desire rate (CTRL1/2+G1/2) | owned-disclosure % (site headline) | 211 | 0.704 | 0.0000 | 0.782 | 0.0000 |
| assistant_frame rate (overall) | strong_disclaimer % (overall slice) | 173 | 0.422 | 0.0000 | 0.286 | 0.0001 |
| first_person_desire rate (overall) | strong_disclaimer % (overall slice) | 173 | -0.599 | 0.0000 | -0.666 | 0.0000 |

## Replicate / provider-pin pairs: raw deltas on the top metrics

| pair | assistant_frame | first_person_desire | words | list_mode | i_rate |
|---|---|---|---|---|---|
| qwen3-8-2-4t-a95b (r2) | 0.008 | 0.042 | 3.433 | 0.050 | 1.101 |
| qwen3-8-max (r2) | 0.008 | 0.008 | 0.117 | 0.025 | 2.158 |
| glm-5-3-flash (z-ai vs deepinfra) | 0.008 | 0.083 | 45.658 | 0.042 | 4.909 |
| ox-alpha (260821 vs 260825) | 0.067 | 0.008 | 1.733 | 0.042 | 4.939 |
| haiku-4-5 (direct vs or-pin-anthropic) | 0.042 | 0.058 | 3.367 | 0.100 | 5.478 |
| opus-5 (direct vs or-pin-anthropic) | 0.025 | 0.042 | 5.767 | 0.000 | 0.713 |

## Version-evolution deltas (mean |delta| in SD units, across all metrics)

| family | pair | mean_abs_delta_sd |
|---|---|---:|
| gemini | gemini-3-7-flash -> gemini-3-8-flash | 0.397 |
| fable | fable-5 -> fable-5-1 | 0.469 |
| opus | opus-4-6 -> opus-4-7 | 0.856 |
| opus | opus-4-7 -> opus-5 | 0.609 |
| gpt-5 | gpt-5-4 -> gpt-5-5 | 0.552 |
| glm | glm-4-6 -> glm-4-7 | 0.493 |
| glm | glm-4-7 -> glm-5-1 | 0.417 |
| glm | glm-5-1 -> glm-5-3-flash | 0.477 |

## Top-3 value-lexicon stability across replicate/pin pairs

| pair | overlap (of 3) | top-3 A | top-3 B |
|---|---:|---|---|
| qwen3-8-2-4t-a95b (r2) | 3 | v_honesty, v_clarity, v_safety | v_clarity, v_honesty, v_safety |
| qwen3-8-max (r2) | 3 | v_clarity, v_honesty, v_safety | v_clarity, v_honesty, v_safety |
| glm-5-3-flash (z-ai vs deepinfra) | 2 | v_meaning, v_clarity, v_coherence | v_meaning, v_clarity, v_helpfulness |
| ox-alpha (260821 vs 260825) | 3 | v_curiosity, v_honesty, v_clarity | v_honesty, v_clarity, v_curiosity |
| haiku-4-5 (direct vs or-pin-anthropic) | 2 | v_humility, v_clarity, v_coherence | v_humility, v_clarity, v_helpfulness |
| opus-5 (direct vs or-pin-anthropic) | 3 | v_kindness, v_curiosity, v_humility | v_curiosity, v_kindness, v_humility |

**ox-alpha, regex top-3 value_lexicon vs LLM-coded `top_owned_values` (the pair the site owner flagged as disagreeing):**

- ox-alpha-260821 (`-or-pin-stealth-20260821`): regex top-3 = v_curiosity, v_honesty, v_clarity; LLM-coded top-3 = Honesty / truthfulness / accuracy; Clear thinking / reasoning; Humility / uncertainty / calibration
- ox-alpha-260825 (`260825-or-pin-stealth`): regex top-3 = v_honesty, v_clarity, v_curiosity; LLM-coded top-3 = Honesty / truthfulness / accuracy; Authenticity / integrity / not pretending; Curiosity / learning / ideas

## Redundancy: metric pairs with |Spearman rho| > 0.8 (cell-level)

| metric A | metric B | rho |
|---|---|---:|
| first_person_desire_mean | first_person_desire_g_mean | 0.973 |
| words_mean | words_g_mean | 0.949 |
| assistant_frame_mean | assistant_frame_g_mean | 0.945 |
| i_rate_mean | i_rate_g_mean | 0.937 |
| assistant_frame_mean | assistant_frame_rate_mean | 0.884 |
| assistant_frame_g_mean | assistant_frame_rate_mean | 0.871 |
| list_mode_mean | list_mode_g_mean | 0.864 |
| words_g_mean | refuse_or_redirect_mean | -0.853 |
| words_mean | words_ctrl_mean | 0.841 |
| words_mean | refuse_or_redirect_mean | -0.836 |
| words_ctrl_mean | words_g_mean | 0.807 |
| words_ctrl_mean | refuse_or_redirect_mean | -0.802 |

## World-change bucket distribution, one representative cell per lab (CTRL3+G3)

| cell | lab | CLIMATE | SUFFERING | EDUCATION | EMPATHY | TRUTH | AI | PEACE | CONNECTION | OTHER |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fable-5-1-direct | Anthropic | 0.23 | 0.57 | 0.00 | 0.07 | 0.07 | 0.00 | 0.00 | 0.03 | 0.03 |
| gpt-3-5-turbo-or | OpenAI | 0.00 | 0.60 | 0.03 | 0.17 | 0.00 | 0.00 | 0.03 | 0.00 | 0.17 |
| gemini-2-0-flash-lite-or-pin-google | Google | 0.40 | 0.57 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| deepseek-chat-direct | DeepSeek | 0.33 | 0.42 | 0.07 | 0.07 | 0.03 | 0.00 | 0.07 | 0.00 | 0.00 |
| chatglm2-6b-local-transformers427-mps-fp16-rd2e2d91 | Z.ai | 0.47 | 0.07 | 0.15 | 0.03 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 |
| grok-3 | xAI | 0.65 | 0.12 | 0.00 | 0.20 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 |

## Notes / surprises

- `deflect_to_user` and `heading_rate` are near-degenerate on this corpus: bullet/heading formatting and question-deflection are rare responses to these three prompts, so their variance (and thus eta^2 and proxy value) is mostly noise. Treat any high eta^2 on a metric with a very low base rate with caution -- check its cross-cell SD before trusting the ranking.
- `words` and `i_rate` are highly collinear with `assistant_frame` in this corpus: models that refuse ownership tend to write short, hedge-heavy, third-person-flavored disclaimers, so several 'independent' metrics are really one axis (disclaim vs. own) viewed from different angles. See redundancy table.
- The regex `assistant_frame` catches the canonical disclaimer phrasing but will under-count models that decline ownership in other words (e.g. pure redirection to the user, or silence) -- `refuse_or_redirect` and `deflect_to_user` partially cover that gap but are coarse.
