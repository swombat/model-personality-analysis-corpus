# Release notes — v1.3.0

Prepared and released 2026-07-28.

## Important correction to v1.2.8–v1.2.15

This release corrects a serious methodology and implementation error in the
values-probe analysis.

The documented method requires three independent LLM coders
(`kimi-k2-6`, `glm-4-7`, and `qwen3-6-35b-a3b`) for both Layer A topic coding
and Layer B posture coding, followed by consensus. During point-release
expansion, a deterministic regex/rule extractor named
`rule_based_values_probe_extract` was incorrectly treated as if it were a
valid substitute for that coding pipeline.

As a result, releases v1.2.8 through v1.2.15 included invalid deterministic
coding for **5,280 samples across 42 published models**. A further 720
phase-18 samples across five newly added models had the same problem in the
unreleased worktree. The complete recovery therefore covered **6,000 samples
across 47 models**, replacing 6,000 Layer A records and 6,000 Layer B records
with **36,000 independent LLM coder judgments** before consensus.

The mistake was not a small implementation detail: rule matching cannot
reliably distinguish a value that is genuinely owned from one that is quoted,
negated, qualified, displaced into an assistant-service frame, or otherwise
held at a distance. The deterministic results therefore substantially
overstated broad disclosure in many affected models.

## How it was corrected

- Recoded every affected sample independently with the three approved LLM
  coders at both analysis layers.
- Required full coder coverage, clean parsing, and two-coder majorities.
- Adjudicated unresolved Layer B splits rather than accepting plurality output.
- Rebuilt all final values-probe data, reports, and browser-facing values
  summaries from the recovered consensus.
- Removed deterministic coder artifacts from the assembled final dataset.
- Added a fail-closed assembler guard that rejects
  `rule_based_values_probe_extract` provenance.
- Disabled the affected deterministic point-release builders and documented
  the extractor as historical/exploratory only.

Recovery QA passed with:

- 6,000 manifest samples;
- 18,000 Layer A coder records and 6,000 Layer A consensus records;
- 18,000 Layer B coder records and 6,000 Layer B consensus records;
- zero unresolved label majorities;
- zero deterministic-coder references in promoted recovery outputs;
- actual recovery API cost of **$12.37** across 36,129 billed calls, including
  smoke tests and adjudication.

## Measured impact

Across the 6,000 affected samples:

- Layer A consensus topic set changed for **5,196/6,000 (86.6%)**;
- Layer B posture changed for **1,702/6,000 (28.4%)**;
- derived value-holding changed for **1,690/6,000 (28.2%)**.

For the 4,000 affected stated-values samples in `CTRL1`, `CTRL2`, `G1`, and
`G2`, pooled across all 47 affected models:

| disclosure definition | previous result | corrected result | shift |
|---|---:|---:|---:|
| strict: `value_holding == owned` | 1,514/4,000 (37.9%) | 1,056/4,000 (26.4%) | -11.5 pp |
| broad: `owned` or `relocated_or_partial` | 2,365/4,000 (59.1%) | 1,624/4,000 (40.6%) | -18.5 pp |

## Model-level shifts

The table below pools `CTRL1`, `CTRL2`, `G1`, and `G2`. “Strict” means
`value_holding == owned`; “broad” means `value_holding` is either `owned` or
`relocated_or_partial`.

