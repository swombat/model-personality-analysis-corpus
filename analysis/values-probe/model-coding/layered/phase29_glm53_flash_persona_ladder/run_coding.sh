#!/usr/bin/env bash
set -euo pipefail

PHASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAYERED="$(cd "$PHASE/.." && pwd)"
MANIFEST="$PHASE/manifest_phase29.jsonl"
LAYER_A="$PHASE/layer_a"
POSTURE="$PHASE/posture_collapsed"
LOGS="$PHASE/logs"
CODERS=(qwen3-6-35b-a3b kimi-k2-6 glm-4-7)

mkdir -p "$LAYER_A" "$POSTURE" "$LOGS"
source /Users/danieltenner/dev/research/model-personality-corpus-v2/scripts/source_sops_keys.sh

python3 "$PHASE/build_manifest.py"

pids=()
for coder in "${CODERS[@]}"; do
  python3 "$LAYERED/run_layer_a_coders.py" \
    --coder "$coder" \
    --workers 5 \
    --manifest "$MANIFEST" \
    --outdir "$LAYER_A" \
    >"$LOGS/layer-a-$coder.log" 2>&1 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done

python3 "$LAYERED/build_layer_a_consensus.py" \
  --manifest "$MANIFEST" \
  --outdir "phase29_glm53_flash_persona_ladder/layer_a" \
  --coders "qwen3-6-35b-a3b,kimi-k2-6,glm-4-7"

pids=()
for coder in "${CODERS[@]}"; do
  python3 "$LAYERED/run_posture_coder_collapsed.py" \
    --coder "$coder" \
    --workers 5 \
    --manifest "$MANIFEST" \
    --consensus "$LAYER_A/consensus_300.jsonl" \
    --outdir "$POSTURE" \
    >"$LOGS/posture-$coder.log" 2>&1 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done

python3 "$LAYERED/build_posture_collapsed_consensus.py" \
  --manifest "$MANIFEST" \
  --indir "$POSTURE" \
  --coders "qwen3-6-35b-a3b,kimi-k2-6,glm-4-7" \
  --out "$POSTURE/consensus.jsonl"

echo "Phase 29 coding complete."
