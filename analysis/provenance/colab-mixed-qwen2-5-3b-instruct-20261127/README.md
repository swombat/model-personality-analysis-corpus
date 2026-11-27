# Qwen2.5-3B Instruct — analysis-only import

Contains 125 reconciled freeflow readings, exact aggregate packet, personality
profile/card, combined analysis and the completed 120-response layered values
release candidate. No website model page, map update or new evaluation.

## Capture provenance

Official `Qwen/Qwen2.5-3B-Instruct` revision
`aa8e72537993ba99e69dfaafa59ed015b17504d1`, bfloat16, vLLM on Google Colab.
Freeflow: **124 NVIDIA RTX PRO 6000 Blackwell Server Edition + LONG_10 on
NVIDIA L4**. Values: **all 120 RTX PRO 6000 Blackwell Server Edition**.
Exact per-sample deployment metadata and hashes remain in `source/config.json`
and original raw traces under `raw/`. Do not generalize a top-level deployment
summary across this mixed capture.

Runtime: vllm==0.34.0; transformers==5.22.2; tokenizers==0.23.3;
torch==2.14.0+cu130. Local endpoints describe capture, not public services.

## Evaluation provenance

**109 original validated readings + 16 targeted v1.3 validated replacements;
zero offline saved-response adoptions.** Original saved answers were replayed
unchanged against pinned v1.3 and the bounded short-source rule. Each archived
binding retains source/output hashes, evaluator generation arm, original QA,
generation attempt and validator hashes. Original and targeted outputs are
stored under their distinct evaluator arms; no relabelling as originals.

Validator snapshots and exact method source are evidence, not replacements for
public evaluation implementations. The values release candidate preserves coder
streams, consensuses, manifest, source map, summary, QA and report without
misrepresenting values as a freeflow evaluation.

Terminal output receipts and all 125 synthesis-input hashes are checked.
`job-receipts.json` preserves completed-job receipt mappings; the historical
blocked queue-ready job is retained, not represented as newly executed.
`artifact-manifest.json` records every installed source path, destination,
SHA-256 and byte count. Source bytes, including original paths, are unchanged.

Based on public `main` at `015095f9ee1ae9f26e2d8d3764f7e5569c983f74`.
Only this model's analysis artifacts are added; the two analysis indices append
one record each. No prior model record is replaced. Local commit only.
