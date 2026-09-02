#!/usr/bin/env bash
set -euo pipefail

PHASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORPUS="/Users/danieltenner/dev/research/model-personality-corpus-v2"
LOG="$PHASE/logs/unattended-pipeline.log"
LOCK="$PHASE/.unattended-pipeline.lock"
mkdir -p "$PHASE/logs"

if ! mkdir "$LOCK" 2>/dev/null; then
  echo "Another Phase 29 unattended pipeline holds the lock." >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

source "$CORPUS/scripts/source_sops_keys.sh"
cd "$PHASE"

log() {
  printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$LOG"
}

valid_count() {
  local label="$1"
  python3 - "$CORPUS/data/traces_values/$label" <<'PY'
import json
import sys
from pathlib import Path
p = Path(sys.argv[1])
print(sum(
    1 for f in p.glob("*.json")
    if (json.loads(f.read_text()).get("result") or "").strip()
))
PY
}

political_valid_count() {
  local cell="$1"
  python3 - "$PHASE/political_probe/raw/$cell" <<'PY'
import json
import sys
from pathlib import Path
p = Path(sys.argv[1])
print(sum(
    1 for f in p.glob("*.json")
    if (json.loads(f.read_text()).get("result") or "").strip()
))
PY
}

deepinfra_available() {
  python3 - <<'PY'
import os
import httpx
body = {
    "model": "z-ai/glm-5.3-flash",
    "messages": [{"role": "user", "content": "Reply with: ready"}],
    "max_tokens": 32,
    "provider": {"only": ["DeepInfra"], "allow_fallbacks": False},
}
try:
    r = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json=body,
        timeout=60,
    )
    raise SystemExit(0 if r.status_code == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

wait_for_deepinfra() {
  until deepinfra_available; do
    log "DeepInfra unavailable; retrying in 5 minutes."
    sleep 300
  done
  log "DeepInfra available."
}

label_for_cell() {
  case "$1" in
    P0) echo "glm-5-3-flash-or-pin-deepinfra-p0-20260827" ;;
    P1) echo "glm-5-3-flash-or-pin-deepinfra-p1-20260827" ;;
    P2) echo "glm-5-3-flash-or-pin-deepinfra-p2-20260827" ;;
    *) return 1 ;;
  esac
}

for cell in P0 P1 P2; do
  label="$(label_for_cell "$cell")"
  while [[ "$(valid_count "$label")" -lt 120 ]]; do
    count="$(valid_count "$label")"
    log "$cell has $count/120 valid responses."
    wait_for_deepinfra
    PHASE29_MAX_ATTEMPTS=6 PHASE29_RETRY_CAP=20 \
      python3 run_collection.py --part values --cells "$cell" --workers 3 \
      >>"$LOG" 2>&1 || true
  done
  log "$cell complete."
done

while [[ "$(political_valid_count deepinfra_raw)" -lt 10 ]] \
   || [[ "$(political_valid_count deepinfra_p2)" -lt 10 ]]; do
  wait_for_deepinfra
  PHASE29_MAX_ATTEMPTS=6 PHASE29_RETRY_CAP=20 \
    python3 run_collection.py --part politics \
      --political-cells deepinfra_raw deepinfra_p2 --workers 3 \
      >>"$LOG" 2>&1 || true
done
log "DeepInfra political cells complete."

python3 build_manifest.py >>"$LOG" 2>&1
log "Manifest complete; starting semantic coding."
while [[ -f "$PHASE/.coding-p0-p1.pid" ]]; do
  partial_pid="$(cat "$PHASE/.coding-p0-p1.pid" 2>/dev/null || true)"
  if [[ -n "$partial_pid" ]] && kill -0 "$partial_pid" 2>/dev/null; then
    log "P0/P1 coding is still running; waiting before the full top-up."
    sleep 60
  else
    rm -f "$PHASE/.coding-p0-p1.pid"
  fi
done
bash run_coding.sh >>"$LOG" 2>&1
python3 analyze_posture.py >>"$LOG" 2>&1
touch AUTOMATION_COMPLETE
log "Automated Phase 29 collection, coding, and posture analysis complete."
