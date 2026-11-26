# Gemma 2 2B IT recovered local staging

- Baseline: `4e35d4c43095be3ff365adf9132ac4ac527eef94` (195 published models).
- Official checkpoint: `google/gemma-2-2b-it`, revision `299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8`.
- Exact capture cell: `gemma-2-2b-it-colab-vllm-bf16-r299a8560`; BF16, vLLM 0.34.0, Google Colab, one NVIDIA L4. Not a hosted endpoint; no API price or capability score assigned.
- Raw candidate: `/home/agent/work/colab-g22-raw`, `389ae4241`, v1.2.53 candidate. Raw adoption: `53147e0dcfbd5e76becdc22cbc7e0967a1c942d9`. This staging is not publication of that candidate.
- Historical release: **2024-07-31**, not the June 27 release of the 9B/27B sizes. Citation: Google, [“Smaller, safer, more transparent: Advancing responsible AI with Gemma”](https://developers.googleblog.com/en/smaller-safer-more-transparent-advancing-responsible-ai-with-gemma/), July 31, 2024. Official page retrieved 2026-11-26; `/tmp/g22-launch.html` contains `"datePublished": "2024-07-31"`.
- Editorial pinned to `origin/lume/colab-batch-editorial`, commit `fa5b220221bdaf2ef56c4d47b68d5d05b0128f72`: **Finds a forgotten world in every mote of dust**. Both banner and thumbnail are byte-exact copies from that pin.

## Recovered evaluation provenance

Source stage manifest: `/home/agent/work/colab-release-tools/recovered_stage_gemma2_2b/manifest.json`.
The evaluator is ordinarily `bv1-luna-v1-20260929`; **five** outputs use the explicitly recorded `bv1-luna-v1-targeted-20261016` variant:
`LONG_1`, `LONG_8`, `MID_6`, `MID_9`, `OPEN_4`.
These are targeted evaluation variants, not five new model captures or regenerated raw responses. Repair-note SHA256 recorded by the stage manifest:
`a468a4f9f8d50f32617ab745facf605658ac4a9b66ddab11052d4158b3dc27ea`.

Values source mappings use the registered `capture_recovery_complete_v2_…` publication-copy phase, with unchanged source contents. Analysis import and values integration are owned independently; this website change does not edit their artifacts.

## Generation and checks

Use `MODEL_PERSONALITY_V2_CORPUS=/home/agent/work/colab-g22-raw`.
Preserve all prior 195 model objects and sample exports from the baseline; absent legacy corpus data must not silently regenerate unrelated records.

```sh
python3 website/scripts/test_gemma2_2b.py
python3 website/scripts/test_pricing.py
/home/agent/work/.corpus-venv/bin/python website/scripts/test_model_map.py
/home/agent/work/.corpus-venv/bin/python website/scripts/generate_map.py
(cd website && npm run build)
```

Verified against the published [v1.2.53 raw release](https://github.com/swombat/model-personality-corpus-v2/releases/tag/v1.2.53). All 195 previous profile records and sample exports passed the preservation check. The regenerated 196-model map includes Gemma and matches its inputs (35,820 freeflow documents). The Astro build produced 610 pages; the rendered Gemma page contains the reviewed strapline. The build used `node node_modules/astro/astro.js build` because the local npm shim failed to resolve Astro’s entrypoint.
