# Release notes — v1.2.8

Date: 2026-06-16

## Added

- Added Corpus V2 / analysis-corpus coverage for seven models:
  - `gpt-3.5-turbo`
  - `gpt-4`
  - `gpt-4-turbo`
  - `gpt-4o-mini`
  - `gpt-4.1-mini`
  - `gpt-4.1-nano`
  - `glm-5.2`
- Added BV1 freeflow outputs, aggregate packets, rich personality profiles, concise personality cards, and website sample exports for the new models.
- Added phase10 layered values-probe data, including Layer A coder outputs, Layer A consensus, collapsed posture coder outputs, collapsed posture consensus, QA reports, and final values-probe reports for the seven models.
- Updated website generated model data with release dates and available Artificial Analysis Intelligence Index scores.
- Added Lume-provided straplines and banner/thumb images for the seven new model cards.

## QA

- Phase10 Layer A consensus: 840/840 records.
- Phase10 collapsed posture consensus: 840/840 records.
- Final values-probe assembly: 16,306 valid samples; phase10 contributes 840 samples across seven models.
- Website data generation and Astro build completed successfully.

## Notes

- Added Artificial Analysis Intelligence Index score 4 for `gpt-3.5-turbo`; `glm-5.2` remains without an AAII score because no current score was available in the checked sources/repo state.
- Transient monitor logs, lock/sentinel files, targeted retry manifests, and duplicate raw backups were removed; failed coder JSONLs and cleaned malformed-fragment JSONLs were kept as audit artifacts.
