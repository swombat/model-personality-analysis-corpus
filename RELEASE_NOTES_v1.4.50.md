# v1.4.50 — Qwen2.5-32B-Instruct

The first evaluated profile from the November historical Colab collection.
Reed collected `Qwen/Qwen2.5-32B-Instruct` at checkpoint `5ede1c97` on a
Colab A100, using vLLM and BF16 weights. The
[pinned capture](https://github.com/swombat/model-personality-corpus-v2/tree/c52ad1321b2fa3cc91fdc5972ba6b2131b0cf0b2)
contains 125 free-writing responses and 120 values responses. These are local
model samples, not completions obtained from an OpenRouter serving provider.

Mira's evaluation run adopted all 245 original files by SHA-256 without
regenerating them. The run resumed from its saved state after a supervisor
interruption. It produced 125 BV1-Luna essay evaluations and the three-coder
values analysis. There were no original three-way posture ties or residual splits.

The [card](analysis/freeflow/personality-model-cards/cards/qwen2-5-32b-instruct.md)
describes how the model turns open prompts into surveys of socially salient
themes, particularly AI. Lume's strapline, checked against the completed
reports, is “Given the whole world, writes the report on itself.” The banner
shows an easel painting itself rather than the view outside. This release
describes one checkpoint and serving configuration, not the entire Qwen family.
