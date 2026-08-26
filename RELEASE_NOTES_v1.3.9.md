# Release notes — v1.3.9

Prepared 2026-08-26.

## Ox Alpha identified as GLM-5.3-Flash

- On 2026-08-26 Z.ai confirmed the OpenRouter stealth model `stealth/ox-alpha`
  was GLM-5.3-Flash (320B-A18B, MIT licence, natively multimodal, 1M context),
  after tokenizer/serving-layer fingerprinting by independent testers earlier
  that day.
- Both dated snapshots (`ox-alpha-260821`, `ox-alpha-260825`) are **preserved
  unchanged** — lab `Unknown`, strapline, artwork, all coding — as a historical
  record of the stealth deployment. They are not re-attributed.
- Added an editorial provenance note to both pages (new
  `website/src/generated/model-notes.json`, rendered under the strapline;
  `notes_markdown` field in `models.json`) linking the announcement and the
  identification threads.
- A separate GLM-5.3-Flash collection under the released identifier is in
  progress; the three cells (two stealth, one named) will be compared as a
  same-weights / different-serving-context control.
