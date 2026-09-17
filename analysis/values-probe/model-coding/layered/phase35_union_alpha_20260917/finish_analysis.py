#!/usr/bin/env python3
"""Bounded QA recovery and scoped assembly; never reroll unresolved judgments."""
import json, shutil, subprocess, sys
from pathlib import Path
PHASE=Path(__file__).resolve().parent
ROOT=PHASE.parents[4]
CODERS=['qwen3-6-35b-a3b','kimi-k2-6','glm-4-7']
def rows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def run(*args): subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True)
def main():
    run(PHASE/'audit_raw.py')
    manifest=rows(PHASE/'manifest_phase35.jsonl');expected={r['layered_id'] for r in manifest}
    assert len(expected)==len(manifest)==120
    for folder in ['layer_a','posture_collapsed']:
        for coder in CODERS:
            data=rows(PHASE/folder/f'{coder}.jsonl')
            assert len(data)==120 and {r['layered_id'] for r in data}==expected
            assert all(r.get('parse_clean',True) for r in data)
    bv=PHASE/'freeflow_bv1/status.json'
    for attempt in range(1,4):
        status=json.loads(bv.read_text())
        if not status['problems']:break
        backup=PHASE/'freeflow_bv1'/f'before_retry_{attempt}'
        backup.mkdir(exist_ok=False);shutil.copy2(bv,backup/'status.json')
        for problem in status['problems']:
            source=ROOT/'analysis/freeflow/personality-eval-bv1/outputs'/problem['cell']/(Path(problem['sample_id']).stem+'.md')
            if source.exists():shutil.copy2(source,backup/source.name)
        subprocess.run([sys.executable,str(PHASE/'run_freeflow_bv1.py')],cwd=ROOT,check=False)
    assert not json.loads(bv.read_text())['problems'], 'BV1 invalid after bounded retries'
    posture=PHASE/'posture_collapsed'
    data=rows(posture/'consensus.jsonl');split={r['layered_id'] for r in data if r.get('collapsed_primary_label_support',0)<2}
    # Existence of this immutable backup records that adjudication has already been attempted.
    if split and not (posture/'before_adjudication').exists():
        (posture/'before_adjudication').mkdir()
        for name in ['consensus.jsonl']+[c+'.jsonl' for c in CODERS]:shutil.copy2(posture/name,posture/'before_adjudication'/name)
        adj=PHASE/'adjudication_manifest.jsonl';adj.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in manifest if r['layered_id'] in split))
        run(ROOT/'analysis/values-probe/final/scripts/adjudicate_posture_split.py','--manifest',adj,'--layer-a-consensus',PHASE/'layer_a/consensus_300.jsonl','--outdir',posture/'adjudicated')
        for coder in CODERS:
            replacements=rows(posture/'adjudicated'/f'{coder}.jsonl'); byid={r['layered_id']:r for r in replacements}
            assert len(replacements)==len(byid) and set(byid)==split
            original=rows(posture/'before_adjudication'/f'{coder}.jsonl')
            (posture/f'{coder}.jsonl').write_text(''.join(json.dumps(byid.get(r['layered_id'],r),ensure_ascii=False)+'\n' for r in original))
        run(PHASE.parent/'build_posture_collapsed_consensus.py','--indir',posture,'--manifest',PHASE/'manifest_phase35.jsonl','--out',posture/'consensus.jsonl')
    unresolved=[r for r in rows(posture/'consensus.jsonl') if r.get('collapsed_primary_label_support',0)<2]
    (PHASE/'unresolved_posture.json').write_text(json.dumps(unresolved,indent=2,ensure_ascii=False)+'\n')
    run(PHASE/'validate_analysis.py')
    run(PHASE/'build_aggregate_packets.py')
    run(PHASE/'assemble_models.py')
    # Human review must attach residual ambiguity to public report before release.
    run(ROOT/'analysis/values-probe/final/scripts/assemble_final_values_probe.py')
    print('ASSEMBLED; awaiting integration and editorial review',flush=True)
if __name__=='__main__':main()
