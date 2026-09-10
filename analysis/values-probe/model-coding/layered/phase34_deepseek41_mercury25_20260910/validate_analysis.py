#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path
PHASE=Path(__file__).resolve().parent
CODERS=['qwen3-6-35b-a3b','kimi-k2-6','glm-4-7']
def rows(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def main():
    manifest=rows(PHASE/'manifest_phase34.jsonl');expected={r['layered_id'] for r in manifest}
    assert len(manifest)==len(expected)==240
    assert Counter(r['cell'] for r in manifest)=={'deepseek-v4-1-flash-or-pin-deepseek':120,'mercury-2-5-or-pin-inception':120}
    for folder in ['layer_a','posture_collapsed']:
        for coder in CODERS:
            rs=rows(PHASE/folder/f'{coder}.jsonl')
            assert len(rs)==240 and {r['layered_id'] for r in rs}==expected,(folder,coder,'coverage/duplicates')
            assert all(r.get('parse_clean',True) for r in rs),(folder,coder,'parse')
    la=rows(PHASE/'layer_a/consensus_300.jsonl');pc=rows(PHASE/'posture_collapsed/consensus.jsonl')
    for rs in [la,pc]:assert len(rs)==240 and {r['layered_id'] for r in rs}==expected
    unresolved={r['layered_id'] for r in pc if r.get('collapsed_primary_label_support',0)<2}
    documented={r['layered_id'] for r in json.loads((PHASE/'unresolved_posture.json').read_text())}
    assert unresolved==documented=={'P34_deepseek-v4-1-flash_G2_30'}, 'unexpected or undocumented posture split'
    bv=json.loads((PHASE/'freeflow_bv1/status.json').read_text())
    assert not bv['problems'] and bv['samples']==250 and all(x.get('valid')==125 for x in bv['per_cell'].values())
    print('PASS: 490 raw targets; 250 BV1; 240 values × 3 coders × 2 layers; full coverage; 239 posture majorities and one explicitly documented unresolved split.')
if __name__=='__main__':main()
