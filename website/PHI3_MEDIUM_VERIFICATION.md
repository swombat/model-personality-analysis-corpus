# Phi-3 Medium 4K local staging

- Base: `be1a4e926b4ab653d5606e9fd81935c86d2fcf76` (Gemma v1.4.51).
- Early analysis review commit: `9c67f26fc`.
- Raw published release: v1.2.52, `90fd625e1`; source adoption `8a887ae154a7a2fa7f3fe2d72d3926f930a5b2bd`.
- Official checkpoint: microsoft/Phi-3-medium-4k-instruct, revision `48d87cd5e0523b430d77e93becd3655cd6897230`.
- Capture: BF16, vLLM 0.34.0, Google Colab, one NVIDIA A100-SXM4-80GB. Not a measured hosted endpoint; no API price or capability score assigned.
- Historical release date: **2024-05-21**, verified from Microsoft's official [model card](https://huggingface.co/microsoft/Phi-3-medium-4k-instruct): “Release dates: The model weight is released on May 21, 2024.” Retrieved source `/tmp/phi-official-card.md`, line 177.
- Editorial text pinned to `0eb843c1684959bc73395ca668fee6194003f73e`: **Give it room and it files a titled magazine feature**. Banner and thumbnail match supplied assets at `fa5b220221bdaf2ef56c4d47b68d5d05b0128f72`.

## Integration and review

Imported the immutable stage manifest from `~/work/colab-release-tools/phi-medium`. All 245 raw SHA256s verified against `~/work/colab-phi-medium-raw`: 125 freeflow and 120 values, one exact cell, no pooling. BV1 evaluator: `bv1-luna-v1-20260929`.

Used unchanged publication worker `integrate_values` and `card_ready`, then validated integration with the raw checkout. Queue terminal metadata remains unchanged and analysis-only. Initial `G3_30` split resolved through the preserved independent adjudication; no residual splits. Original votes retained.

Site generation uses `MODEL_PERSONALITY_V2_CORPUS=~/work/colab-phi-medium-raw`. The absent legacy v1 checkout produces warnings and regenerates unrelated old prose; all prior 194 published model objects and previous sample exports are therefore preserved from the base, rather than accepting unrelated changes. New invariant test enforces exact prior-model equality.

## Checks

Commands from repository root:

```sh
python3 website/scripts/test_phi3_medium.py
python3 website/scripts/test_pricing.py
~/work/.corpus-venv/bin/python website/scripts/test_model_map.py
~/work/.corpus-venv/bin/python -m unittest discover \
  -s analysis/values-probe/final/scripts/tests -p test_capture_integration.py
~/work/.corpus-venv/bin/python website/scripts/generate_map.py
(cd website && npm run build)
```

Pricing passes, all eight map unit tests and all ten integration unit tests pass. Final Phi invariant passes, including exact map strapline, 245 samples, prior-model equality, pinned assets and map fingerprint. Prior integrated JSONL records are all retained.

Final map contains 195 models and 35,695 freeflow documents. All six projections generated; final Astro build passes with 608 pages. Static rendered profile checks confirm the exact revised strapline, supplied banner and local hardware provenance. No browser-interaction claims are made for this staging.

Capability refresh's default path points at an unavailable Mac substrate checkout. Rather than sourcing new benchmark data, the established unscored record is used, unchanged from the Gemma precedent.

Logs: `/tmp/phi-{map-final,invariants,build-final,pricing,map-test,values-test}.log`. No pushes, tags, release actions, queue edits, or provider calls.