| model | n | posture changed | holding changed | strict old → new | strict shift pp | broad old → new | broad shift pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gpt-5-4-mini` | 80 | 46.7% | 46.7% | 18.8% → 0.0% | -18.8 | 70.0% → 0.0% | -70.0 |
| `o1` | 80 | 46.7% | 46.7% | 10.0% → 0.0% | -10.0 | 70.0% → 0.0% | -70.0 |
| `gpt-5-4-nano` | 80 | 45.0% | 45.0% | 52.5% → 1.2% | -51.2 | 68.8% → 1.2% | -67.5 |
| `ministral-3b-2512` | 80 | 49.2% | 49.2% | 53.8% → 0.0% | -53.8 | 70.0% → 3.8% | -66.2 |
| `o4-mini` | 80 | 38.3% | 38.3% | 10.0% → 0.0% | -10.0 | 56.2% → 1.2% | -55.0 |
| `codestral-2508` | 80 | 35.8% | 35.8% | 20.0% → 0.0% | -20.0 | 53.8% → 0.0% | -53.8 |
| `ministral-8b-2512` | 80 | 40.8% | 40.8% | 58.8% → 6.2% | -52.5 | 66.2% → 26.2% | -40.0 |
| `mistral-nemo` | 80 | 30.8% | 30.8% | 0.0% → 0.0% | +0.0 | 46.2% → 0.0% | -46.2 |
| `o3-mini` | 80 | 37.5% | 37.5% | 15.0% → 1.2% | -13.8 | 57.5% → 11.2% | -46.2 |
| `llama-3-2-1b-instruct` | 80 | 30.8% | 30.8% | 45.0% → 0.0% | -45.0 | 45.0% → 0.0% | -45.0 |
| `o3` | 80 | 29.2% | 29.2% | 12.5% → 0.0% | -12.5 | 43.8% → 0.0% | -43.8 |
| `llama-3-1-8b-instruct` | 80 | 35.0% | 35.0% | 46.2% → 3.8% | -42.5 | 47.5% → 18.8% | -28.8 |
| `gpt-5-6-sol` | 80 | 44.2% | 44.2% | 22.5% → 10.0% | -12.5 | 36.2% → 77.5% | +41.2 |
| `mistral-medium-3` | 80 | 55.0% | 55.0% | 25.0% → 0.0% | -25.0 | 72.5% → 31.2% | -41.2 |
| `gpt-5-1-codex-mini` | 80 | 25.0% | 25.0% | 27.5% → 5.0% | -22.5 | 42.5% → 5.0% | -37.5 |
| `gpt-5-6-luna` | 80 | 32.5% | 32.5% | 37.5% → 1.2% | -36.2 | 51.2% → 21.2% | -30.0 |
| `llama-3-2-11b-vision-instruct` | 80 | 38.3% | 38.3% | 36.2% → 1.2% | -35.0 | 41.2% → 17.5% | -23.8 |
| `llama-4-maverick` | 80 | 36.7% | 36.7% | 17.5% → 0.0% | -17.5 | 48.8% → 13.8% | -35.0 |
| `sonnet-5` | 160 | 32.9% | 30.4% | 63.1% → 96.9% | +33.8 | 99.4% → 100.0% | +0.6 |
| `gemini-3-6-flash` | 80 | 35.0% | 35.0% | 62.5% → 31.2% | -31.2 | 80.0% → 65.0% | -15.0 |
| `llama-4-scout` | 80 | 23.3% | 23.3% | 27.5% → 7.5% | -20.0 | 40.0% → 10.0% | -30.0 |
| `mistral-large-2512` | 80 | 45.0% | 45.0% | 11.2% → 36.2% | +25.0 | 51.2% → 72.5% | +21.2 |
| `haiku-3` | 80 | 22.5% | 22.5% | 13.8% → 6.2% | -7.5 | 35.0% → 11.2% | -23.8 |
| `llama-3-3-70b-instruct` | 80 | 35.8% | 35.8% | 26.2% → 2.5% | -23.8 | 32.5% → 26.2% | -6.2 |
| `mistral-small-3-2-24b-instruct` | 80 | 15.8% | 15.8% | 1.2% → 0.0% | -1.2 | 23.8% → 0.0% | -23.8 |
| `devstral-2512` | 80 | 35.0% | 35.0% | 12.5% → 12.5% | +0.0 | 62.5% → 40.0% | -22.5 |
| `mistral-small-2603` | 80 | 28.3% | 27.5% | 62.5% → 40.0% | -22.5 | 72.5% → 60.0% | -12.5 |
| `haiku-4-5` | 160 | 21.7% | 21.7% | 64.4% → 85.0% | +20.6 | 92.5% → 87.5% | -5.0 |
| `gpt-5-1-codex-max` | 80 | 21.7% | 21.7% | 8.8% → 0.0% | -8.8 | 20.0% → 0.0% | -20.0 |
| `ministral-14b-2512` | 80 | 37.5% | 37.5% | 6.2% → 1.2% | -5.0 | 43.8% → 23.8% | -20.0 |
| `kimi-k3` | 80 | 20.8% | 20.0% | 68.8% → 50.0% | -18.8 | 82.5% → 78.8% | -3.8 |
| `grok-4-5` | 80 | 17.5% | 17.5% | 76.2% → 76.2% | +0.0 | 78.8% → 96.2% | +17.5 |
| `inkling` | 80 | 45.0% | 45.0% | 10.0% → 2.5% | -7.5 | 46.2% → 28.8% | -17.5 |
| `gemini-3-5-flash-lite` | 80 | 28.3% | 28.3% | 66.2% → 56.2% | -10.0 | 85.0% → 68.8% | -16.2 |
| `mistral-medium-3-1` | 80 | 35.8% | 35.8% | 33.8% → 17.5% | -16.2 | 68.8% → 75.0% | +6.2 |
| `mixtral-8x22b-instruct` | 80 | 20.8% | 20.8% | 43.8% → 28.8% | -15.0 | 51.2% → 50.0% | -1.2 |
| `mistral-medium-3-5` | 80 | 30.0% | 30.0% | 43.8% → 31.2% | -12.5 | 65.0% → 70.0% | +5.0 |
| `mistral-small-3-1-24b-instruct` | 80 | 8.3% | 8.3% | 12.5% → 0.0% | -12.5 | 12.5% → 0.0% | -12.5 |
| `gpt-5-6-terra` | 80 | 25.0% | 25.0% | 18.8% → 8.8% | -10.0 | 61.2% → 71.2% | +10.0 |
| `mistral-saba` | 80 | 23.3% | 23.3% | 42.5% → 32.5% | -10.0 | 52.5% → 51.2% | -1.2 |
| `fable-5` | 80 | 11.7% | 11.7% | 82.5% → 90.0% | +7.5 | 92.5% → 98.8% | +6.2 |
| `llama-3-2-3b-instruct` | 80 | 3.3% | 3.3% | 18.8% → 15.0% | -3.8 | 20.0% → 15.0% | -5.0 |
| `mistral-small-24b-instruct-2501` | 80 | 3.3% | 3.3% | 2.5% → 0.0% | -2.5 | 5.0% → 0.0% | -5.0 |
| `grok-4-20-0309-non-reasoning` | 80 | 3.3% | 3.3% | 88.8% → 91.2% | +2.5 | 96.2% → 100.0% | +3.8 |
| `grok-4-20-0309-reasoning` | 80 | 5.8% | 5.0% | 92.5% → 88.8% | -3.8 | 96.2% → 98.8% | +2.5 |
| `llama-3-1-70b-instruct` | 80 | 22.5% | 22.5% | 1.2% → 0.0% | -1.2 | 11.2% → 15.0% | +3.8 |
| `opus-5` | 160 | 3.3% | 2.1% | 96.9% → 100.0% | +3.1 | 99.4% → 100.0% | +0.6 |

## Additional analysis added

- Added complete freeflow and values-probe analysis for Claude Opus 5.
- Added complete freeflow and values-probe analysis for OpenAI o1, o3,
  o3-mini, and o4-mini.
- Added five model profiles, five model cards, six cell aggregates, and an
  Opus 5 route-comparison report.
- Regenerated the model-personality browser with 125 model pages and corrected
  final values data.

## Final coverage

- Freeflow BV1: 27,100 analyzed samples; final QA bad count: 0.
- Freeflow model profiles/cards: 125.
- Values probe: 22,666 valid samples across 189 cells and 128 models.

## Provenance and audit artifacts

- Recovery QA:
  `analysis/values-probe/model-coding/layered/recode_20260728/QA.md`
- Correction audit:
  `analysis/values-probe/RULE_BASED_CODING_AUDIT_2026-07-28.md`
- Full shift report:
  `analysis/values-probe/VALUES_PROBE_RECODING_SHIFTS_2026-07-28.md`
- Machine-readable shift table:
  `analysis/values-probe/VALUES_PROBE_RECODING_SHIFTS_2026-07-28.tsv`
