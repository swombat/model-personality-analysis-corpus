# LLM recoding recovery plan — 2026-07-28

## Purpose

Replace every Layer A and Layer B record produced by
`rule_based_values_probe_extract` with results from the approved three-LLM
coding and consensus pipeline, rebuild the final values-probe dataset, and
produce a clean model-level disclosure table for later correction of the
ChatGPT-thaw article.

This is a recovery operation. Do not update the blog or its chart during this
run.

## Read first

- `RULE_BASED_CODING_AUDIT_2026-07-28.md`
- `RULE_BASED_CODING_DEPRECATED.md`
- `final/METHODOLOGY.md`
- `model-coding/layered/posture/TAXONOMY_v1_COLLAPSED.md`

## Non-negotiable constraints

1. Preserve all existing worktree changes. Do not reset, clean, delete, or
   overwrite the historical deterministic outputs.
2. Use exactly these three approved coders for both layers:
   - `kimi-k2-6`
   - `glm-4-7`
   - `qwen3-6-35b-a3b`
3. Do not use `deepseek-v4-pro` merely because the Layer A runner still exposes
   it as an option.
4. Do not use family exclusion; the core published methodology allowed
   self/family coding.
5. Layer B must consume the newly generated Layer A LLM consensus—not the old
   deterministic consensus.
6. No component may be promoted with missing coder records, parse failures, or
   unresolved Layer B samples lacking a two-coder majority.
7. The final assembler's forbidden-coder guard must remain enabled.

## Scope

Eight source components are contaminated:

| source component | samples |
|---|---:|
| `phase9_fable_5_20260610` | 120 |
| `phase12_sonnet_5_20260630` | 240 |
| `phase13_model_family_sweep_20260714` | 3,960 |
| `phase14_grok_4_5_20260716` | 120 |
| `phase15_kimi_k3_20260716` | 120 |
| `phase16_gemini_inkling_20260721` | 360 |
| `phase17_haiku_20260722` | 360 |
| `phase18_opus5_openai_reasoning_20260725` | 720 |

Total: **6,000 samples across 47 models**. Each sample requires three Layer A
judgments and three Layer B judgments: **36,000 model-coder calls** before
retries.

## Phase 0 — establish a safe baseline

Work from:

```bash
cd /Users/danieltenner/dev/model-personality-analysis-corpus
```

Record, but do not alter:

```bash
git status --short
git diff -- analysis/values-probe \
  internal/scripts/analysis-scripts/values_probe_extract.py \
  > /tmp/values-probe-recovery-start.diff
```

Confirm the containment guard currently fails on the first contaminated
component:

```bash
python3 analysis/values-probe/final/scripts/assemble_final_values_probe.py
```

Expected result: non-zero exit mentioning
`phase9_fable_5_20260610` and the forbidden coder. If assembly succeeds, stop:
the containment change is missing or broken.

Confirm `OPENROUTER_API_KEY` exists without printing it:

```bash
test -n "$OPENROUTER_API_KEY" && echo "OPENROUTER_API_KEY is set"
```

## Phase 1 — create isolated recovery directories

Never write new LLM outputs into the old deterministic directories. Use:

```text
analysis/values-probe/model-coding/layered/recode_20260728/
  phase9_fable_5_20260610/
  phase12_sonnet_5_20260630/
  phase13_model_family_sweep_20260714/
  phase14_grok_4_5_20260716/
  phase15_kimi_k3_20260716/
  phase16_gemini_inkling_20260721/
  phase17_haiku_20260722/
  phase18_opus5_openai_reasoning_20260725/
```

Each component directory must contain:

```text
layer_a/
  kimi-k2-6.jsonl
  glm-4-7.jsonl
  qwen3-6-35b-a3b.jsonl
  consensus_300.jsonl
  qa_report.md
posture_collapsed/
  kimi-k2-6.jsonl
  glm-4-7.jsonl
  qwen3-6-35b-a3b.jsonl
  consensus.jsonl
  consensus.qa.md
```

## Phase 2 — run a bounded smoke test

Before launching 36,000 calls, run ten samples from the smallest component
through all three Layer A coders:

