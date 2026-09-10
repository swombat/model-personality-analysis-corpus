#!/usr/bin/env bash
set -euo pipefail
PHASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$PHASE/../../../../.." && pwd)"
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"
source "$ROOT/../model-personality-corpus-v2/scripts/source_sops_keys.sh"
ROOT="$(cd "$PHASE/../../../../.." && pwd)"
trap 'echo "STOPPED rc=$? at $(date -u)"' EXIT
cd "$ROOT"
(
 for round in 1 2 3; do
  if python3 "$PHASE/run_freeflow_bv1.py"; then exit 0; fi
 done
 exit 1
) > "$PHASE/bv1-retry.log" 2>&1 &
BV1=$!
python3 analysis/values-probe/final/scripts/adjudicate_posture_split.py --manifest "$PHASE/adjudication_manifest.jsonl" --layer-a-consensus "$PHASE/layer_a/consensus_300.jsonl" --outdir "$PHASE/posture_collapsed/adjudicated" > "$PHASE/adjudication.log" 2>&1
python3 - "$PHASE" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])/'posture_collapsed'
for coder in ['qwen3-6-35b-a3b','kimi-k2-6','glm-4-7']:
 def load(f):return [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
 new={r['layered_id']:r for r in load(p/'adjudicated'/f'{coder}.jsonl')}
 assert len(new)==7
 old=load(p/'before_adjudication'/f'{coder}.jsonl')
 assert set(new)<= {r['layered_id'] for r in old}
 (p/f'{coder}.jsonl').write_text(''.join(json.dumps(new.get(r['layered_id'],r),ensure_ascii=False)+'\n' for r in old))
PY
python3 analysis/values-probe/model-coding/layered/build_posture_collapsed_consensus.py --indir "$PHASE/posture_collapsed" --manifest "$PHASE/manifest_phase34.jsonl" --out "$PHASE/posture_collapsed/consensus.jsonl"
wait "$BV1"
python3 "$PHASE/audit_raw.py" > "$PHASE/raw_audit.log"
python3 "$PHASE/validate_analysis.py"
python3 "$PHASE/build_aggregate_packets.py"
python3 "$PHASE/assemble_models.py"
python3 analysis/values-probe/final/scripts/assemble_final_values_probe.py > "$PHASE/final-assembly.log"
echo "CLASSIFICATION_AND_ASSEMBLY_COMPLETE $(date -u)"
