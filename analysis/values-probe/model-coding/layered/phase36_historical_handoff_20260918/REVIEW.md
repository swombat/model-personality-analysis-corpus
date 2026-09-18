# Handoff review — 2026-09-18

## Completion and preservation

- Seven accepted historical cells: 1,715 raw traces pass the declared structural
  fidelity checks; 875 existing BV1 evaluations pass output QA.
- Five pre-existing layered values cells match their current source response
  text (the existing GLM manifest strips outer whitespace).
- The run coded 360 samples × three coders × two layers, but only Yi and
  ChatGLM2's **240 samples** are new final records.
- Nineteen Layer-A records required schema repair. Eight needed the final
  active-chain-only key-list reminder. All original outputs are preserved.
- Eight changed consensus topic inputs were recoded for posture by all three
  coders. Final posture has **zero three-way splits**; no split adjudication was
  necessary. Taxonomy, identities, chain separation, and vote counts pass QA.
- Final integration caught existing GLM records under a different model alias.
  Its redundant phase36 reanalysis is excluded from final datasets. The
  phase22 votes are retained, with only `glm-4-9b-chat` normalized to
  `glm-4-9b-chat-hf` so the website can find them.
- All prior rows in nine final files remain semantically identical except for
  that alias, preserving duplicate multiplicity; each file adds 240 rows.

## Evidence-span caution

Across the full run (including the excluded GLM reanalysis), the exact-substring
check flags **82 coder evidence spans**. Sixty-three match
after accounting for case, markdown emphasis, and ellipsis-separated excerpts.
The remaining 19 were reviewed against the full source responses: they involve
small inflection/paraphrase changes, omitted list items, joined/split words, or
translation/omission of code-switched words. These are coder-generated evidence
annotations, **not guaranteed verbatim quotations**.

Examples include “preventing or de-escalating conflicts” for the source's
“prevent or de-escalate conflicts”, and translating `消除一些` into “eliminating
some”. The source traces retain their oddities unchanged. Semantic coder votes
are not manually rewritten based on this review.

Use the source trace when quoting a model. Website examples are extracted from
source responses by the established generator, not copied from these coder
evidence-span strings. `evidence-span-warnings.json` preserves all flags.

The raw fidelity audit checks stored-answer agreement, checkpoint metadata,
generation stop status, and known decoding/role artifacts. It does not certify
that an awkward, code-switched, or low-quality answer is fluent, and does not
exclude such answers merely for being awkward.

## Publication checks

`verify_handoff.py` checks all seven built pages, their 125/120 analyzed and
published counts, and exact preservation of unrelated generated model records.
The freeflow map and sample bundles are unchanged.

The existing map suite passes all eight tests. The pricing suite already failed
before the site refresh because it expects a `deepseek-v4-flash` entry absent
from current generated data. This unrelated baseline failure is not hidden or
repaired in this historical handoff.

## Remaining collection blocker

Qwen2.5 7B requires faithful recollection of 26 freeflow and five values traces
before paired-cell publication. No partial cell is promoted as complete.
