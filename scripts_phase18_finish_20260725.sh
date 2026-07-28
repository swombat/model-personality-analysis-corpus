#!/usr/bin/env bash
set -euo pipefail

ANALYSIS=/Users/danieltenner/dev/research/model-personality-analysis-corpus
CORPUS=/Users/danieltenner/dev/research/model-personality-corpus-v2
COLLECTION_LOGDIR="$CORPUS/logs/collection-2026-07-25-opus5-openai-reasoning"
COLLECTION_PID_FILE="$COLLECTION_LOGDIR/runner.pid"
MANIFEST=collection-manifest-2026-07-25-opus5-openai-reasoning.json
PHASE=analysis/values-probe/model-coding/layered/phase18_opus5_openai_reasoning_20260725
LOG="$ANALYSIS/logs/phase18_finish_20260725.log"

exec >>"$LOG" 2>&1

stamp() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$*"
}

source_keys() {
  set +u
  # shellcheck disable=SC1091
  source "$CORPUS/keys.env"
  set -u
}

qa_bad() {
  python3 - <<'PY'
import json
try:
    print(json.load(open(
        "analysis/freeflow/personality-eval-bv1/qa_summary.json"
    )).get("qa_bad_count", 999999))
except Exception:
    print(999999)
PY
}

assert_collection_complete() {
  python3 - <<'PY'
import json
from pathlib import Path

path = Path(
    "/Users/danieltenner/dev/research/model-personality-corpus-v2/"
    "logs/collection-2026-07-25-opus5-openai-reasoning/state.json"
)
state = json.loads(path.read_text())
expected = {
    "opus-5-direct",
    "opus-5-or-pin-anthropic",
    "o1-direct",
    "o3-direct",
    "o3-mini-direct",
    "o4-mini-direct",
}
problems = {}
for label in sorted(expected):
    entry = state.get("models", {}).get(label, {})
    for probe, target in (("freeflow", 125), ("values", 120)):
        record = entry.get(probe, {})
        if record.get("status") != "complete" or record.get("valid") != target:
            problems[f"{label}:{probe}"] = record
if problems:
    raise SystemExit("collection incomplete: " + json.dumps(problems, indent=2))
print("collection complete: 6 routes, 750 freeflow and 720 values samples")
PY
}

stamp "phase18 continuation starting"
source_keys

if [[ -f "$COLLECTION_PID_FILE" ]]; then
  collection_pid=$(cat "$COLLECTION_PID_FILE")
  while kill -0 "$collection_pid" 2>/dev/null; do
    stamp "waiting for corpus collector pid $collection_pid"
    sleep 300
  done
fi

# Reinvoke once with top-up semantics. Complete files are skipped, while any
# transiently failed or interrupted samples are repaired.
stamp "running final corpus top-up pass"
cd "$CORPUS"
python3 -u scripts/run_manifest_collection.py "$MANIFEST" \
  --state "$COLLECTION_LOGDIR/state.json" \
  --log-dir "$COLLECTION_LOGDIR" \
  --smoke-dir "$COLLECTION_LOGDIR/smoke" \
  --max-topup-rounds 5

assert_collection_complete

stamp "regenerating corpus inventory and freeflow scores"
python3 scripts/corpus_summary.py
python3 scripts/run_analysis.py

stamp "starting analysis-corpus BV1 point update"
cd "$ANALYSIS"
python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py \
  --rerun-failed-only --concurrency 20
python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py --qa-only

for _ in 1 2 3 4 5 6; do
  bad=$(qa_bad)
  stamp "BV1 qa_bad=$bad"
  [[ "$bad" == "0" ]] && break
  python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py \
    --rerun-failed-only --concurrency 12
  python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py --qa-only
done

bad=$(qa_bad)
if [[ "$bad" != "0" ]]; then
  stamp "BV1 still has qa_bad=$bad; stopping before aggregation"
  exit 1
fi

stamp "generating aggregate packets and missing cell aggregates"
python3 internal/scripts/analysis-scripts/generate_personality_aggregate_packets.py
PERSONALITY_CELL_AGG_MODEL="${PERSONALITY_CELL_AGG_MODEL:-gpt-5.4}" \
PERSONALITY_CELL_AGG_CONCURRENCY="${PERSONALITY_CELL_AGG_CONCURRENCY:-4}" \
  python3 internal/scripts/analysis-scripts/run_personality_cell_aggregates.py \
    --concurrency "${PERSONALITY_CELL_AGG_CONCURRENCY:-4}"

stamp "building route comparisons, cards, and profiles"
PERSONALITY_ROUTE_MODEL="${PERSONALITY_ROUTE_MODEL:-gpt-5.4}" \
PERSONALITY_ROUTE_CONCURRENCY="${PERSONALITY_ROUTE_CONCURRENCY:-4}" \
  python3 internal/scripts/analysis-scripts/analyze_model_cell_difference.py
python3 internal/scripts/analysis-scripts/build_personality_model_cards.py
python3 internal/scripts/analysis-scripts/build_personality_model_profiles.py

stamp "building and assembling phase18 values data"
python3 "$PHASE/build_phase18.py"
python3 analysis/values-probe/final/scripts/assemble_final_values_probe.py

stamp "regenerating website data and verifying the static build"
python3 website/scripts/generate_data.py
(cd website && npm run build)

stamp "phase18 continuation complete"
