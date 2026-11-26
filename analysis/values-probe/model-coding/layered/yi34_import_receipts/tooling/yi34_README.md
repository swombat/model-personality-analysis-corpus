# Original Yi 34B Chat local analysis import (2026-11-26)

Owner retains site files and publication. No network, inference, raw writes,
push, or additional agents. Fresh origin/main base:
`4410d5e467b792ca0344b4b0d45fb1d8d3aa1fd2`.
Worktree: `~/work/colab-yi34-site`, branch `mira/colab-yi34-analysis`.

Run from `~/work/colab-release-tools`:

```
python3 -B -m unittest yi34_test -v
python3 -B yi34_import.py > yi34_dry_run.json
python3 -B yi34_apply.py > yi34_apply.log
```

The importer pins the finish spec `52557b93...` and recovery fork `a033e33f...`
(full pins in source). It checks all ten finish receipts, all successful fork
receipts and byte-identical adopted copies, 245 raw hashes, exact mixed-arm
manifest/bindings, and targeted request/response/sidecar provenance. Exactly
LONG_4, MID_2, MID_9, MID_14, OPEN_15 use the targeted sentence-evidence arm;
120 essays remain original v1. Original and targeted attempts retain their
distinct trees and names.

G3_25 Kimi layer A was separately verified at attempt 1. Yi's actual recovery
contract is `verified.json` plus a one-request `dispatch.json`, not Gemma's
`authorization.json`. The verifier checks the original held-row digest and
hold hash, original config/spec binding, isolated output hash, finish-adopted
output hash, and equal finish recovery receipt. The original blocked jobs are
not relabeled done. Coherent original/fork/finish exports replace live sqlite
copies. Entire final, retry, and fork phase trees are included.

Apply reuses Gemma's analysis-only lane with model-specific substitutions.
The website update block is removed in memory. Fixed base, clean analysis,
empty index, and exact independently prepared sibling raw candidate hashes
are required. Every previous final-data JSONL **multiset**, including duplicate
rows, must survive. Only explicit analysis paths are staged. Apply does not
commit; the local analysis commit is a separate reviewed step.
The Yi adapter explicitly includes its new final report: ordinary `git diff`
does not inventory untracked files.

Cross-artifact review: aggregate/card/profile agree on earnest reflective-writer
prose, formulaic ocean/nature/blank-page imagery and reassurance, contrasted with
open-condition AI role boundaries. Profile counts total 125: 66 expressive,
19 generic essays, 9 low-signal, 6 fiction, 25 role-boundary. Values report has
120 samples: 117 recited-not-owned, 2 owned (CTRL3), 1 relocated/partial (G3).
CTRL1/CTRL2 are each 10/10 disowned service-frame. One initial posture split
received independent adjudication, zero residual splits. This is provenance
and consistency review, not an independent reevaluation of every trace.

Imported immutable Markdown can contain trailing whitespace/hard breaks.
Do not normalize receipt-bearing bytes to satisfy `git diff --check`.
Tool sources, dry-run/applied reports and test logs are retained locally and
copied into the analysis receipt directory for audit (paths assume the original
local tools/queue layout).
