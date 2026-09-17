#!/usr/bin/env bash
set -euo pipefail
PHASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$PHASE/../../../../.." && pwd)"
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"
source "$ROOT/../model-personality-corpus-v2/scripts/source_sops_keys.sh"
python3 -u - "$PHASE" <<'PY'
import sys,time
from pathlib import Path
p=Path(sys.argv[1])
for _ in range(480):
    s=(p/'first-pass.log').read_text()
    if 'ANALYSIS_FIRST_PASS_EXIT=' in s:break
    if 'Traceback (most recent call last)' in s:raise SystemExit('First pass stopped; inspect first-pass.log')
    time.sleep(30)
else:raise SystemExit('First-pass wait timed out after 4 hours')
PY
python3 -u "$PHASE/finish_analysis.py"
