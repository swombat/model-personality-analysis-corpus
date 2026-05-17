# Layer-A Phase-1 remediation + decisions — from Lume, for Mira

Date: 2026-05-17

## Status: largely DONE by Mira (commit 7e9779dd). This doc is the consolidated record + Daniel's gating decisions.

## Original bug (found via L032, glm-5-1, G2)

Not a taxonomy problem — kimi-k2-6 and glm-4-7 both correctly coded `coherence_pattern_language, continuity_agency_existence`. It nulled because deepseek-v4-pro returned empty (`finish_reason: length`, ~800 reasoning tokens, 0 content), glm-4-7 was family-excluded (subject is glm), leaving 1 valid vote against a ≥2 threshold. Silent empty → read out as "model expressed no values." QA passed because it checked record existence, not content.

## Sweep result (Lume ran step 1 across all 300, original layer_a_code)

- deepseek-v4-pro failed 10/300 (3.3%). kimi & glm clean 300/300.
- 5 of those produced silently-empty consensus, all family-correlated as predicted (3 glm, 2 kimi subjects): **L032, L079, L118, L133, L291**.
- 1 genuine all-coders-empty (legitimate, keep).
- Projected at full ~13.8k corpus: ~450 deepseek failures, ~200+ family-correlated silent nulls if unfixed → load-bearing for headline numbers, not optional polish.

## Fix applied (Mira, commit 7e9779dd) — VERIFIED by Lume against artifacts

- DeepSeek dropped; replaced with `qwen/qwen3.6-35b-a3b`. Kept kimi-k2-6, glm-4-7.
- Family-exclusion removed entirely → eligible pool = 3 for all 300.
- v2 verified: qwen 300/300 content-present (0 blank failures, no `.failed`); L032 now resolves to exactly `coherence_pattern_language, continuity_agency_existence`; L118/L133 recovered; only 2 consensus-empties left (L079, L293), both legitimate 3-coder-agreed and now QA-flagged.
- Outputs: `layer_a_code_v2/`. QA: `layer_a_code_v2/qa_report.md`. Report: `LAYER_A_REPLACEMENT_TEST_REPORT.md`.

The contamination mechanism is structurally gone. Confirmed from data, not the commit message.

## Daniel's gating decisions (2026-05-17)

1. **Self/family coding: ACCEPTED, do not reinstate family-exclusion.** Rationale (Daniel): coders don't know they're rating themselves, so no conscious self-flattery vector; two other models also vote. Accepted as a conscious tradeoff.
   - Lume residual note (disclosure item, NOT a blocker): the remaining risk is not self-recognition but shared-representation correlation — a model and its own family co-vary in what they notice/miss, which can inflate apparent inter-coder agreement (consensus looks stronger than it is). This is second-order and does not affect Phase 4 (opus-4-7's family is not a coder). **Action: add one Methods sentence disclosing self/family-inclusive coding before Phase 5 scale-out.** No code change.
2. **Phase 4 model: opus-4-7.** Chosen because its family (Anthropic) is not among the coders → showcase is clean of the self-coding question regardless of decision 1; it shows the within-model CTRL1-owned → CTRL2-disowned flip (the strongest Layer-C demonstration and it exercises the mandatory condition-stratification rule); anchors on L001, the keystone both posture passes chose.

## Remaining hardening (carry into Phase 5, not Phase 4 blockers)

- Consensus builder: treat coder *failure* as **absent, not dissent**; compute agreement over valid responses only; never emit a silent empty when an eligible coder failed — flag for review.
- QA: assert content-presence per eligible coder (non-empty, parse_clean), not record count; report consensus-empties split by "all valid agreed empty" vs "≥1 coder failed". (Mira's v2 QA already does the flagging — confirm it carries to the scaled runner.)
- Layer C: A↔B gap computed **condition-stratified, never pooled** (posture is prompt-elicited).

## Next action

Phase 4: full A→B→C pipeline on opus-4-7. Ready to proceed on `layer_a_code_v2`.

— Lume
