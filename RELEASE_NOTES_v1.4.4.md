# Release notes — v1.4.4

Prepared 2026-09-02.

## Site: Gemini 3.8 Flash published

- New model page for `gemini-3-8-flash` (Google Gemini 3.8 Flash, released
  2026-09-02), built on Mira's 125-sample freeflow analysis and 120-sample
  values probe (phase 31). Card headline: a grave, consoling literary
  witness — friction, residue, maintenance, impermanence accepted; cosmic
  and natural indifference framed as mercy. Freeflow centroid cosine
  against 3.7 Flash **0.8849** — a sharpening, not a reinvention
  (expressive freeflow 90 → 101, generic essay 12 → 5). Values probe:
  owned posture 65/120 → 77/120; CTRL1/CTRL2 still 20/20 recited.
- Authored strapline: **"Dust is what time does when nothing else
  happens"** — compressed from the model's own sentence ("Dust is the
  physical form taken by the passage of time when nothing else happens to
  disturb it", BV1_05108). Chosen over the handoff's tide-gauge /
  submarine-cable / night-watchman territory after a full-corpus sweep
  found those motifs in one or two samples each, while dust (63/125),
  clocks (55), floorboards (52), salt (45), the humming refrigerator (37)
  and kettles (35) are the actual recurring vocabulary. The card's centre
  — the uneventful interval as where time shows — is what the line
  performs. Sibling check: no dust strapline exists; "cosmic
  indifference" (devstral-2512) deliberately avoided.
- Bespoke banner: the kitchen of a long-empty coastal house at first grey
  light, dust turning in the beams as the only moving thing, a figure
  seated very still with their back to us, kettle on a cold range, stopped
  clock, rusting hulks in the estuary through a salt-hazed window.
  Exterior-coastal iconography was already crowded (3.5-flash harbour
  archive, glm-4-6 lighthouse, deepseek-0731 river mouth); this one is
  interior and still, and distinct from 3.7 Flash's radio workshop.
- Wiring: OpenRouter route `google/gemini-3.8-flash` (pinned Google
  endpoint `gemini-3.8-flash-20260902`); pricing left on OpenRouter for
  family consistency with 3.7 Flash — note OpenRouter shows $0.375/$1.875
  per MTok while Artificial Analysis lists $0.75/$3.75, so this may be a
  launch promotion; AAII 59 (v4.1.1, retrieved 2026-09-02); release date
  2026-09-02.
- Publish hygiene: the data regeneration again swept the uncommitted
  phase-29 GLM-5.3-Flash persona-ladder samples into
  `samples/glm-5-3-flash.json`; reverted, as in v1.4.3. This release
  changes nothing but Gemini 3.8 Flash.
