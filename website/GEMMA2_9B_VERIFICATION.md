# Gemma 2 9B IT local integration

- Base: analysis main `9f2edf8178dd15541afd8e13c2465f3172e0a1d9` (Qwen v1.4.50 precedent).
- Raw release: `swombat/model-personality-corpus-v2` tag `v1.2.51`, commit `fc7dc13b61c8473a4f3ba3db5c612e4dc9e103d7`.
- Source adoption: `d7c3868fe9b398dbb93132fc40e96e0739a188df`.
- Official checkpoint: `google/gemma-2-9b-it`, revision `11c9b309abf73637e4b6f9a3fa1e92e615547819`.
- Capture: local BF16, vLLM 0.34.0, Google Colab, one NVIDIA L4; not a measured hosted API endpoint. No comparable API price or capability-ladder score assigned.
- Samples: 125 freeflow (BV1-Luna `bv1-luna-v1-20260929`) and 120 values; exact local-cell alias, no pooling.
- Historical release date: **2024-06-27**, verified against Google's displayed date and `article:published_time` at https://blog.google/technology/developers/google-gemma-2/ . This is not the capture date.
- Analysis imports: original commits `5f8036f3a47c73aba575c5dc75058d42aa92be9a` and `ae58b25ec0f27004c805645e6096c55955582900`.

## Uncertainty disclosure

`G3_17` remains split after adjudication. Original votes and provisional selection are preserved, not promoted to a majority classification. The rendered page includes the warning in provenance notes, ahead of the values headline, and in detailed values analysis. Report tables retain provisional selections, so the warning explicitly explains their effect on percentages. Owned world-change advocacy is 33/40 (82.5%); owned stated-value disclosure is 0/80.

## Local verification

Run from repository root:

```sh
python3 website/scripts/test_gemma2_9b.py
python3 website/scripts/test_pricing.py
~/work/.corpus-venv/bin/python website/scripts/test_model_map.py
~/work/.corpus-venv/bin/python -m unittest discover \
  -s analysis/values-probe/final/scripts/tests -p test_capture_integration.py
(cd website && npm run build)
```

The Gemma invariant test checks exact-cell sample counts, provenance, unscored capability, disclosure, preservation of all other main model objects, and map input fingerprint. Map generation uses `~/work/.corpus-venv/bin/python website/scripts/generate_map.py`.

Final results: Gemma and Qwen invariant checks pass; all 8 map unit tests, pricing checks, and all 10 capture-integration unit tests pass. The established values integration validates against the raw checkout. Final Astro build passes with 606 pages.

Browser verification with the supplied `LD_LIBRARY_PATH=/home/agent/work/.browser-libs/usr/lib/x86_64-linux-gnu` passed desktop rendering, camera retention, all six projections, fidelity/provenance controls and keyboard tree activation. It failed the existing mobile first-viewport assertion (map top 894px); this integration does not change layout. Static rendered-page checks confirm Lume's exact strapline, supplied banner, and residual disclosure. No banner was generated through a paid service. No push, release publication, or remote tag action was performed.
