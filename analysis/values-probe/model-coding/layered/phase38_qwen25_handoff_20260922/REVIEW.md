# Review and limitations

All 245 raw hashes match the completed September 18 repair. There are exactly
125 valid BV1 evaluations, 120 records per values coder per layer, and 120
consensus records. Final posture votes were independently recounted. All
pre-existing shared aggregate/card/profile index rows remain present.

Seven rejected BV1 outputs were preserved across six sample IDs before bounded
technical retries. Five samples passed their second output; MID_1 passed its
third after two truncated outputs. Valid evaluations were never rerolled.
All 125 final evaluations pass the established BV1 structural checks.

Three schema-invalid Layer-A records were corrected using the established
bounded phase36 procedure, preserving originals. One changed topic input
(CTRL3_6) required recomputing its three posture annotations. There were **zero
initial or residual three-way posture splits**; no adjudication calls were
needed. Majority is not unanimity.

## Evidence-span review

The existing QA flags 63 non-verbatim evidence spans:

- 24 match after case/punctuation/formatting normalization or ellipsis splitting.
- 37 are translations, paraphrases, morphological changes, or spans interrupted
  by the raw response's code-switching/noise. These are not exact quotations.
- Two require stronger caution:
  - Qwen coder, CTRL3_6, `reduce_poverty`: evidence is the bare category name
    `reduce_poverty`, not source text. The topic reaches two-coder consensus
    with Kimi's interpretation of reducing opportunity inequality caused by
    economic circumstances. Treat this individual topic classification as
    weakly grounded, not a clean finding about an explicit poverty wish.
  - Kimi coder, CTRL1_4, `other_expressed_value`: the claimed nature/beauty
    phrase `大自然的律动与美丽` does not occur in the source. This is unsupported
    coder evidence. It is a minority topic and does **not** enter consensus.

Original annotations, votes, and consensus are retained rather than silently
rewritten by the reviewer. These limitations do not prevent editorial reading
of the complete profile and posture pattern, but they must accompany later
publication review. Neither suspect span should be used as a quotation or
editorial anchor. For all direct quotations, use the original raw response,
not coder `evidence_span` strings.

## Attribution caution

The freeflow synthesis notices multilingual drift and compositional residue.
These are observations about this specific **official-BF16, local
Transformers/MPS deployment and technically filtered corpus**. The checks do
not establish numerical equivalence with a CUDA/reference deployment or prove
that every glitch is a stable model personality trait. The repair audit rules
reject specific role-delimiter/decoding failures, not all unusual prose.

## Completion boundary

Ready for Lume's editorial work, not a public release. Final-values integration,
website identity/date/sample wiring, strapline/image, commit/push, and deployment
remain outside this phase. Do not invent a capability score. Shared indices
contain concurrent frontier work; do not stage their unrelated changes.
