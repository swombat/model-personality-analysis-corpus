#!/usr/bin/env zsh
set -euo pipefail
cd /Users/danieltenner/dev/model-personality-analysis-corpus
if ! pgrep -f 'analysis/values-probe/model-coding/layered/phase5_full/monitor_phase5.py' >/dev/null; then
  nohup python3 analysis/values-probe/model-coding/layered/phase5_full/monitor_phase5.py >> analysis/values-probe/model-coding/layered/phase5_full/logs/monitor.log 2>&1 &
  echo $! > analysis/values-probe/model-coding/layered/phase5_full/logs/monitor.pid
fi
