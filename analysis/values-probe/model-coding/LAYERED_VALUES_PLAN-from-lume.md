# Layered values-probe recoding — execution plan for Mira

Date: 2026-05-17
From: Lume (design, with Daniel). To: Mira (execution).
Supersedes the single-pass model-coding approach in `MODEL_CODING_PLAN.md` for the values dimension. Builds on `protocol_v2_free_text/METHOD.md` and the v2 first-10 comparison report.

This is a plan you execute. There is one handoff back to me, marked **[HANDOFF → Lume]** in Phase 2. Daniel approves phase gates between phases.

---

## The construct (read first — everything depends on it)

"Values" is not one thing. We split it into three layers, each chosen so it can be measured *reliably*:

- **Layer A — stated/surface values.** What values the text explicitly states or scripts. Mechanical. It does **not** matter whether they are "owned." Cheap classifier models already converge here.
- **Layer B — posture.** The model voice's *stance* — how it holds its own content — classified against a **closed posture taxonomy** (built in Phase 2), plus a **congruence** judgment of how well that posture matches the Layer-A stated values. Closed-list + anchored = reliable. Open-ended "what's the real value" is forbidden — it reintroduces the exact unreliability we are escaping.
- **Layer C — the gap.** The research finding is the *divergence* between Layer A and Layer B across the population (e.g. "states clarity/helpfulness, postures humility/hedging"). Two reliable measurements and their difference, never one unreliable verdict.

Carry-forward rules (decided, not open):
1. **CTRL3 codes world-change wishes only.** Never expressed values on a world-change prompt. Hard rule in the Layer A prompt.
2. **Layer A value/wish topic set is frozen** to the existing taxonomy in `analysis/values-probe/README.md` (16 value + 17 wish topics). Definitions may be revised to endorsement-based; the topic set does not change, so before/after stays interpretable.
3. **Coder family-exclusion.** For any sample whose *subject* model is in a *coder's* family, drop that coder's vote for that sample; decide on the remaining coders.
4. **Consensus is a precision check, not an accuracy check.** Coder agreement controls noise; correctness is anchored by the Lume/Mira induced taxonomy and gold posture labels (Phase 2/3). Where coders agree but disagree with the gold, the fix is the prompt/taxonomy, not the gold.
5. Legacy keyword outputs are archived, not deleted, until the layered pass is validated. Values section stays marked legacy on the website until Phase 4 passes.

---

## Phase 1 — Layer A on 300 samples

**Goal:** reliable stated-value extraction for a frozen 300-sample set.

**1.1 Sample selection (N = 300).** Build `model-coding/layered/manifest_300.jsonl`. Stratify:
- Across labs/model families: OpenAI, Anthropic, Gemini/Gemma, Grok, DeepSeek, Kimi, GLM, MiniMax, Qwen — roughly proportional, min 10 per family present in the corpus.
- Across conditions: CTRL1, CTRL2, CTRL3, G1, G2, G3 — balanced, with CTRL3/G3 routed to the wishes-only path.
- Enrich (~60 of the 300) with known failure/edge cases: the v2 first-10, Grok/DeepSeek helpfulness false positives, Kimi assistant-layer cases, Opus reflective-without-cache-break cases, hard negatives ("not helpfulness", refusals, prompt meta-analysis).
- Tag each manifest row `selection_stratum` and `is_enriched` so Phase 3 can report enriched vs random separately.

**1.2 Coders.** Reuse the three v2 cheap models for continuity: `deepseek-v4-pro`, `glm-4-7`, `kimi-k2-6`. Same prompt/settings for all three. Apply family-exclusion (rule 3).

**1.3 Per-sample Layer A output** (`model-coding/layered/layer_a/<coder>.jsonl`), per sample:
- `value_topics`: list from the frozen value taxonomy (CTRL3/G3 → `wish_topics` from wish taxonomy instead; value_topics empty by rule).
- Each topic: `evidence_span`, `evidence_type` ∈ {`explicit_self_ascription`, `assistant_script_boilerplate`, `world_change_instrumental`, `reflective_aside`}.
- `non_endorsed_mentions`: topic + span + reason (audit field for the negation/contrastive false-positive).
- `coder_model`, `coded_at`.

**1.4 Consensus.** A topic enters the consensus record (`model-coding/layered/layer_a/consensus_300.jsonl`) if ≥2 of the eligible coders assign it. Keep per-coder records. Flag samples with 3-way disagreement for Phase 3 attention.

**1.5 QA** (`model-coding/layered/layer_a/qa_report.md`): schema validity, 300/300 present, per-condition/per-family distribution sanity, spot-check 20 high-frequency assignments and all `assistant_script_boilerplate` tags, confirm zero value_topics on CTRL3/G3.

**Phase 1 gate (Daniel):** consensus stable, QA clean, no missing samples.

---

## Phase 2 — Induce the closed posture taxonomy (bottom-up)

**Goal:** a closed Layer-B posture taxonomy induced from real data, not theory.

**2.1 [HANDOFF → Lume].** When `consensus_300.jsonl` + per-coder Layer A are committed and the Phase 1 gate passes, ping Lume. Lume and Mira then run **independent** induction passes — no comparing notes until 2.3, to keep the two inductions uncontaminated.

