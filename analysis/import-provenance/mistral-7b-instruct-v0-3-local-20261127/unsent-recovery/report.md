# Mistral v0.3 unsent-request recovery — 2026-11-27

Completed exactly one real targeted evaluator request for each of MID_5 and
VARY_19. Both returned HTTP 200, OpenAI / `openai/gpt-6-luna`, and passed
unchanged targeted-arm QA, provenance and binding validation. No retries.

The four old charged slots (two per essay) had failed before sending anything:
the fork lacked `BV1_signal_plus_felt.md`. Restored its missing file from the
analysis worktree after checking the contract pin:
`485f11ef774e0ea4e9708c4728ac93c617c4d3c67ab2cc02715314f95dcfa16a`.
No config, spec, validator or old allowance was changed.

The operator explicitly confirmed a separate new dispatch ledger only for these
two previously unsent requests. Its authorization, durable pre-call dispatches,
returned evidence hashes, terminal result and preservation verification are in:
`state/mistral-unsent-recovery-20261127/`.
Execution used the standard `corpus-ops/with_keys.py` launcher with corpus-venv
Python and `mistral_unsent_recovery.py`; log: `mistral-unsent-recovery.log`.

Outputs, including provenance sidecars:

`remaining_recovery_colab-mistral-7b-instruct-v0-3/analysis/analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-targeted-20261016/outputs/mistral-7b-instruct-v0-3-colab-vllm-bf16-rc170c708/{MID_5,VARY_19}.md`

Full unchanged request/response and QA records are linked and hashed in each
`*-returned.json`. Provider generation IDs:

- MID_5: `gen-1795734149-lNY7mNfM7iOpEFKW2Oc6`
- VARY_19: `gen-1795734158-6WwnUe0R9qMB6Ainbd85`

Preservation check verified 5,216 pre-existing files across the original state
tree and recovery fork. Old budgets remain 2/2 per essay. Original and fork
SQLite job states were deliberately left untouched: these are validated
recovery artifacts, not a resumed DAG or a claim of finalized queue jobs.
No downstream execution, publication or room posts.
