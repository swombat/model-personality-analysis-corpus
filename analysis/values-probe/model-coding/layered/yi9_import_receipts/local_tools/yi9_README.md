# Yi 1.5 9B analysis-only import

Local worktree `~/work/colab-yi9-site`, branch `mira/colab-yi9-analysis`,
base `0736983b404300033ce20858c64870b17f68d269` (current local origin/main).
No push, tag, commit, raw writes or website edits.

Run from this directory:

```
python3 -B -m unittest yi9_test -v
python3 -B yi9_import.py > yi9_dry_run.json
python3 -B yi9_apply.py > yi9_apply.log
```

Adapters reuse the Yi34 mixed-arm verifier and Gemma analysis-only apply lane.
Finish has six completed jobs; the recovery fork retains its blocked/pending
jobs. Three targeted essays (LONG_9, LONG_25, OPEN_18) retain distinct attempts,
bindings, sidecars and mixed-arm manifest entries. Other 122 remain original v1.

The isolated values recovery is **posture G1_20 Kimi**, not layer A:
one captured request, production validation true, publication authorization false.
Verified receipt equals the finish-adopted receipt; isolated and adopted bytes
match. Parent hold, original rows/spec/config, prior failed-lane hashes,
authorization, request-consumed and returned-answer evidence are retained.
Live sqlite files are not copied; coherent task snapshots are exported.

All 245 raw files are hash-checked against adopted config and sibling raw
candidate. Raw is data only: no raw scripts/config are loaded. Values trace paths
must belong to the already verified inventory; traversal/symlinks are rejected.
Integration runs trusted analysis scripts with website update block removed.
Every prior final-data JSONL multiset (including duplicates) survives, and prior
non-Yi9 profiles remain byte-identical. Existing imported-file conflicts abort.
Only explicit analysis paths are staged, including the otherwise-untracked report.

Immutable imported Markdown may have trailing whitespace: do not normalize
receipt-bearing bytes for diff-check. Test output can show inherited sqlite
ResourceWarnings; tests themselves must pass. Applied report and tests record
the exact scope. No publication authority is implied by readiness.
