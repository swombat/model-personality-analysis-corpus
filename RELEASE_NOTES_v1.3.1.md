# Release notes — v1.3.1

Prepared and released 2026-08-01.

## Added

- Added full freeflow personality coverage for three new models
  (all released 2026-07-31):
  - **DeepSeek V4 Flash** (`deepseek-v4-flash-0731`, direct API snapshot).
  - **Inkling Small** (`inkling-small`, Thinking Machines Lab, via
    OpenRouter pinned to DeepInfra).
  - **Qwen 3.7 Flash** (`qwen3-7-flash`, via OpenRouter pinned to Alibaba).
  - 125 freeflow samples per model; 375 new BV1 per-sample readings
    (final QA bad count: 0); three cell aggregates, three rich model
    profiles, three concise personality cards.
- Added editorial assets for all three models: straplines
  (single-phrase house rules) and oil-painterly banner/thumbnail images.
- Added release-date metadata for all three models.

## Values probe — recorded but not yet promoted

Phase-19 layered values coding for the three new models is included in this
release under
`analysis/values-probe/model-coding/layered/phase19_flash_small_20260731/`:

- 360 samples (120 per model), coded independently by the three approved
  LLM coders (`kimi-k2-6`, `glm-4-7`, `qwen3-6-35b-a3b`) at both layers:
  1,080 Layer A coder records plus consensus, and 1,080 collapsed-posture
  coder records plus consensus. No deterministic coder was used anywhere.
- 6 samples produced three-way posture splits with no majority. One
  adjudication round (18 further coder judgments) resolved 5 of the 6;
  1 sample remains without a two-coder majority.
- These results have **not yet been merged into the final values dataset,
  tables, or browser data**. The three new models currently appear on the
  site with personality coverage only (no values panel). Promotion into
  the final values dataset — including final adjudication of the remaining
  split and regeneration of the values tables — is deferred to a
  subsequent release rather than rushed here, in keeping with the
  fail-closed posture adopted in v1.3.0.

## Maintenance

- BV1 sample IDs across existing cell aggregate packets were renumbered by
  the re-indexed evaluation run (mechanical; no readings changed).
- `model-cell-difference-analysis/decisions.json` trimmed of per-call token
  usage metadata; unrun entries now marked `skipped`.
- Layered values coding scripts made path-relative and aligned with the
  documented three-coder roster.
- Website data regeneration extended with slug, lab, and release-date
  mappings for the three new models.

## Coverage

- Freeflow personality cards/profiles: **128 models**.
- Published freeflow samples in the browser: **49,780**.
- Layered values-probe models in the final dataset: **128** (unchanged;
  the three new models pend values promotion).
