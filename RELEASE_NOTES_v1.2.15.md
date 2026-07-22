# Release notes — v1.2.15

Prepared 2026-07-22 from `model-personality-corpus-v2` v1.2.15.

## Added

- Added complete analysis coverage for Claude 3 Haiku and Claude Haiku 4.5:
  - 375 BV1 per-sample freeflow readings across three deployment cells.
  - Three cell aggregates, two rich model profiles, and two concise
    personality cards.
  - A route-comparison report for the direct and OpenRouter-Anthropic Haiku
    4.5 cells.
  - Rule-based values extraction and phase 17 layered values coding over 360
    samples.
  - Final layered values reports for both models.
- Added release-date and Artificial Analysis Intelligence Index metadata:
  - Claude 3 Haiku: released 2024-03-13; AAII 4.
  - Claude Haiku 4.5: released 2025-10-15; AAII 31.

## Coverage

- Freeflow BV1: 26,350 analyzed samples; final QA bad count: 0.
- Freeflow model profiles/cards: 120.
- Values: 21,946 valid samples across 183 cells and 123 layered-analysis
  models.

## Access audit

- Claude 3 Haiku is no longer callable through the configured Anthropic direct
  account, but remains callable through OpenRouter's Amazon Bedrock upstream.
- Claude 3.5 Haiku was tested and is no longer callable through either the
  configured Anthropic direct account or OpenRouter.
- Claude Haiku 4.5 remains callable directly and through OpenRouter's
  Anthropic upstream.
- The moving `Claude Haiku Latest` alias resolves to Haiku 4.5 and was not
  analyzed as a separate model.

## Pending editorial pass

- The Haiku 3 and Haiku 4.5 personality cards are ready for Lume to add the
  final straplines and banner/thumbnail images.
- Website model data should be regenerated after those editorial assets are
  present.
