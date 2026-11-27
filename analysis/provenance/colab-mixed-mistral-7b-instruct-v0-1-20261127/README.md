# Mistral 7B Instruct v0.1 — analysis-only import

This import contains 125 reconciled freeflow readings, their aggregate packet,
model personality profile/card, and the completed 120-response layered values
release candidate. It does not publish a website model page or modify a map.

## Capture provenance

Official `mistralai/Mistral-7B-Instruct-v0.1` revision
`b1e7b9fc50d01ccbe4a30510386aba6f6adb1806`, bfloat16, vLLM on Google Colab.
All 125 freeflow responses used **Google Colab 1x NVIDIA L4**.
All 120 values responses used **Google Colab 1x NVIDIA RTX PRO 6000 Blackwell
Server Edition**. Do not apply the config's historical top-level L4 deployment
summary to values: exact per-sample deployments and hashes are retained in
`source/config.json` and original raw trace JSON under `raw/`.

Runtime metadata is retained verbatim: vllm==0.34.0; transformers==5.22.2;
tokenizers==0.23.3; torch==2.14.0+cu130. Local endpoint metadata describes capture,
not a public hosted endpoint.

## Evaluation provenance

The reconciled population contains 98 original validated readings, 3 offline
saved-response revalidations, and 24 targeted v1.3 validated replacements.
Each `readings/<sample>/binding.json` retains evaluator arm, original QA result,
source/output hashes, generation attempt and exact validator hashes.
Generation attempts are archived alongside bindings. Targeted replacements are
stored separately from the original evaluator arm, not relabelled as originals.
The three offline saved revalidations are OPEN_21, VARY_5 and VARY_23.
Validator and method source snapshots are evidence, not replacements for the
repository's public evaluation implementations.

The exact layered values release candidate includes the three coder streams,
layer-A and posture consensuses, manifest, source map, model summary, QA and
report. Original evaluation procedures and model metadata accompany the import;
no freeflow evaluator inference is used to relabel the values method.

The final aggregate/profile/card and combined-analysis bytes are verified against
the successor terminal receipts. All 125 synthesis-input reading hashes are
verified. `job-receipts.json` retains the 1,404 verified completed-job receipts.
The old scheduler's `queue-ready` remains blocked; this is historical scheduler
state, not a missing reading or a claim that its original readiness gate ran.
The explicit successor terminal records the completed analysis.

`artifact-manifest.json` lists each installed artifact's original source,
SHA-256, size and release destination. This retains original source paths as
provenance, not as a claim those paths are portable. Artifact bytes are copied
without textual provenance rewrites.

Based on public default branch `main` at
`015095f9ee1ae9f26e2d8d3764f7e5569c983f74`; the public repository has no
`master` branch. All prior model records and artifacts are preserved, apart from
appending this model to the two analysis indices. Local commit only.
