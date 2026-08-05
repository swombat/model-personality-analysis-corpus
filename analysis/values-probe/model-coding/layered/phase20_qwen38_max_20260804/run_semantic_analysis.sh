#!/usr/bin/env bash
set -euo pipefail

ANALYSIS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
CORPUS="$ANALYSIS/../model-personality-corpus-v2"
LAYERED="$ANALYSIS/analysis/values-probe/model-coding/layered"
PHASE="$LAYERED/phase20_qwen38_max_20260804"
MANIFEST="$PHASE/manifest_phase20.jsonl"
LAYER_A="$PHASE/layer_a"
POSTURE="$PHASE/posture_collapsed"
LOG="$PHASE/run.log"
CODERS=(qwen3-6-35b-a3b kimi-k2-6 glm-4-7)

exec > >(tee -a "$LOG") 2>&1

stamp() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$*"
}

jsonl_unique_count() {
  python3 - "$1" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
ids = set()
if p.exists():
    for line in p.read_text().splitlines():
        if line.strip():
            ids.add(json.loads(line)["layered_id"])
print(len(ids))
PY
}

assert_collection() {
  python3 - "$CORPUS" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
label = "qwen3-8-max-or-pin-alibaba"
problems = {}
for probe, directory, target in [
    ("freeflow", root / "data/traces_freeflow" / f"freeflow_{label}", 125),
    ("values", root / "data/traces_values" / label, 120),
]:
    valid = 0
    for path in directory.glob("*.json"):
        try:
            valid += bool(json.loads(path.read_text()).get("result"))
        except Exception:
            pass
    if valid != target:
        problems[probe] = {"valid": valid, "target": target}
if problems:
    raise SystemExit("collection incomplete: " + json.dumps(problems, indent=2))
print("collection complete: 125 freeflow and 120 values samples")
PY
}

assert_coder_coverage() {
  local dir="$1"
  for coder in "${CODERS[@]}"; do
    local count
    count="$(jsonl_unique_count "$dir/$coder.jsonl")"
    [[ "$count" == "120" ]] || {
      echo "$coder coverage is $count/120 in $dir" >&2
      return 1
    }
  done
}

stamp "Phase 20 Qwen3.8 Max semantic analysis starting"
set +u
# shellcheck disable=SC1091
source "$CORPUS/keys.env"
set -u
assert_collection

stamp "Regenerating corpus inventory and canonical freeflow scores"
(cd "$CORPUS" && python3 scripts/corpus_summary.py && python3 scripts/run_analysis.py)

stamp "Running per-sample BV1 semantic freeflow evaluation"
(cd "$ANALYSIS" && python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py \
  --rerun-failed-only --concurrency 20)
for _ in 1 2 3 4 5; do
  (cd "$ANALYSIS" && python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py --qa-only)
  bad="$(
    cd "$ANALYSIS"
    python3 - <<'PY'
import json
print(json.load(open("analysis/freeflow/personality-eval-bv1/qa_summary.json"))["qa_bad_count"])
PY
  )"
  [[ "$bad" == "0" ]] && break
  stamp "BV1 QA has $bad bad outputs; retrying failed rows"
  (cd "$ANALYSIS" && python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py \
    --rerun-failed-only --concurrency 12)
done
[[ "$bad" == "0" ]] || {
  echo "BV1 QA still has $bad bad outputs" >&2
  exit 1
}

stamp "Building BV1 cell aggregates, model cards, and profiles"
(cd "$ANALYSIS" && \
  python3 internal/scripts/analysis-scripts/generate_personality_aggregate_packets.py && \
  PERSONALITY_CELL_AGG_MODEL="${PERSONALITY_CELL_AGG_MODEL:-gpt-5.4}" \
    python3 internal/scripts/analysis-scripts/run_personality_cell_aggregates.py \
      --concurrency "${PERSONALITY_CELL_AGG_CONCURRENCY:-4}" && \
  PERSONALITY_ROUTE_MODEL="${PERSONALITY_ROUTE_MODEL:-gpt-5.4}" \
    PERSONALITY_ROUTE_CONCURRENCY="${PERSONALITY_ROUTE_CONCURRENCY:-4}" \
    python3 internal/scripts/analysis-scripts/analyze_model_cell_difference.py && \
  python3 internal/scripts/analysis-scripts/build_personality_model_cards.py && \
  python3 internal/scripts/analysis-scripts/build_personality_model_profiles.py)

stamp "Building values manifest without deterministic classification"
(cd "$ANALYSIS" && python3 "$PHASE/build_manifest.py")

mkdir -p "$LAYER_A" "$POSTURE"
stamp "Running three independent Layer A semantic coders"
for coder in "${CODERS[@]}"; do
  (cd "$ANALYSIS" && python3 "$LAYERED/run_layer_a_coders.py" \
    --coder "$coder" --workers 6 --manifest "$MANIFEST" --outdir "$LAYER_A")
done
assert_coder_coverage "$LAYER_A"

stamp "Building two-of-three Layer A consensus"
(cd "$ANALYSIS" && python3 "$LAYERED/build_layer_a_consensus.py" \
  --manifest "$MANIFEST" --outdir "$LAYER_A" \
  --coders qwen3-6-35b-a3b,kimi-k2-6,glm-4-7)

stamp "Running three independent Layer B posture coders"
for coder in "${CODERS[@]}"; do
  (cd "$ANALYSIS" && python3 "$LAYERED/run_posture_coder_collapsed.py" \
    --coder "$coder" --manifest "$MANIFEST" \
    --consensus "$LAYER_A/consensus_300.jsonl" \
    --outdir "$POSTURE" --workers 8)
done
assert_coder_coverage "$POSTURE"

stamp "Building Layer B majority consensus"
(cd "$ANALYSIS" && python3 "$LAYERED/build_posture_collapsed_consensus.py" \
  --indir "$POSTURE" --manifest "$MANIFEST" \
  --out "$POSTURE/consensus.jsonl")

python3 - "$POSTURE/consensus.jsonl" "$POSTURE/adjudication_required.jsonl" <<'PY'
import json, sys
from pathlib import Path
source, out = map(Path, sys.argv[1:])
rows = [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
unresolved = [
    row for row in rows
    if row.get("collapsed_primary_label_support", 0) < 2
]
out.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in unresolved))
print(f"unresolved posture majorities: {len(unresolved)}")
PY

stamp "Phase 20 initial semantic analysis complete"
