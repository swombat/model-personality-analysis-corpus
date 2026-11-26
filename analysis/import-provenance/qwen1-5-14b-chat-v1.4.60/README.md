# Qwen1.5 14B Chat — local analysis import for v1.4.60

Prepared from `~/work/colab-batch-queue/finish_qwen14_v13_20261127c`,
mirroring the Yi v1.4.59 analysis import (`940f0176d`), on baseline
`e0050c97b4c24c9b0ec3e409573e09e137d2cf20`.
This is an analysis-only preparation, not a release or publication.

## Imported paths

- `analysis/freeflow/personality-aggregates/qwen1-5-14b-chat-colab-vllm-bf16-r9492b228/`
- `analysis/freeflow/personality-model-cards/cards/qwen1-5-14b-chat.md`
- `analysis/freeflow/personality-model-profiles/profiles/qwen1-5-14b-chat.md`
- `analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-20260929/outputs/qwen1-5-14b-chat-colab-vllm-bf16-r9492b228/` (124 samples)
- `analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-targeted-20261016/outputs/qwen1-5-14b-chat-colab-vllm-bf16-r9492b228/` (`LONG_22`)
- `analysis/values-probe/model-coding/layered/capture_qwen14_offline_20261127/`
- `analysis/values-probe/final/reports/qwen1-5-14b-chat.md`
- `analysis/values-probe/final/data/*.jsonl`: append only this capture's records.
- `analysis/values-probe/final/capture_sources.json`: append this capture.
- `analysis/values-probe/final/data/QA.md`: update counts and add import note.

## Provenance and checks

`validation.json` inventories every copied path and SHA-256, all changed existing
files, and the earlier/new JSONL row counts and hashes. All 75,229 earlier
analysis files were hashed: 75,216 remain unchanged; only the 11 shared JSONL
files, capture source list, and QA summary changed. Earlier JSONL bytes are
preserved as exact prefixes, existing keys cannot overlap new keys, and every
earlier capture source remains present. No existing model report was regenerated.

All 125 BV1 source and output hashes matched the verified handoff. Original
producing arms are preserved, including the targeted `LONG_22`. `LONG_12`
remains in `bv1-luna-v1-20260929`; it is **not** attributed to the v1.3 validator.
Its original `quote_sentence_boundary` QA failure and separate successful
zero-call revalidation are explicitly retained in:

- `analysis/values-probe/model-coding/layered/capture_qwen14_offline_20261127/bv1_bindings_luna_v1/LONG_12.json`
- `analysis/values-probe/model-coding/layered/capture_qwen14_offline_20261127/bv1_bindings_v13_revalidation/LONG_12.json`

The source lane's editorial hashes were verified before copying. Its readiness
records report 125 BV1 and 120 values samples. `source-handoff/` preserves the
offline-ready handoff, earlier editorial handoff, verification, adapter source,
and existing editorial response receipt. The earlier `held_before_dispatch`
and missing-helper messages are historical snapshots, superseded by the
offline-ready handoff, not new blockers. Absolute paths inside copied source
records deliberately retain their original provenance; they are not rewritten
as new generation claims.

No website files, release metadata, queue database, Git index, or source-lane
artifacts were edited. No model calls, publication, pushes, or posts were made.
