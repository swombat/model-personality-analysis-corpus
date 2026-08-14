# Lume handoff — August 13 model batch

These cells passed strict corpus-fidelity checks and completed the freeflow and
approved three-coder values pipelines:

- `chatglm3-6b-local-transformers-mps-float16-re9e0406d`
- `mistral-7b-instruct-v0-2-local-transformers-mps-auto-r63a8b081`
- `qwen1-5-7b-chat-local-transformers-mps-auto-r5f4f5e69`
- `qwen2-7b-instruct-local-transformers-mps-auto-rf2826a00`
- `glm-4-9b-chat-hf-local-transformers-mps-auto-r8599336f`
- `grok-4-6-or-pin-xai-20260813`
- `deepseek-v4-pro-0813-direct-20260813`
- `qwen3-8-2-4t-a95b-or-pin-digitalocean`

## Inputs for straplines and pictures

- Freeflow profiles: `analysis/freeflow/personality-model-profiles/profiles/`
- Concise cards: `analysis/freeflow/personality-model-cards/cards/`
- Values reports: `analysis/values-probe/final/reports/`
- Phase provenance and QA:
  `analysis/values-probe/model-coding/layered/phase22_august13_recovery_20260814/`

The website data generator intentionally remains pending: it requires Lume's
generated straplines for these new model slugs.

DeepSeek LLM 7B and Qwen 2.5 7B failed strict recollection fidelity and remain
preserved under the corpus `discarded/` tree.
