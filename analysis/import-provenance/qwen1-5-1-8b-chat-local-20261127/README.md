# Qwen1.5 1.8B Chat — local analysis import

Base: v1.4.63 release commit `cf7fb674b` (tag not present in this local
repository). Follows the Mistral analysis-only import; no regeneration.

The exact finalized lane is `qwen18_values_authorized_20261127b`.
Its historical terminal receipt, config, synthesis response and transport,
coding, adjudication, STOPPED and subsequent offline-finish proofs are retained
in `history/`. Historical request counts describe earlier work, not this import.

All 125 canonical essay readings and 120 canonical values samples are included.
The full capture phase preserves original and targeted attempt responses,
coding layers, consensus, adjudication, bindings and release-candidate data.
Producing-arm outputs remain unchanged. `validation.json` maps canonical
readings and verifies all 245 raw-source hashes against the frozen raw corpus
(raw release v1.2.65 is separate), copied bytes and append-only final data.

## Generation is not offline revalidation

MID_15 was generated under the original Luna arm; OPEN_8 was generated under
the targeted arm. Both were separately adopted through offline v1.3
revalidation. Their canonical adopted readings are in `canonical-readings/`;
original attempts, selection/revalidation evidence and validator source are
preserved in `history/` and the capture phase's
`bv1_bindings_v13_revalidation/`. This is not a claim that the producing
arms originally passed those readings. In particular OPEN_8's original
failure was `quote_sentence_boundary`; the binding explicitly records
`original_qa_pass: false` and the independent v1.3 result.

Prior failed/setup/stopped lanes and logs are retained, including the original
continuation, four-targeted recovery, downstream preflight, first authorized
lane and final authorized lane. `history/original-state/` also preserves the
original scheduler's models, attempts, failure logs and outbox.
`jobs-snapshot.json` exports historical job
states/attempts/reasons without live SQLite WAL files. Absolute paths in copied
historical receipts deliberately remain original, not rewritten to imply
new generation. The import script is retained beside this document.

Current shared profile/capture indexes and final JSONL preserve every existing
entry and append only this model's finalized rows. No website, model calls,
remote writes/posts or delegation occurred. Checks are local and offline.
