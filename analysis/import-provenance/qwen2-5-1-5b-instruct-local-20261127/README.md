# Qwen2.5 1.5B Instruct — local analysis-only import

Base: `d7f311e0ce3159caf2fa484eb17a2d81acc22f3e`.
Source: `/home/agent/work/colab-batch-queue/qwen25_final_20261127/terminal.json`.

Following the preceding Qwen2 import, validation inventories byte-preserved
analysis, 125 canonical BV1 readings, 120 values sources and all 245 raw hashes.
Shared JSONL additions are append-only; earlier index entries remain unchanged.
The independent check records source/destination hashes and unchanged prior data.

History preserves original generation arms, failed QA, attempts, source bindings,
frozen validators, read-only job snapshots, 28 initial offline-short adoptions,
the eight-sample targeted scope, and seven targeted result entries (not seven
short-rule adoptions). Final canonical readings include 30 separately adopted
readings; receipt paths distinguish ordinary offline adoption from short-rule
adoption. Original arm outputs are not rewritten as successful revalidations.
Original and targeted phase attempts and all canonical receipt files are frozen.

**Adapter caveat:** the source used a task-local validation/path adapter, not a
mainline validator change. Inherited generation arms and separate offline
short-rule receipts remain intact. `history/qwen25_final_20261127/adapter-provenance.json`
and the preserved adapter/precedent scripts retain the exact evidence.
Absolute historical paths and intermediate failure statuses are intentional.

Run `q2_import.py`, then `complete_provenance.py` on a fresh base; stage analysis
(force-add inventoried artifacts ignored by repository rules), then run
`q2_check.py`. Imported whitespace is intentionally byte-preserved, including
Markdown hard breaks and source EOF blanks flagged by `git diff --check`.
No website generation/publication, model calls, remote
writes/posts, scheduler execution or delegation occurred. Local commit only.
