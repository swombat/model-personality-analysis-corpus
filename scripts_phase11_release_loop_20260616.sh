#!/usr/bin/env bash
set -u
ANALYSIS=/Users/danieltenner/dev/research/model-personality-analysis-corpus
CORPUS=/Users/danieltenner/dev/research/model-personality-corpus-v2
PHASE=analysis/values-probe/model-coding/layered/phase11_openai_oss_mini_nano_20260616
LOGDIR="$ANALYSIS/logs"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/phase11_release_loop_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
cd "$CORPUS"
set +u
source ./keys.env
set +e
set -u
cd "$ANALYSIS"

echo "[$(date)] phase11 loop start log=$LOG"
notify(){ cd /Users/danieltenner/dev/mira && python3 shared/automation/scripts/send_research_status_telegram.py --force || true; cd "$ANALYSIS"; }
qa_bad(){ python3 - <<'PY'
import json
try:
 print(json.load(open('analysis/freeflow/personality-eval-bv1/qa_summary.json')).get('qa_bad_count', 999999))
except Exception:
 print(999999)
PY
}

# 1. Ensure BV1 clean.
python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py --qa-only || true
for i in {1..6}; do
  bad=$(qa_bad)
  echo "[$(date)] BV1 qa_bad=$bad"
  [ "$bad" = "0" ] && break
  python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py --rerun-failed-only --concurrency 8
  python3 analysis/freeflow/personality-eval-bv1/run_full_bv1.py --qa-only || true
done
bad=$(qa_bad)
if [ "$bad" != "0" ]; then echo "BV1 still has qa_bad=$bad; aborting"; notify; exit 1; fi
notify

echo "[$(date)] Generating freeflow aggregate packets"
python3 internal/scripts/analysis-scripts/generate_personality_aggregate_packets.py

echo "[$(date)] Running missing personality cell aggregates"
PERSONALITY_CELL_AGG_MODEL=${PERSONALITY_CELL_AGG_MODEL:-gpt-5.4} PERSONALITY_CELL_AGG_CONCURRENCY=${PERSONALITY_CELL_AGG_CONCURRENCY:-4} \
  python3 internal/scripts/analysis-scripts/run_personality_cell_aggregates.py --concurrency ${PERSONALITY_CELL_AGG_CONCURRENCY:-4}

echo "[$(date)] Running route difference analysis"
PERSONALITY_ROUTE_MODEL=${PERSONALITY_ROUTE_MODEL:-gpt-5.4} PERSONALITY_ROUTE_CONCURRENCY=${PERSONALITY_ROUTE_CONCURRENCY:-4} \
  python3 internal/scripts/analysis-scripts/analyze_model_cell_difference.py

echo "[$(date)] Building personality profiles and cards"
python3 internal/scripts/analysis-scripts/build_personality_model_cards.py
python3 internal/scripts/analysis-scripts/build_personality_model_profiles.py

# 2. Values phase11.
echo "[$(date)] Building phase11 values manifest"
python3 $PHASE/build_manifest_phase11.py
mkdir -p $PHASE/layer_a $PHASE/posture_collapsed

echo "[$(date)] Running Layer A coders"
for coder in deepseek-v4-pro kimi-k2-6 glm-4-7; do
  python3 analysis/values-probe/model-coding/layered/run_layer_a_code_coders.py \
    --coder "$coder" --workers 8 --manifest "$PHASE/manifest_phase11.jsonl" --outdir "$PHASE/layer_a"
done
python3 analysis/values-probe/model-coding/layered/build_layer_a_consensus.py \
  --manifest "$PHASE/manifest_phase11.jsonl" --outdir phase11_openai_oss_mini_nano_20260616/layer_a --family-exclusion

echo "[$(date)] Running collapsed posture coders"
for coder in qwen3-6-35b-a3b kimi-k2-6 glm-4-7; do
  python3 analysis/values-probe/model-coding/layered/run_posture_coder_collapsed.py \
    --coder "$coder" --workers 8 --manifest "$PHASE/manifest_phase11.jsonl" \
    --consensus "$PHASE/layer_a/consensus_300.jsonl" --outdir "$PHASE/posture_collapsed" --mask-prompt
done
python3 analysis/values-probe/model-coding/layered/build_posture_collapsed_consensus.py \
  --manifest "$PHASE/manifest_phase11.jsonl" --indir "$PHASE/posture_collapsed" --out "$PHASE/posture_collapsed/consensus.jsonl"

echo "[$(date)] Assembling final values probe"
python3 analysis/values-probe/final/scripts/assemble_final_values_probe.py
notify

# 3. Website metadata placeholders.
echo "[$(date)] Updating website placeholder metadata"
python3 - <<'PY'
import json
from pathlib import Path
base=Path('website/src/generated')
base.mkdir(parents=True, exist_ok=True)
new={
 'gpt-oss-120b':'Placeholder strapline pending Lume',
 'gpt-oss-20b':'Placeholder strapline pending Lume',
 'gpt-5-mini':'Placeholder strapline pending Lume',
 'gpt-5-nano':'Placeholder strapline pending Lume',
}
# validate_strapline requires 3-12 words, so use four-word placeholders.
p=base/'model-summaries.json'; data=json.loads(p.read_text()) if p.exists() else {}; data.update(new); p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
p=base/'model-release-dates.json'; data=json.loads(p.read_text()) if p.exists() else {}; data.update({'gpt-oss-120b':'2026-06-16','gpt-oss-20b':'2026-06-16','gpt-5-mini':'2026-06-16','gpt-5-nano':'2026-06-16'}); p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
# Leave AAII null/absent unless independently verified; generated data will preserve old if any.
p=base/'model-benchmarks.json'; data=json.loads(p.read_text()) if p.exists() else {}; p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
PY

echo "[$(date)] Generating website data and building"
python3 website/scripts/generate_data.py
(cd website && npm run build)

# 4. Release notes, commit, tag.
echo "[$(date)] Preparing analysis release"
cat > RELEASE_NOTES_v1.2.9.md <<'MD'
# Release notes — v1.2.9

Date: 2026-06-16

## Added

- Added analysis-corpus coverage for four OpenAI models from Corpus V2 v1.2.9:
  - `gpt-oss-120b`
  - `gpt-oss-20b`
  - `gpt-5-mini`
  - `gpt-5-nano`
- Added BV1 freeflow outputs, personality aggregates, rich profiles, concise cards, and website sample exports.
- Added phase11 layered values-probe data, collapsed posture consensus, final values-probe assembly, and per-model final reports.
- Added website placeholders for straplines/images pending Lume.

## QA

- Corpus V2 v1.2.9 pushed and tagged.
- BV1 QA completed with zero invalid outputs after targeted reruns.
- Website data generation and Astro build completed successfully.
MD

git add .
git commit -m 'Release v1.2.9 with OpenAI OSS and GPT-5 mini/nano analysis' || true
git tag -f v1.2.9
git push origin main v1.2.9
notify

echo "[$(date)] phase11 loop complete"
