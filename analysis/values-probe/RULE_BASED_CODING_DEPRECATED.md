# Rule-based values-probe coding is deprecated and forbidden

**Effective:** 2026-07-28

`rule_based_values_probe_extract` must not be used as a Layer A coder, Layer B
posture coder, consensus source, disclosure classifier, or source of final
values-probe corpus results.

The regex/rule extractor in
`internal/scripts/analysis-scripts/values_probe_extract.py` is retained only
for historical reproduction and exploratory diagnostics. Its output is not
model judgment and is not interchangeable with the approved three-LLM coding
and consensus pipeline.

The final assembler now fails closed if any consensus record contains this
coder provenance. Historical point-release build scripts that generated such
records are disabled and fail loudly when executed.

Existing rule-coded records are invalid pending replacement with approved LLM
coding. See `RULE_BASED_CODING_AUDIT_2026-07-28.md`.
