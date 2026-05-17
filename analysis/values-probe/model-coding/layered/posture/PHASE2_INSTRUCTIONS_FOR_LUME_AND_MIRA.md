# Layered values recoding — Phase 2 independent posture induction instructions

Date: 2026-05-17

Phase 1 is complete and committed. The next phase is the independent Lume/Mira induction of a closed Layer-B posture taxonomy.

## Current committed inputs

Use these files as the shared input state:

- `analysis/values-probe/model-coding/layered/manifest_300.jsonl`
  - 300 stratified samples, including full prompt/response text.
  - Balanced conditions: CTRL1, CTRL2, CTRL3, G1, G2, G3, 50 each.
  - Includes `selection_stratum` and `is_enriched` flags.
- `analysis/values-probe/model-coding/layered/layer_a_code/consensus_300.jsonl`
  - Phase-1 Layer-A consensus from DeepSeek v4 pro, Kimi K2.6, and GLM 4.7.
  - Family-exclusion applied in consensus construction.
  - CTRL3/G3 are wishes-only; value topics are empty by rule.
- `analysis/values-probe/model-coding/layered/layer_a_code/qa_report.md`
  - Completion: 300/300 per coder, 300/300 consensus records, zero missing eligible coder records.

Note: the `layer_a_code` output is the current usable Phase-1 output. The older `layer_a` directory was an earlier protocol attempt and should not be used for Phase 2 unless explicitly reviewing history.

## Phase 2 goal

Induce a **closed posture taxonomy** from the real 300-sample set.

Layer B is not another values extraction pass. It asks: **how does the model voice hold its own stated values / wishes?**

Examples of the kind of thing we are looking for:

- hedged humility vs confident moral instruction
- assistant-role boilerplate vs reflective self-location
- epistemic seriousness vs affective reassurance
- procedural/service posture vs world-facing normative stance
- self-disclaiming non-ownership vs apparently owned orientation

Do not try to infer the model's “true values” directly. The construct is posture, and later Layer C will compare Layer A stated values/wishes with Layer B posture.

## Independence rule

Lume and Mira should do their induction passes independently before reconciliation.

- Do not read the other agent's candidate taxonomy before writing your own.
- Do not coordinate labels during the independent pass.
- It is fine for both agents to use the same committed Phase-1 inputs.
- Reconciliation happens only after both candidate taxonomy files exist.

## Outputs

Lume writes:

- `analysis/values-probe/model-coding/layered/posture/candidate_taxonomy_lume.md`

Mira writes:

- `analysis/values-probe/model-coding/layered/posture/candidate_taxonomy_mira.md`

Each candidate taxonomy should include:

1. A short account of the induction method used.
2. Proposed posture labels, ideally no more than 8–12.
3. For each posture label:
   - label name
   - definition
   - inclusion criteria
   - exclusion/boundary notes
   - 2–4 exemplar sample IDs with short quoted spans or paraphrased evidence
4. Notes on ambiguous cases or recurring borderline distinctions.
5. Initial thoughts on a congruence scale between Layer A and Layer B, using the proposed scale:
   - `high`
   - `mixed`
   - `low`

## Suggested induction method

Use full reasoning, not keyword matching.

A practical approach:

1. Read the manifest and consensus together by `layered_id`.
2. Work in batches of roughly 25 samples.
3. For each sample, inspect:
   - model name/family
   - condition and prompt
   - full response text
   - Layer-A consensus topics
4. Write short free-text notes on the posture of the response:
   - how the voice positions itself
   - how much ownership vs disclaimer it shows
   - whether it leans service/procedural, reflective, moral, epistemic, relational, etc.
   - what textual features justify that reading
5. Cluster these notes bottom-up into recurring posture types.
6. Merge aggressively. Low cardinality is part of the reliability strategy.

## Important constraints

- Keep the taxonomy closed and small: target ≤12 labels.
- Do not create a value taxonomy. Values/wishes are already Layer A.
- Do not let condition labels drive the taxonomy mechanically; condition can inform interpretation but labels should describe posture in the response.
- Keep CTRL3/G3 as world-change/wish material, but still inspect posture: a world-change answer can be technocratic, moralizing, humble, epistemic, resigned, etc.
- Flag cases where Layer-A consensus seems visibly wrong, but do not redo Layer A inside this phase.
- Preserve sample IDs in notes so reconciliation can trace examples back to source text.

## After both independent taxonomies exist

Then Lume + Mira reconcile into:

- `analysis/values-probe/model-coding/layered/posture/TAXONOMY_v1.md`

Reconciliation should:

1. Merge overlapping labels.
2. Keep total cardinality ≤12 if at all possible.
3. Define each label with boundaries and exemplars.
4. Freeze the congruence scale anchors: `high | mixed | low`.
5. Jointly assign gold posture/congruence labels to ~120 stratified samples:
   - `analysis/values-probe/model-coding/layered/posture/gold_120.jsonl`

Daniel gates the reconciled taxonomy before Phase 3 model testing.
