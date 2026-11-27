# Qwen2 1.5B Instruct — local analysis-only import

Base: `b264fb61c` (requested v1.4.65, existing 209-model site baseline).
Source: `/home/agent/work/colab-batch-queue/qwen2_final_20261127b/terminal.json`.

`validation.json` inventories byte-preserved source files and SHA-256 receipts,
all 125 canonical BV1 readings and all 125+120 raw-source hashes.
`check-receipt.json` independently checks bytes, append-only shared data,
unchanged earlier records and untouched website. Reproduction/check scripts
are included; they load no provider modules.

The offline-short lane's 14 adoptions remain separate from original-arm
generations, with original failed QA, attempts, frozen validators and source
bindings preserved. The targeted scope was eight: four normal passes and four
separately adopted short-rule readings (MID_14, MID_3, OPEN_9, VARY_15).
Normal targeted passes are LONG_15, MID_11, MID_24 and MID_9.
Earlier original/recovery/continuation attempts, exhausted limits and failed
intermediate lanes remain historical facts, not overwritten successes.
Final offline validation lists 19 separately handled readings, including the
earlier LONG_1 adoption; these are not 19 new generations.

History retains original state, read-only job snapshots, offline14,
targeted-eight, failed final lanes and final integration receipts, including
pre-dispatch path repair and synthesis transport evidence. Absolute historical
paths and intermediate failure statuses are intentionally unchanged.

Only this model is appended to shared JSONL files and indices. No website
generation, publication, paid calls, scheduler execution, delegation, posts or
remote writes occurred in this import. The commit is local only.
