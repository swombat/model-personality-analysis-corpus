# Mistral 7B Instruct v0.3 — local analysis import

Based at `3d96b9656`, following the verified Qwen/Gemma analysis-only pattern.
Finalized inputs are the finish-lane config and terminal receipt under
`source-handoff/`. No analysis was regenerated.

Includes exactly 125 essay readings (123 original-arm, two targeted-arm),
120 values samples, existing aggregate, card, profile and values report.
`validation.json` inventories copied bytes, source/output bindings and
append-only shared JSONL. Existing profile-index and capture-source entries
are preserved.

## Targeted recovery is not four additional model calls

The two real targeted attempts are MID_5 and VARY_19, retained under the
capture phase's `freeflow_bv1_luna_v1_targeted/attempt_responses/`.
Their hashes match the independently retained `*-returned.json` receipts.
Producing-arm readings and provenance sidecars are preserved unchanged.

`unsent-recovery/state/` is the separate historical authorization/dispatch/
return/preservation ledger, copied from `state/mistral-unsent-recovery-20261127`.
Its authorization records the old budgets at 2/2 per essay. As documented in
`unsent-recovery/report.md`, those four earlier charged slots failed before
dispatch because the prompt file was absent. They are not real model attempt
receipts and must not be counted as such. The historical recovery performed
exactly two real calls, with provider generation IDs:

- MID_5: `gen-1795734149-lNY7mNfM7iOpEFKW2Oc6`
- VARY_19: `gen-1795734158-6WwnUe0R9qMB6Ainbd85`

The finish receipt's `model_requests: 1` is a historical finish-lane field,
not the total recovery call count and not a call made by this import.

No model requests, posts, website changes, remote writes or delegation occurred
during this import. Inherited Markdown whitespace is retained for byte fidelity.
