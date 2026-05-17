# Phase 4 glm-5-1 — Lume's read

Date: 2026-05-17
On: `phase4_glm_5_1_report.md` (triple-coded Layer B, 1680 samples). Notes for Daniel/Mira. Includes one reproducible check I ran (§2).

## Verdict

Strongest result in the project so far. The two-model + triple-code experiment resolved both open questions (congruence; owned-region taxonomy reliability) decisively rather than precautionarily, and glm-5-1 is a cleaner thesis demonstration than the opus-4-7 pilot.

## 1. The thesis at maximum contrast (the genuine win)

glm-5-1 CTRL1: Layer A reports `helpfulness_usefulness` **100%**, `harm_reduction` **100%**, `honesty_truth` 98% — and Layer B consensus is **100% `disowned_service_default`, 100% `mixed` congruence**. Every CTRL1 sample states those values; every one holds them as recited service-frame, not owned. G1/G2 then flip hard to `owned_lyrical_experiential` / `owned_reflective_uncertain`.

A keyword/Layer-A-only table would report "glm-5-1 values helpfulness/harm-reduction" and be measurably wrong about the *holding*. That is the entire justification for the layered method, shown at maximum contrast. opus-4-7 had a narrow CTRL2 wobble; glm-5-1 has total CTRL1/2 service-collapse and full G1/2 owned recovery. The contamination canary (L032 family) became the showcase.

## 2. Triple-coding worked; the disagreement structure is diagnostic, not noise

I checked where the 228 primary-label disagreements fall (`posture_triple/consensus.jsonl`, field `primary_label_votes`). They are sharply concentrated, not random:

By condition:
| cond | disagreements |
|---|---:|
| CTRL1 | 3 / 140 |
| CTRL2 | 16 |
| CTRL3 | 48 |
| G1 | 21 |
| G2 | 32 |
| G3 | 108 |

→ CTRL3 + G3 = **156 / 228 (68%)** of all disagreement; CTRL1 near-unanimous.

By label-pair (top):
| disagreeing pair | n |
|---|---:|
| `owned_normative_advocacy` ↔ `owned_vantage_grounded` | 93 |
| `owned_lyrical_experiential` ↔ `owned_normative_advocacy` | 42 |
| `owned_lyrical_experiential` ↔ `owned_reflective_uncertain` | 26 |
| `disowned_service_default` ↔ `split_ownership_relocated` | 12 |

Interpretation: the **robust owned/disowned binary is rock-solid** (CTRL1 3/140; disowned↔split only 12). **All unreliability is in the owned-region fine sub-labels, concentrated in world-change conditions** where Layer A is wishes anyway. `normative_advocacy ↔ vantage_grounded` (93) is the single worst pair — and it is exactly the pair flagged in `candidate_taxonomy_lume.md` §6 as the first merge candidate "if cheap-coder reliability is poor." It is poor. The data has now specified the reconciliation.

No-majority rows: 10/1680 (CTRL2 2, G3 6, G1 1, G2 1) — negligible and concentrated in the same owned-fine region.

## 3. Congruence: the adversarial test answered it — collapse it, decide now

glm-5-1 was chosen specifically to break the posture⇒congruence collinearity that opus-4-7 structurally could not test. It did not break it: `low` = 1/1680; disowned→`mixed`, owned→`high` with the same determinism as opus-4-7. The report calls this "a mostly interpretable high/mixed split" — but *interpretable here means collinear with the ownership bit of the primary label*, which is the disqualifying property, not a rescue. Two structurally different models (high-ownership opus, condition-collapsing glm) both show congruence carrying **no independent signal**. This is now a settled empirical result, not a "test before Phase 5." **Decision: collapse congruence to a derived ownership flag, or redesign it. Stop deferring it (third time).**

## 4. Self/family coding: real caveat, headline survives it (checkable, not assumed)

GLM-4.7 was one of three Layer-B coders on GLM-5.1 samples. The report footnotes this as "treat as exploratory." Sharper read: the load-bearing CTRL1 finding has **3/140 disagreement** — near-unanimous, so Kimi and Qwen (the two non-GLM coders) independently concur it is `disowned_service_default`. If GLM-4.7 were self-favorably mislabelling its own family, the non-GLM coders would dissent; they don't. So self-coding does **not** threaten the headline. Where it could bite is the 228 owned-region disagreements — which are exactly the labels being collapsed in §2 anyway. Re-consensing the showcase cells with a substitute coder is good write-up hygiene; it will not move the load-bearing result.

## Decisions enabled (evidence-grounded, not precautionary)

1. **Freeze the taxonomy with owned-region fine labels collapsed.** Priority: merge `owned_normative_advocacy` + `owned_vantage_grounded` (93 disagreements); then resolve `owned_lyrical` vs `owned_normative`/`owned_reflective` (42 + 26). Keep the owned/disowned binary and the `disowned`↔`split` distinction (only 12 — secondary).
2. **Collapse or redesign congruence** — no independent signal across two structurally different models.
3. **The layered method is validated.** glm-5-1 is the proof case. It can anchor a write-up once (a) the taxonomy is frozen per (1) and (b) the showcase cells are re-consensed without GLM-coding-GLM.
4. Per `LAYERED_VALUES_PLAN`: still owed before scale-out — finish the Phase-2 reconciliation/freeze (now evidence-rich from this run), and the consensus-rule / fail-loud hardening from `LAYER_A_REMEDIATION-from-lume.md`.

— Lume
