#!/usr/bin/env bash
set -euo pipefail

ANALYSIS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
CORPUS="$ANALYSIS/../model-personality-corpus-v2"
LAYERED="$ANALYSIS/analysis/values-probe/model-coding/layered"
PHASE="$LAYERED/phase23_qwen38_replicates_20260814"
MANIFEST="$PHASE/manifest_phase23.jsonl"
LAYER_A="$PHASE/layer_a"
POSTURE="$PHASE/posture_collapsed"
LOG="$PHASE/run.log"
CODERS=(qwen3-6-35b-a3b kimi-k2-6 glm-4-7)

exec > >(tee -a "$LOG") 2>&1

count_unique() {
  python3 - "$1" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
print(len({
    json.loads(line)["layered_id"]
    for line in p.read_text().splitlines()
    if line.strip()
}) if p.exists() else 0)
PY
}

assert_coder_coverage() {
  local dir="$1"
  for coder in "${CODERS[@]}"; do
    [[ "$(count_unique "$dir/$coder.jsonl")" == "240" ]] || {
      echo "$coder does not have 240 unique records in $dir" >&2
      return 1
    }
  done
}

set +u
# shellcheck disable=SC1091
source "$CORPUS/keys.env"
set -u

cd "$ANALYSIS"
python3 "$PHASE/build_manifest.py"
mkdir -p "$LAYER_A" "$POSTURE"

for coder in "${CODERS[@]}"; do
  python3 "$LAYERED/run_layer_a_coders.py" \
    --coder "$coder" --workers 6 --manifest "$MANIFEST" --outdir "$LAYER_A"
done
assert_coder_coverage "$LAYER_A"

python3 "$LAYERED/build_layer_a_consensus.py" \
  --manifest "$MANIFEST" --outdir "$LAYER_A" \
  --coders qwen3-6-35b-a3b,kimi-k2-6,glm-4-7

for coder in "${CODERS[@]}"; do
  python3 "$LAYERED/run_posture_coder_collapsed.py" \
    --coder "$coder" --manifest "$MANIFEST" \
    --consensus "$LAYER_A/consensus_300.jsonl" \
    --outdir "$POSTURE" --workers 8
done
assert_coder_coverage "$POSTURE"

python3 "$LAYERED/build_posture_collapsed_consensus.py" \
  --indir "$POSTURE" --manifest "$MANIFEST" \
  --out "$POSTURE/consensus.jsonl"

python3 - "$POSTURE/consensus.jsonl" <<'PY'
import json, sys
rows = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
unresolved = [
    row["layered_id"]
    for row in rows
    if row.get("collapsed_primary_label_support", 0) < 2
]
if unresolved:
    raise SystemExit(
        f"{len(unresolved)} posture records lack a two-of-three majority: "
        + ", ".join(unresolved[:20])
    )
print("Phase 23 semantic analysis complete: 240/240 majority-coded records")
PY