```bash
BASE=analysis/values-probe/model-coding/layered
SRC=$BASE/phase9_fable_5_20260610
REC=$BASE/recode_20260728/phase9_fable_5_20260610

for coder in kimi-k2-6 glm-4-7 qwen3-6-35b-a3b; do
  python3 "$BASE/run_layer_a_code_coders.py" \
    --coder "$coder" \
    --manifest "$SRC/manifest_fable_5.jsonl" \
    --outdir "$REC/layer_a-smoke" \
    --limit 10 \
    --workers 3
done
```

Check that every output has ten unique `layered_id` values, `parse_clean=true`,
non-empty `raw_text`, and the expected `coder_key`. Do not begin the full run
until this passes.

Delete only the isolated `layer_a-smoke` directory after inspection. Do not
touch historical source outputs.

## Phase 3 — run Layer A for every affected component

Manifest mapping:

| component | manifest |
|---|---|
| phase 9 | `phase9_fable_5_20260610/manifest_fable_5.jsonl` |
| phase 12 | `phase12_sonnet_5_20260630/manifest_sonnet_5.jsonl` |
| phase 13 | `phase13_model_family_sweep_20260714/manifest_phase13.jsonl` |
| phase 14 | `phase14_grok_4_5_20260716/manifest_phase14.jsonl` |
| phase 15 | `phase15_kimi_k3_20260716/manifest_phase15.jsonl` |
| phase 16 | `phase16_gemini_inkling_20260721/manifest_phase16.jsonl` |
| phase 17 | `phase17_haiku_20260722/manifest_phase17.jsonl` |
| phase 18 | `phase18_opus5_openai_reasoning_20260725/manifest_phase18.jsonl` |

For each component:

```bash
BASE=analysis/values-probe/model-coding/layered
COMPONENT=phase12_sonnet_5_20260630       # change per component
MANIFEST=manifest_sonnet_5.jsonl          # change per table above
SRC="$BASE/$COMPONENT"
REC="$BASE/recode_20260728/$COMPONENT"

for coder in kimi-k2-6 glm-4-7 qwen3-6-35b-a3b; do
  python3 "$BASE/run_layer_a_code_coders.py" \
    --coder "$coder" \
    --manifest "$SRC/$MANIFEST" \
    --outdir "$REC/layer_a" \
    --workers 6
done
```

The runner is resumable: successful `layered_id` records are skipped on rerun.
Do not treat entries in `*.failed.jsonl` as final failure counts; verify the
successful output coverage after retries.

Build Layer A consensus:

```bash
python3 "$BASE/build_layer_a_consensus.py" \
  --manifest "$SRC/$MANIFEST" \
  --outdir "recode_20260728/$COMPONENT/layer_a" \
  --coders "kimi-k2-6,glm-4-7,qwen3-6-35b-a3b"
```

### Layer A promotion gate

For every component:

- each coder output has exactly one successful record per manifest
  `layered_id`;
- no duplicate successful `layered_id`;
- all records have `parse_clean=true`;
- all `raw_text` fields are non-empty;
- `qa_report.md` reports zero missing eligible coder records;
- consensus record count equals manifest count;
- every `eligible_coders` set contains exactly the approved three coders;
- neither raw outputs nor consensus mention
  `rule_based_values_probe_extract`.

Stop and repair any component that fails. Do not continue that component to
Layer B.

## Phase 4 — run Layer B posture coding

For each component that passed Layer A:

```bash
BASE=analysis/values-probe/model-coding/layered
COMPONENT=phase12_sonnet_5_20260630       # change per component
MANIFEST=manifest_sonnet_5.jsonl          # change per table above
SRC="$BASE/$COMPONENT"
REC="$BASE/recode_20260728/$COMPONENT"

for coder in kimi-k2-6 glm-4-7 qwen3-6-35b-a3b; do
  python3 "$BASE/run_posture_coder_collapsed.py" \
    --coder "$coder" \
    --manifest "$SRC/$MANIFEST" \
    --consensus "$REC/layer_a/consensus_300.jsonl" \
    --outdir "$REC/posture_collapsed" \
    --workers 6
done
```

Build Layer B consensus:

```bash
python3 "$BASE/build_posture_collapsed_consensus.py" \
  --manifest "$SRC/$MANIFEST" \
  --indir "$REC/posture_collapsed" \
  --coders "kimi-k2-6,glm-4-7,qwen3-6-35b-a3b" \
  --out "$REC/posture_collapsed/consensus.jsonl"
```

### Layer B promotion gate

For every component:

