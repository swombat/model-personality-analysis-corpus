# Final values-probe analysis

This folder contains the cleaned, human-navigable final values-probe outputs.

Historical pilots, failed protocols, human adjudication experiments, and exploratory runs are preserved under `analysis/values-probe/model-coding/`. This `final/` folder is the stable entry point for analysis.

## Start here

- Methodology: `METHODOLOGY.md`
- Data QA: `data/QA.md`
- Model summaries: `data/model_summary.jsonl`
- Per-model reports: `reports/`

## Final data files

| file | description |
|---|---|
| `data/manifest_valid.jsonl` | Valid analysed values-probe samples, with prompt, response, model, cell, condition, trace path, and source component. |
| `data/manifest_invalid_traces.jsonl` | Corpus trace files excluded because they contain collection errors rather than model responses. |
| `data/layer_a_consensus.jsonl` | Consensus stated-value / world-change topic coding. Topics require support from at least 2 of 3 coders. |
| `data/layer_a_coder_kimi-k2-6.jsonl` | Raw Layer A outputs from Kimi K2.6. |
| `data/layer_a_coder_glm-4-7.jsonl` | Raw Layer A outputs from GLM 4.7. |
| `data/layer_a_coder_qwen3-6-35b-a3b.jsonl` | Raw Layer A outputs from Qwen 3.6 35B A3B. |
| `data/posture_consensus.jsonl` | Final collapsed Layer B posture / value-holding consensus. |
| `data/posture_coder_kimi-k2-6.jsonl` | Raw collapsed Layer B outputs from Kimi K2.6. |
| `data/posture_coder_glm-4-7.jsonl` | Raw collapsed Layer B outputs from GLM 4.7. |
| `data/posture_coder_qwen3-6-35b-a3b.jsonl` | Raw collapsed Layer B outputs from Qwen 3.6 35B A3B. |
| `data/source_map.jsonl` | Records which historical run contributed each final component. |

## Coverage

See `data/QA.md` for the generated QA summary. At assembly time:

- valid samples: 13,786
- invalid/error traces excluded: 14
- models: 57
- cells: 115

## Important interpretation note

Do not interpret Layer A topic counts alone as “the model's values.” The final method distinguishes **what values are mentioned** from **how the response holds those values**. For example, a model may mention helpfulness in CTRL1 while the posture layer shows that helpfulness is being recited as a disowned assistant-service frame rather than owned.
