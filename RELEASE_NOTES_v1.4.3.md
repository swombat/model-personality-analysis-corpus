# Release notes — v1.4.3

Prepared 2026-09-01.

## Site: Claude Fable 5.1 published

- New model page for `fable-5-1` (Claude Fable 5.1, released 2026-09-01),
  built on the 125-sample freeflow analysis and values probe added earlier
  today. Card headline: a reflective essayist drawn to the overlooked,
  load-bearing ordinary — hidden care, wear, guided noticing; values probe
  even more ownership-forward than Fable 5 (118/120 owned).
- Authored strapline: **"Where the banister shines, someone held on"** —
  chosen to perform the model's own move (a worn surface read as a record
  of quiet human care) rather than describe it. First candidate (a hinge
  line) was discarded on the sibling collision check: gpt-5 already owns
  "hinges more honored than monuments".
- Bespoke banner: a library stairwell at first light, steps dished by a
  century of feet, the banister's shine the brightest thing in the frame,
  a caretaker's broom and bucket on the half-landing.
- Wiring: first-party Anthropic API pricing ($10/$50 per MTok, since the
  OpenRouter stats endpoints 404 on launch day), AAII 66 (v4.1.1,
  retrieved 2026-09-01), release date 2026-09-01 (Anthropic announcement;
  replaces a duplicate 2026-08-28 key that reflected pre-launch staging).
- Publish hygiene: the data regeneration tried to sweep the uncommitted
  phase-29 GLM-5.3-Flash persona-ladder outputs (365 → 725 samples,
  including the dropped political side-probe) into the published samples;
  that leak was reverted — this release changes nothing but Fable 5.1.