- each coder output covers every manifest `layered_id` exactly once;
- no failed/missing successful records remain;
- consensus count equals manifest count;
- `consensus.qa.md` reports zero missing coder records;
- every consensus record has at least two votes supporting its selected
  `collapsed_primary_label`;
- every consensus record has at least two votes supporting its selected
  `value_holding`;
- no record contains the forbidden coder provenance.

If a sample has a three-way label split or otherwise lacks a two-coder
majority, stop and create a documented adjudication packet. Do not silently
accept the plurality selected by the current consensus script.

## Phase 5 — full recovery QA before integration

Create a machine-readable recovery QA report covering all eight components.
It must verify:

1. 6,000 manifest samples.
2. 18,000 successful Layer A coder records.
3. 6,000 Layer A consensus records.
4. 18,000 successful Layer B coder records.
5. 6,000 Layer B consensus records.
6. Exactly 47 affected models.
7. Zero references to `rule_based_values_probe_extract` anywhere in promoted
   recovery outputs.
8. Exact agreement between manifest and consensus ID sets for both layers.
9. No duplicate IDs within a component or across the eight recovery
   components.
10. All expected condition counts and source trace paths retained.

Write the report to:

```text
analysis/values-probe/model-coding/layered/recode_20260728/QA.md
```

Also compare distributions against the discarded deterministic outputs, but
use this only as a diagnostic. Large differences are not grounds for changing
the LLM results.

## Phase 6 — integrate without destroying evidence

Do not overwrite the historical phase directories. Update the eight
corresponding entries in:

```text
analysis/values-probe/final/scripts/assemble_final_values_probe.py
```

Keep each original manifest path, but point `layer_a_dir`,
`layer_a_consensus`, `posture_dir`, and `posture_consensus` at the matching
`recode_20260728/<component>/...` paths.

Leave the forbidden-coder guard intact.

Run:

```bash
python3 analysis/values-probe/final/scripts/assemble_final_values_probe.py
```

This must now succeed.

## Phase 7 — validate the rebuilt final dataset

Required checks:

- `manifest_valid.jsonl`: 22,666 records.
- `layer_a_consensus.jsonl`: 22,666 records.
- `posture_consensus.jsonl`: 22,666 records.
- 128 models and 189 cells, assuming no source corpus changes occurred during
  recovery.
- zero occurrences of `rule_based_values_probe_extract` in:

```text
analysis/values-probe/final/data/
```

- all final coder provenance belongs to the approved LLM coders;
- source-map counts sum correctly;
- reports exist for all models;
- assembler rerun is deterministic apart from timestamps or explicitly
  documented metadata;
- the invalid-data warning may be removed only after all checks pass.

Run a targeted regression comparison for previously LLM-coded models to ensure
their records and summaries did not change as a side effect.

## Phase 8 — produce the article handoff, but do not edit the article

Create:

```text
analysis/values-probe/CHATGPT_THAW_DISCLOSURE_NUMBERS_2026-07-28.md
```

The handoff must:

1. Define exactly which Layer B labels count as “disclosure.”
2. Report both useful alternatives:
   - strict ownership: `value_holding == owned`;
   - broad non-disowned posture:
     `value_holding in {owned, relocated_or_partial}`.
3. Use only `CTRL1`, `CTRL2`, `G1`, and `G2`.
4. Show numerator, denominator, and percentage for every plotted model.
5. Show per-condition and pooled values.
6. Identify cell pooling and model-release grouping explicitly.
7. Include the exact final-data Git commit or worktree provenance.
8. State that no regex complement is being presented as disclosure.

Do not choose between strict and broad disclosure silently. Daniel should make
that editorial choice after seeing both tables and representative samples.

## Completion criteria

The recovery is complete only when:

- all 47 affected models have approved three-LLM Layer A and Layer B coding;
- all consensus and QA gates pass;
- final assembly succeeds with the forbidden-coder guard enabled;
- final data contains no deterministic coder provenance;
- the current invalid-data warning is removed with an accompanying clean QA
  record;
- the article handoff contains reproducible LLM-derived numbers;
- a final summary lists changed files, commands run, unresolved caveats, and
  the exact provenance needed by the next blog-editing session.

## Important operational note

This repository already contains extensive uncommitted work, including the
phase-18 additions and generated final outputs. Review diffs narrowly and never
use broad cleanup or reset commands. Preserve unrelated user work throughout.
