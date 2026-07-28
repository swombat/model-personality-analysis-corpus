# LLM recoding recovery QA

- generated: 2026-07-28T13:07:25.781026+00:00
- passed: **True**
- manifest samples: 6,000
- Layer A coder records: 18,000
- Layer A consensus records: 6,000
- Layer B coder records: 18,000
- Layer B consensus records: 6,000
- affected models: 47
- unique recovery IDs: 6,000
- promoted-record API cost: $12.284436
- actual billed calls including smoke/adjudication: 36,129
- actual billed API cost: $12.365033

## Components

| component | samples | Layer A consensus | Layer B consensus | no label majority |
|---|---:|---:|---:|---:|
| `phase9_fable_5_20260610` | 120 | 120 | 120 | 0 |
| `phase12_sonnet_5_20260630` | 240 | 240 | 240 | 0 |
| `phase13_model_family_sweep_20260714` | 3960 | 3960 | 3960 | 0 |
| `phase14_grok_4_5_20260716` | 120 | 120 | 120 | 0 |
| `phase15_kimi_k3_20260716` | 120 | 120 | 120 | 0 |
| `phase16_gemini_inkling_20260721` | 360 | 360 | 360 | 0 |
| `phase17_haiku_20260722` | 360 | 360 | 360 | 0 |
| `phase18_opus5_openai_reasoning_20260725` | 720 | 720 | 720 | 0 |

## Errors

- none
