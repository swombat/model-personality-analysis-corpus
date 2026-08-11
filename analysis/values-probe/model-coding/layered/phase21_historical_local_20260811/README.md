# Phase 21 — historical local full-precision checkpoints

Source: `model-personality-corpus-v2` v1.2.18.

Models:

- `yi-6b-chat` — official `01-ai/Yi-6B-Chat` BF16 checkpoint.
- `chatglm2-6b` — official `zai-org/chatglm2-6b` FP16 checkpoint.

This phase uses the approved independent three-LLM Layer A topic coding and
Layer B posture coding pipeline. Deterministic rule-based classification is
forbidden. The source manifest preserves each trace's local runtime, model
revision, weight precision, and hardware provenance.
