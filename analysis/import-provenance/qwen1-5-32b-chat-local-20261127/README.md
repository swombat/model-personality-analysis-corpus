# Qwen1.5 32B Chat — local-only analysis import

Base: `7b389986fffa3fe59b6c4436b7267c1adc4e9e69`, following its validated
Qwen1.5 1.8B import. Source: `qwen32_values_authorized_20261127/terminal.json`
under `/home/agent/work/colab-batch-queue`.

`validation.json` inventories byte-preserved files with source paths and SHA-256,
all 125 BV1 canonical readings, all 125+120 canonical raw-source hashes, and
append-only shared-data receipts. `check-receipt.json` records independent checks.
`q1532_import.py` and `q1532_check.py` are offline-only reproduction/check scripts.

The seven separate original-arm readings are not relabelled as new generations:
LONG_2's earlier offline adoption and the six additional offline reads
(MID_7, MID_9, MID_19, MID_23, LONG_5, LONG_21) retain their original attempts,
failed original QA, frozen validator provenance and separate canonical readings.
The six adoption bindings remain in their historical terminal receipt; LONG_2's
binding remains in the final phase. MID_2, MID_22 and SHORT_14 retain their
targeted-arm passes, bindings and attempts. Original-arm outputs and sidecars
remain distinct from these canonical selections.

History preserves original state, exhausted scoped recovery, continuation,
offline-six, three-targeted and values lanes, including stopped/intermediate
receipts, transport charge/response evidence, synthesis response, authorization,
validator source, logs and read-only SQLite job snapshots. Historical absolute
paths and intermediate failure states are deliberately not rewritten.

All earlier records are unchanged; only the new model is appended to shared
JSONL files and indices. No website change, publication, remote write, provider
call, scheduler run or delegation occurred during this import.
