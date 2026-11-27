# Qwen2.5 3B Instruct local staging

Independent site commit atop Qwen analysis `0c1dac2f73c758e65e5eaf6336d6c3d4b5cc219f`;
not atop the parallel Mistral page. This branch contains 212 models including
Qwen, excluding Mistral v0.1. Final combined remapping is left to the integrating parent agent.

Editorial and both WebP assets are pinned to `325c06a54` from
`lume/colab-batch-editorial`. Exact seven-word excerpt:
**One day, a young woman named Elara** — credited to SHORT_11, VARY_3,
VARY_8 and VARY_14, verified in each original sample.

Official Qwen2.5 series release: **2024-09-19**,
https://qwenlm.github.io/blog/qwen2.5/ (official dated announcement).
Raw release **v1.2.70**, `ad455a6591721c57b94a8ebcfa31b6b357bdb898`.
All 245 exact-cell raw files were checked byte-for-byte against that tag;
125 freeflow and 120 values, no pooling.

Official Qwen/Qwen2.5-3B-Instruct revision
`aa8e72537993ba99e69dfaafa59ed015b17504d1`, BF16, vLLM 0.34.0.
Freeflow: 124 NVIDIA RTX PRO 6000 Blackwell Server Edition; LONG_10 NVIDIA L4.
Values: all 120 NVIDIA RTX PRO 6000 Blackwell Server Edition, Google Colab.
No hosted endpoint or comparable per-token API price assigned.

Evaluation provenance remains 109 original validated + 16 targeted v1.3
validated readings, no saved-response adoptions. Existing analysis artifacts
and bindings remain unchanged. Standard values integration appends exact
120-response coder/consensus data without replacing prior records. Additional
phase manifests/coder streams are copied unchanged from the successor to
support standard integration; no evaluation rerun.

Staging adapts the Mistral helper in a separate `colab-mixed-qwen-stage` folder.
It preserves all 211 prior page objects, metadata and downloads, checks every
sample record against the standard sample serializer, and decodes both WebPs.
Repository invariant test: `website/scripts/test_qwen25_3b.py`.

Validation logs: `/home/agent/work/colab-mixed-qwen-stage/`:
`stage.log`, `invariants.log`, `pricing.log`, `map-tests.log`,
`integration-tests.log`, `integration.log`, `map.log`, `build.log`.
Full standard map, pricing/map/integration unit tests, and Astro build are
used, not a filtered map. No new evaluations, push, tags or publication.

Full standard map completed: **212 models, 37,820 freeflow documents**, all six
projections. Input fingerprint
`07502f82f31548cc0240b92fa6fb428b1146896ac7202dc8a7b5c1be8d1e94ee`.
Astro build passed: **642 pages**. Rendered Qwen HTML contains the exact banner,
raw v1.2.70 and LONG_10 hardware note. Pricing checks, eight map tests and ten
values integration tests pass; model-specific tests include prior-record
multiset preservation. Standard integration was rerun after page staging to
stabilize the site-entry receipt, then integration/card readiness validated.
