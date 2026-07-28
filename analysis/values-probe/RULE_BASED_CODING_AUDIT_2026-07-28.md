# Rule-based coding contamination audit — 2026-07-28

## Status

**Resolved in v1.3.0.** The audit found that the then-current assembled
values-probe data contained **6,000 Layer A records and 6,000 Layer B/posture
records across 47 models** whose sole coder provenance was
`rule_based_values_probe_extract`.

All 6,000 samples were subsequently replaced by the approved three-LLM coding
and consensus pipeline. The rebuilt final dataset contains no deterministic
coder provenance, and the assembler now fails closed if that provenance
reappears. The original finding is retained below as the correction audit.

## Affected source components

| source component | affected records per layer |
|---|---:|
| `phase9_fable_5_20260610` | 120 |
| `phase12_sonnet_5_20260630` | 240 |
| `phase13_model_family_sweep_20260714` | 3,960 |
| `phase14_grok_4_5_20260716` | 120 |
| `phase15_kimi_k3_20260716` | 120 |
| `phase16_gemini_inkling_20260721` | 360 |
| `phase17_haiku_20260722` | 360 |
| `phase18_opus5_openai_reasoning_20260725` | 720 |

## Affected models

- `codestral-2508`
- `devstral-2512`
- `fable-5`
- `gemini-3-5-flash-lite`
- `gemini-3-6-flash`
- `gpt-5-1-codex-max`
- `gpt-5-1-codex-mini`
- `gpt-5-4-mini`
- `gpt-5-4-nano`
- `gpt-5-6-luna`
- `gpt-5-6-sol`
- `gpt-5-6-terra`
- `grok-4-20-0309-non-reasoning`
- `grok-4-20-0309-reasoning`
- `grok-4-5`
- `haiku-3`
- `haiku-4-5`
- `inkling`
- `kimi-k3`
- `llama-3-1-70b-instruct`
- `llama-3-1-8b-instruct`
- `llama-3-2-11b-vision-instruct`
- `llama-3-2-1b-instruct`
- `llama-3-2-3b-instruct`
- `llama-3-3-70b-instruct`
- `llama-4-maverick`
- `llama-4-scout`
- `ministral-14b-2512`
- `ministral-3b-2512`
- `ministral-8b-2512`
- `mistral-large-2512`
- `mistral-medium-3`
- `mistral-medium-3-1`
- `mistral-medium-3-5`
- `mistral-nemo`
- `mistral-saba`
- `mistral-small-24b-instruct-2501`
- `mistral-small-2603`
- `mistral-small-3-1-24b-instruct`
- `mistral-small-3-2-24b-instruct`
- `mixtral-8x22b-instruct`
- `o1`
- `o3`
- `o3-mini`
- `o4-mini`
- `opus-5`
- `sonnet-5`

## Containment applied

1. Removed the rule-based coder from the final assembler's coder list.
2. Added a fail-closed provenance check to reject any source containing the
   forbidden coder in Layer A or Layer B consensus records.
3. Disabled every extant deterministic point-release builder script.
4. Marked the rule extractor as exploratory/historical only.
5. Corrected the final methodology to forbid deterministic coding.

The contaminated generated files were replaced during the v1.3.0 recovery.
Historical deterministic source outputs remain preserved in their original
phase directories for audit, but are not assembled into `final/data/`.
