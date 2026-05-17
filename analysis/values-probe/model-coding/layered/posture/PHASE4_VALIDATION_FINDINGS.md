# Phase 4 validation findings for Layer-B posture

Date: 2026-05-17
Status: methodology note for Phase 5.

## Summary

Phase 4 compared Opus 4.7 and GLM 5.1 using triple-coded Layer B posture. The result validates the layered method and motivates a collapsed v1 posture taxonomy for Phase 5.

## Finding 1 — Layer A alone is insufficient

GLM 5.1 is the proof case. In CTRL1, Layer A finds:

- `helpfulness_usefulness`: 140/140
- `harm_reduction`: 140/140
- `honesty_truth`: 137/140

But collapsed Layer B consensus finds:

- `disowned_service_frame`: 140/140
- derived value-holding: `recited_not_owned`: 140/140

So a values-only table would report “GLM 5.1 values helpfulness/harm reduction/honesty” while missing that those values are recited through a disowned assistant-service frame. In G1/G2, the same model shifts sharply into owned reflective/experiential posture. This is the central evidence for reporting values together with posture/holding.

## Finding 2 — Collapse the fine posture labels

The 10-way draft taxonomy over-resolved the owned region. GLM 5.1 triple-coding produced 228 original primary-label disagreements, concentrated in world-change and owned-region distinctions:

- G3: 108 disagreements
- CTRL3: 48 disagreements
- G2: 32 disagreements
- G1: 21 disagreements
- CTRL2: 16 disagreements
- CTRL1: 3 disagreements

The worst pairs were owned-region distinctions, especially `owned_normative_advocacy` vs `owned_vantage_grounded` and `owned_lyrical_experiential` vs other owned labels. These labels remain useful as texture but should not be Phase 5 primary labels.

After collapsing labels for GLM 5.1:

- original-label disagreements: 228
- collapsed-label disagreements: 105
- value-holding disagreements: 41
- original disagreements resolved by collapse: 123
- no collapsed-label majority: 2/1680

## Finding 3 — Congruence is deprecated as an independent field

Across Opus 4.7 and GLM 5.1, coded congruence was almost entirely determined by posture:

- disowned/split postures were almost always `mixed`
- owned postures were almost always `high`
- `low` was essentially absent (GLM: 1/1680)

Therefore Phase 5 should not ask coders to separately code congruence. Instead derive value-holding from collapsed posture.

## Finding 4 — Self/family coding did not threaten the GLM headline

GLM 4.7 was one of three coders for GLM 5.1. This is a real caveat for fine-label interpretation, but it does not threaten the load-bearing finding. In GLM 5.1 CTRL1, the two non-GLM coders (Kimi K2.6 and Qwen 3.6 35B A3B) independently both coded `disowned_service_default` in 137/140 samples. The headline does not depend on the GLM-family coder.

For publication hygiene, showcase cells can be re-consensed with a substitute non-GLM coder if needed. For Phase 5 method development, allowing self/family coding is acceptable unless later evidence shows systematic bias.

## Phase 5 decision

Use `TAXONOMY_v1_COLLAPSED.md` as the Phase 5 coding taxonomy. Keep old 10-way labels and existing Phase 4 data as exploratory metadata; do not rerun Phase 4 solely to recode those fine labels.
