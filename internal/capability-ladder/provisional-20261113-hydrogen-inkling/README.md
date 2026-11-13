# November 13 ladder additions

Bounded task, based on analysis `cf996888d80c4247ad05e94ddd8b1a46e9726263`.
Runbook: `model-personality-corpus-v2/docs/daily-mapping-runbook.md:211–226`.

## Results

- **Inkling 2 Small: 151.1/220**, theta 160.25; 10 measured, 12 fitted rungs.
  Only `currentModel` from <https://artificialanalysis.ai/models/inkling-2-small>
  was used. Its effort field is null: provider-default effort alignment is not
  established. AA release date is November 5, 2026.
- **Gemini 4 Hydrogen: explicitly unscored**, zero admissible measured rungs.
  Both <https://artificialanalysis.ai/models/gemini-4-hydrogen> (xhigh default)
  and <https://artificialanalysis.ai/models/gemini-4-hydrogen-high> returned HTTP
  200 with correct titles, but no `currentModel` in decoded, concatenated Next
  Flight payloads. Neither `initialModels` nor `currentRelease` was used.
  The task establishes High as Google's provider default; no xhigh substitution.
  Recheck when `currentModel` becomes available, or obtain an explicit separate
  extraction-policy decision. This does **not** mean AA has no benchmark data.

## Method and receipts

`update.py` fetches pages, extracts only `currentModel`, recovers the original
October 4 provisional method from `c85984e1^`'s ladder substrate, verifies Sol High
161.6 and MiMo 128.1 calibration fixtures, and writes entry/result files.
Run `python3 internal/capability-ladder/provisional-20261113-hydrogen-inkling/update.py`
from this worktree. It reconstructs the two edited tracked files from this
worktree's HEAD plus these additions; do not run it over unrelated local edits.

`fetch_receipts.json` records URLs, HTTP status, title, content hashes, byte
counts, and currentModel counts. Only Inkling's currentModel is saved: no
comparison-row benchmark cache is retained. `*_result.json` contains the raw
admissible rung fields, theta, fit and explanatory note; `*_entry.json` contains
the exact published ladder object.

Ten Inkling raw fields: AA-LCR .833333333333333; SciCode .523148148148148;
AutomationBench .45621320178972646; HLE .44114921223355;
Omniscience accuracy .33766666666666667; GDP-PDF .252;
MLCR .205555555555556; tau3 banking .404123711340206;
TerminalBench 2.1 .812734082397004; Briefcase rubric .502020202020202.
HLE chance correction is .048. New AA fields outside the fixed 22-rung
definition (e.g. HLE Diamond, TerminalBench 4.0) are not substituted.

## Validation

- Calibration assertions passed: Sol High 161.6, MiMo 128.1.
- Recovered slopes: 905 observations, RMS .003847193640806355.
- JSON semantic check: only the two requested model additions; existing models
  and top-level metadata unchanged. Inkling has exactly 22 rung rows, 10 measured.
- `git diff --check` passed. Tracked diff: aliases +2 lines, ladder +202 lines,
  no deletions or formatting churn.
- No website regeneration/build, commit, push, main-checkout edits, or delegation.
