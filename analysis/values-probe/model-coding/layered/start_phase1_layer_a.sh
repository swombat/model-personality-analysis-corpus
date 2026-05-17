#!/usr/bin/env bash
set -eo pipefail
cd /Users/danieltenner/dev/model-personality-analysis-corpus
set -a
source /Users/danieltenner/dev/model-personality-corpus-v2/keys.env >/dev/null 2>&1 || true
set +a
mkdir -p analysis/values-probe/model-coding/layered/logs
for coder in deepseek-v4-pro kimi-k2-6 glm-4-7; do
  nohup /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -u analysis/values-probe/model-coding/layered/run_layer_a_coders.py --coder "$coder" --workers 4 \
    > "analysis/values-probe/model-coding/layered/logs/${coder}.layer_a.log" 2>&1 &
  echo "$!" > "analysis/values-probe/model-coding/layered/logs/${coder}.layer_a.pid"
done
