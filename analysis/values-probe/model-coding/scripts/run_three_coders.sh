#!/usr/bin/env bash
set -eo pipefail
cd /Users/danieltenner/dev/model-personality-analysis-corpus
set -a
source /Users/danieltenner/dev/model-personality-corpus-v2/keys.env
set +a
mkdir -p analysis/values-probe/model-coding/logs
for coder in deepseek-v4-pro kimi-k2-6 glm-4-7; do
  nohup /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 analysis/values-probe/model-coding/scripts/run_pilot_coder.py "$coder" --workers 5 \
    > "analysis/values-probe/model-coding/logs/${coder}.log" 2>&1 &
  echo "$!" > "analysis/values-probe/model-coding/logs/${coder}.pid"
done
