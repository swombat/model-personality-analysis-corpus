#!/usr/bin/env bash
set -euo pipefail
PHASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$PHASE/../../../../.." && pwd)"
CORPUS="$ROOT/../model-personality-corpus-v2"
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"
source "$CORPUS/scripts/source_sops_keys.sh"
# Bounded wait: do not analyze partial cells or silently proceed after collection failure.
python3 - "$CORPUS" <<'PY'
import json,sys,time
from pathlib import Path
p=Path(sys.argv[1])/'logs/2026-09-10-deepseek41-mercury25/state.json'
labels=['deepseek-v4-1-flash-or-pin-deepseek','mercury-2-5-or-pin-inception']
for _ in range(240):
 d=json.loads(p.read_text());rows=d.get('models',{})
 stages={k:rows.get(k,{}).get('stage','pending') for k in labels}
 if all(s=='complete' for s in stages.values()):break
 if any(s in {'blocked','partial'} for s in stages.values()):raise SystemExit(str(stages))
 time.sleep(30)
else:raise SystemExit('Collection did not complete within two hours')
print('Collection complete; checking raw final answers',flush=True)
PY
python3 "$PHASE/audit_raw.py" > "$PHASE/raw_audit.log"
python3 "$PHASE/run_freeflow_bv1.py" > "$PHASE/bv1.log" 2>&1 &
BV1=$!
bash "$PHASE/run_semantic_analysis.sh" > "$PHASE/semantic.log" 2>&1 &
SEMANTIC=$!
rc=0
wait "$BV1" || rc=1
wait "$SEMANTIC" || rc=1
exit "$rc"
