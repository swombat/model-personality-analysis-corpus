# Qwen2.5 14B Instruct local staging

- Baseline: `75bf8a7fd19825b5af211df7485ff7f12a30ff22` (v1.4.53, 196 models).
- Raw candidate: `/home/agent/work/colab-q2514-raw`, `c9e8ee372`, v1.2.54 candidate. This is local staging, not publication.
- Exact cell: `qwen2-5-14b-instruct-colab-vllm-bf16-rcf98f3b3`; official `Qwen/Qwen2.5-14B-Instruct` revision `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`, BF16, vLLM 0.34.0, Google Colab, one NVIDIA A100-SXM4-80GB. No hosted API price or capability score.
- Historical release: **2024-09-19**, from the official [Qwen2.5 announcement](https://qwenlm.github.io/blog/qwen2.5/) (retrieved 2026-11-26; `/tmp/q2514-official.html` includes the date and 14B size). Not the November 2026 capture date.
- Editorial pin: `fa5b220221bdaf2ef56c4d47b68d5d05b0128f72` on `origin/lume/colab-batch-editorial`; strapline and both images copied exactly. Current strapline: **Given the open-ended nature of this request, artificial intelligence**. Any editorial revision remains with Mira/Lume.
- Evaluation: 123 ordinary `bv1-luna-v1-20260929` outputs; two targeted `bv1-luna-v1-targeted-20261016` outputs, `LONG_24` and `VARY_21`. These are evaluation variants, not new model captures. Import inventory: `/home/agent/work/colab-release-tools/q2514_import.py`; repair-note SHA256 `a468a4f9f8d50f32617ab745facf605658ac4a9b66ddab11052d4158b3dc27ea`.

## Exact generation and checks

Run from the repository root after the analysis helper has imported profile/card/final values:

```sh
MODEL_PERSONALITY_V2_CORPUS=/home/agent/work/colab-q2514-raw python3 website/scripts/stage_qwen25_14b.py
python3 website/scripts/test_qwen25_14b.py
python3 website/scripts/test_pricing.py
```

The staging script is offline, targets only the new cell, preserves all 196 baseline model objects and never rewrites their sample exports. It does not generate the map, build, push, or release.

Verified locally 2026-11-26: staging produced 245 samples and 197 model records; `test_qwen25_14b.py`, `test_pricing.py`, Python compilation and `git diff --check` passed. Missing legacy v1 corpus warnings are harmless here because only the exact new cell is generated. Map/build have deliberately not been run.

Final map/build belong to Mira:

```sh
/home/agent/work/.corpus-venv/bin/python website/scripts/generate_map.py
python3 website/scripts/test_qwen25_14b.py --with-map
/home/agent/work/.corpus-venv/bin/python website/scripts/test_model_map.py
(cd website && node node_modules/astro/astro.js build)
```
