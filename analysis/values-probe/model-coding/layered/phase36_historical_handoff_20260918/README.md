# Phase 36 — historical full-precision analysis handoff

This phase fills the missing 120-sample layered values analyses for **Yi-6B-Chat
and ChatGLM2-6B**, and repairs **GLM-4-9B-Chat-HF's** existing analysis/site linkage.
Their existing freeflow BV1 evaluations, profiles, cards, images, and editorial
summaries are retained.

The initial website audit missed GLM's existing phase22 records under
`glm-4-9b-chat`, so this phase unnecessarily recoded its 120 samples. Final
integration caught the duplicate physical cell. The redundant GLM run is
preserved here but **excluded from final datasets**; the existing phase22
records are retained with their model name normalized to `glm-4-9b-chat-hf`.
There are only **240 net new samples**, not 360.

## Frozen method

- Three independent approved LLM coders: Qwen 3.6 35B A3B, Kimi K2.6, GLM 4.7.
- Layer A: fixed stated-values/world-change-wishes codebooks and two-of-three
  topic consensus.
- Layer B: fixed collapsed posture taxonomy and two-of-three primary posture
  majority.
- At most one independent boundary-guided adjudication of initial three-way
  posture splits, preserving original votes. Any residual split is reported,
  not rerolled until agreement.
- No deterministic keyword replacement for semantic coding.

All 360 run-source traces are hashed in `manifest_phase36.jsonl`; resume checks
their exact bytes. `run.py` performs coding; `finish.py` checks coverage,
adjudicates once where needed, assembles final datasets, verifies prior rows,
and refreshes only these three website values views.

Schema QA also checks each topic key against the correct frozen list. Nineteen
first-pass coder records used out-of-list keys (mostly value keys in the wish
chain). `repair_taxonomy.py` preserves the originals and first makes a targeted
schema-correction call with the unchanged codebooks and an explicit validity
reminder. Eight records still used a value key in the wish chain; one final
schema retry shows only the active chain's frozen key list, with no third retry.
Only posture inputs whose consensus topic keys change are recomputed.
This is correction of invalid structured output, not a reroll of valid
disagreements. Exact repairs and changed inputs are recorded under
`taxonomy_repair/`.

## Scope and fidelity

`raw_audit.json` covers all eight historical cells the local queue had called
complete. Seven pass 125 freeflow + 120 values fidelity checks, and all seven
already have 125 valid BV1 evaluations:

Yi-6B, ChatGLM2, ChatGLM3, Mistral 7B v0.2, Qwen1.5 7B, Qwen2 7B, GLM-4 9B.
Five already had complete layered values analyses, including GLM under its
previous alias. Only Yi and ChatGLM2 require new final rows.

**Qwen2.5 7B is blocked:** 26 freeflow and 5 values outputs fail role-continuation
and/or replacement-character checks. The audit accepts only 99/125 freeflow and
115/120 values traces. Originals remain untouched and unpublished; no partial
cell is promoted as complete, and no raw recollection is performed here.

## Evidence

- `raw_audit.json`: exact file-level fidelity findings.
- `baseline-final-signatures.json`: original prior semantic hash multisets.
- `baseline-final-signatures-alias-aware.json`: signatures read from the
  original committed baseline, allowing only the explicit GLM model alias.
  Both retain duplicate multiplicity.
- `integration-check.json`: verifies all prior final records unchanged except
  for the GLM model alias, and exactly 240 additions in each of nine final files.
- `QA.json`: coverage and split counts after assembly.
- `unresolved_posture.json`: residual split records, if any.
- `posture_collapsed/before_adjudication/`: immutable first-pass votes, when
  adjudication is needed.

Initial failed coder records with error `'OPENROUTER_API_KEY'` document a local
credential-loading failure before any API call. The subsequent run used an
existing research credential, with no change to coder identity or methodology.
The shared Layer-A QA script's `empty raw_text records` counter refers to a
field absent from its parsed-record schema, not empty API responses; actual raw
responses live in `*.attempts.jsonl` and schema-repair receipts. Phase36's
`validate_coding.py` checks those separately.

Website refresh uses established generation functions but touches only the
three repaired values views. Raw sample bundles, freeflow map geometry, unrelated
models, and Lume's editorial contributions are deliberately left unchanged.
