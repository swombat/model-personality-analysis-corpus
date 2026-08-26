# Phase 28 — GLM 5.3 Flash DeepInfra values attribution

Values-only replication of `z-ai/glm-5.3-flash` through OpenRouter, pinned to
DeepInfra with fallbacks disabled, collected August 26, 2026.

- values: 120/120 non-empty
- purpose: distinguish weight-level behavior from Z.AI serving-layer behavior
- comparison targets: Z.AI-hosted GLM-5.3-Flash and Ox Alpha 260821/260825

Result: DeepInfra does not behave as a materially separate model. Freeflow was
therefore not collected. The values cell is retained as an independent-provider
replication and folded into the GLM-5.3-Flash reading.

See `PROVIDER_COMPARISON.md`.
