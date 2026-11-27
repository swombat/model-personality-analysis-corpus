# Original Gemma 2B IT — local analysis import

Prepared on `ad31746c8a839c30586abca8cce973814c61ea1b`, verified equal to
local `origin/main`, following Qwen import `0d2a9fb54`. This is the original
`google/gemma-2b-it`, not Gemma 2 2B. Analysis-only preparation for publication;
no release or website generation was performed.

## Imported paths

- `analysis/freeflow/personality-aggregates/gemma-2b-it-colab-vllm-bf16-r96988410/`
- `analysis/freeflow/personality-model-cards/cards/gemma-2b-it.md`
- `analysis/freeflow/personality-model-profiles/profiles/gemma-2b-it.md` and its index entry
- `analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-20260929/outputs/gemma-2b-it-colab-vllm-bf16-r96988410/` (124)
- Corresponding `bv1-luna-v1-targeted-20261016` output directory (`SHORT_17` only)
- `analysis/values-probe/model-coding/layered/capture_gemma2_final_20261127/`
- `analysis/values-probe/final/reports/gemma-2b-it.md`
- Shared final JSONL files: append-only capture records; capture source and QA updates.

## Provenance

The terminal source is `finish_gemma2_one_synthesis_20261127` under
`~/work/colab-batch-queue/`. Its existing synthesis is copied, not rerun.
The exact corpus is 125 freeflow plus 120 values samples (245 total).
`validation.json` inventories copied bytes and shared-file changes and records
the preservation check across all earlier analysis files.

`OPEN_7` remains attributed to its original `bv1-luna-v1-20260929`
generation. The original `quote_sentence_boundary` failure and successful
zero-call v1.3 revalidation are separate records in
`bv1_bindings_luna_v1/OPEN_7.json` and
`bv1_bindings_v13_revalidation/OPEN_7.json` within the capture.
The validator is not a producing arm. `SHORT_17` retains its targeted producing
arm, binding and attempt responses.

`source-handoff/` retains terminal/offline/targeted records from all four
specified lanes. Values repair terminal hashes and charged transport receipts
are retained from `gemma2_values_through_report_20261127`; repaired G2_15/G2_16
sample artifacts and attempt histories remain in the capture. Historical
requests recorded in these receipts are not requests made by this import.
Absolute paths inside source artifacts deliberately retain their provenance.

Earlier shared JSONL bytes are exact prefixes; appended keys are checked
disjoint. No previous model report was regenerated. No queue database, source
lane, website file or release metadata was changed. No paid call, post, push
or other remote write was made.
