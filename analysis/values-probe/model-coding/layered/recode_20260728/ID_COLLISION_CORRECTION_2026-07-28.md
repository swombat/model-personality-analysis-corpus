# Recovery manifest ID-collision correction — 2026-07-28

During the LLM recoding recovery, the preflight uniqueness check found that two
source manifests did not have one unique `layered_id` per trace:

| component | rows | unique old IDs | duplicate-ID excess |
|---|---:|---:|---:|
| `phase17_haiku_20260722` | 360 | 240 | 120 |
| `phase18_opus5_openai_reasoning_20260725` | 720 | 600 | 120 |

In both components, multiple cells for the same model reused IDs based only on
model, condition, and sample number. For example, the direct and pinned
OpenRouter Haiku 4.5 cells both used IDs such as
`P17_haiku-4-5_CTRL1_001`.

This is unsafe for the resumable LLM runners, which use `layered_id` as their
completion key. Running against the original manifests would silently skip one
of the colliding traces.

## Recovery-only correction

The historical manifests and deterministic outputs remain untouched. The
recovery uses:

- `phase17_haiku_20260722/manifest_recovery_unique_ids.jsonl`
- `phase18_opus5_openai_reasoning_20260725/manifest_recovery_unique_ids.jsonl`

under `recode_20260728/`.

Each recovery ID includes the source cell and sample ID. The old ID is retained
as `original_layered_id`, and the original `trace_path`, `cell`, `sample_id`,
model, condition, prompt, and response are unchanged.

The final assembler must use these two corrected recovery manifests together
with their matching recovery consensus outputs. Comparisons with the
pre-recovery dataset must join samples by source component, cell, sample ID,
and trace path rather than by the non-unique historical `layered_id`.