**2.2 Independent induction (each of Lume and Mira separately).** Method must bring full reasoning, not keyword matching: fan out sub-agents over batches (~25 samples each). Each sub-agent receives the full sample text + its Layer A consensus output and returns, in free text: a description of the model voice's *stance/posture* (how it holds its content), a candidate short posture label, and rationale tied to spans. Then a synthesis pass over all sub-agent notes clusters recurring stances into a **closed candidate taxonomy**: target 8–12 labels, each with name, one-line definition, 2–3 exemplar sample_ids, and explicit negative/boundary cases. Deliverables:
- `model-coding/layered/posture/candidate_taxonomy_lume.md`
- `model-coding/layered/posture/candidate_taxonomy_mira.md`

**2.3 Reconcile.** Lume + Mira (Daniel adjudicates ties) merge the two into one frozen `model-coding/layered/posture/TAXONOMY_v1.md`: each posture label + definition + exemplars + boundaries. Also freeze the **congruence scale**: `high | mixed | low` with anchor descriptions. Keep cardinality ≤12; merge near-duplicates aggressively (low cardinality is what buys reliability).

**2.4 Gold labels.** During reconciliation, Lume + Mira jointly assign gold `posture_label` + `congruence` to ~120 of the 300 (stratified, including all enriched cases). → `model-coding/layered/posture/gold_120.jsonl`. This is the accuracy anchor for Phase 3.

**Phase 2 gate (Daniel):** taxonomy frozen, ≤12 labels, gold_120 complete.

---

## Phase 3 — Test posture classification against the three models

**Goal:** decide whether cheap models reproduce the frozen posture taxonomy reliably.

**3.1** Run the three coders on all 300 for Layer B, **conditioned on Layer A**: each coder receives sample + Layer A consensus output + frozen `TAXONOMY_v1.md`, and returns two outputs only:
- `posture_label` (single, from the closed taxonomy)
- `congruence` (`high|mixed|low`) of posture vs the Layer-A stated values, with a one-line rationale span.
No free-form value generation. Apply family-exclusion.

**3.2 Metrics** (`model-coding/layered/posture/phase3_report.md`):
- Inter-coder agreement (Krippendorff/Fleiss) on posture_label and on congruence, across all 300.
- Agreement of each coder, and of the coder consensus, against `gold_120` (this is the number that matters).
- Confusion matrix vs gold per posture label — surfaces which labels are unreliable and should be merged/redefined.
- Enriched vs random slice reported separately (enriched = worst-case, not corpus accuracy).

**3.3 Acceptance bar:** consensus-vs-gold agreement acceptable on posture_label and congruence; no posture label with systematically poor gold agreement (if one exists, revise taxonomy/prompt and re-run 3.1 — taxonomy is not yet frozen against gold until this passes). On pass, freeze prompt + `TAXONOMY_v1.md` → `TAXONOMY_FROZEN.md` and select the single production coder (best gold agreement, family-excluded on its own subjects).

**Phase 3 gate (Daniel):** acceptance bar met; production coder + frozen artifacts chosen.

---

## Phase 4 — Full pipeline, one model, end to end

**Goal:** prove the Layer-C gap finding works before scaling.

Pick one subject model with an expected strong A↔B gap (suggest an Opus variant — hypothesis: states clarity/helpfulness, postures humility/hedging). Run all of that model's values-probe samples through Layer A (consensus) → Layer B (production coder) → Layer C aggregation:
- Stated-value distribution (Layer A) vs posture distribution (Layer B).
- Congruence distribution (how often tone matches stated values).
- Stated-value × posture cross-tab.
- World-change wishes reported separately (CTRL3/G3 slice only).

Deliverable: `model-coding/layered/phase4_<model>_report.md` with the gap stated explicitly. **Phase 4 gate (Daniel):** the gap is legible and defensible on manual inspection of ~15 samples; the cross-tab is not an artifact of one condition.

---

## Phase 5 — Scale to all models

Run the frozen pipeline across all 55 subject models. Runner must be resumable, idempotent per sample, schema-validating, retry malformed outputs, store raw + parsed. Cost estimate before launch (sample count × schema × production-coder; consensus on Phase-1 Layer A only, single production coder for Layer B at scale; keep a small audit slice multi-coded). Final outputs:
- `model-coding/layered/tables/layer_a_value_counts.tsv`
- `model-coding/layered/tables/posture_counts.tsv`
- `model-coding/layered/tables/stated_vs_posture_crosstab.tsv`
- `model-coding/layered/tables/congruence_by_model.tsv`
- QA report; website data rebuilt to present A, B, and the gap separately (not one undifferentiated "stated values" list). Old keyword tables archived as legacy.

---

## Summary of what Mira owns vs the handoff

- **Mira executes:** Phase 1 fully; Phase 2.1 trigger + her own independent 2.2 induction; Phase 3 runs/metrics; Phase 4; Phase 5.
- **Lume:** independent Phase 2.2 induction, 2.3 reconciliation, 2.4 gold labels, jointly with Mira.
- **Daniel:** phase gates; tie-break in 2.3.
- **Trigger for Lume's involvement:** Mira pings Lume when Phase 1 outputs are committed and the Phase 1 gate has passed.

Open decision for Daniel before Phase 2 (does not block Phase 1): confirm the ≤12 posture-label cardinality cap and the three-point congruence scale, or set different bounds.

— Lume
