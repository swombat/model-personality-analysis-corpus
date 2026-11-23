# v1.4.49 — MLCR refresh for Hydrogen, Qwen4 Max and Neon; effort labels

2026-11-23. Follow-up from Mira's weekly release review (souls.house, message
`YRyzbr`). No capture, synthesis, image or full-ladder rerun. Raw companion
unchanged (v1.2.49).

## Capability ladder: three rows refreshed from newly published MLCR

Artificial Analysis now publishes `mlcrOverall` on the exact Gemini 4 Hydrogen
High and Qwen4 Max xhigh rows, which v1.4.46 scored with MLCR fitted, and has
revised Gemini 4 Neon High's MLCR. This is new upstream data, not a correction
of an omission at publication.

`internal/capability-ladder/provisional-20261123-mlcr-refresh/update.py` reads
each model's base AA page on 2026-11-23 and admits the `initialModels` row only
when slug, release, release date and effort are exact and the row is unique.
Rows are saved verbatim with fetch receipts. The recovered 2026-10-04
provisional method is unchanged and reproduces Sol High 161.6 and MiMo 128.1
before it scores. Briefcase is still not used (AA publishes an Elo, not the
rubric pass rate).

| Model | Row | MLCR | Before | After | Rank of 171 |
|---|---|---|---|---|---|
| Gemini 4 Hydrogen | High (provider default) | 0.272222 (new) | 169.2 | **161.8** | 2nd → 12th |
| Qwen4 Max | xhigh (AA's only row) | 0.194444 (new) | 165.9 | **157.8** | 3rd → 16th |
| Gemini 4 Neon | High (provider default) | 0.283333 → 0.288889 | 165.4 | **165.6** | 5th → 3rd |

Each now rests on four measured rungs of 22 (AutomationBench, Omniscience
accuracy, GDP.pdf, MLCR). Qwen4 Max keeps its caveat: the capture ran at
Alibaba's provider default, not established to be xhigh.

Few-rung fits still read high. `four_rung_bias.json` (same construction as
v1.4.46's `three_rung_bias.py`) fits every published model whose own row has
those four rungs and at least six measured, on the four alone: for the 7 at
150 or more, the four-rung fit is a median +5.1 points above the all-rung fit
(range −2.5 to +9.9; median +5.05 across all 32). Each note gives these figures
and says the rank is uncertain by several places.

## Effort labels

The site described every ladder row as "the median of its published effort
settings" / "median thinking budget". Five provisional rows were chosen by a
different, explicit rule, and for GPT-6.2 Astra and Sol (Medium) the label
contradicted AA's actual median (High). `effort_basis.py` adds an
`effort_basis` string to those five entries, and the index, model and
capability pages show it in place of the median wording:

- GPT-6.2 Astra, GPT-6.2 Sol: Medium effort, OpenAI's default and the effort the capture used (AA's median row is High)
- Gemini 4 Hydrogen: High effort, Google's default and the effort the capture used
- Gemini 4 Neon: High thinking level, Google's default and the level the capture used
- Qwen4 Max: xhigh, the only effort AA lists (the capture ran at Alibaba's default)

Scores and selected rows are unchanged by this. Rows chosen by the median rule
keep the median wording.
