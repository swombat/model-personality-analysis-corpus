#!/usr/bin/env python3
"""Require exact sample identities, final answers, and pinned upstream provenance."""
import json
from pathlib import Path
from collections import Counter
PHASE = Path(__file__).resolve().parent
CORPUS = PHASE.parents[4].parent / 'model-personality-corpus-v2'
CELLS = {'deepseek-v4-1-flash-or-pin-deepseek': ('deepseek/deepseek-v4.1-flash', 'DeepSeek'), 'mercury-2-5-or-pin-inception': ('inception/mercury-2.5', 'Inception')}
def audit():
    problems = []; results = []
    for cell, (model, pin) in CELLS.items():
        for probe in ['freeflow','values']:
            folder = CORPUS / 'data' / ('traces_'+probe) / (('freeflow_' if probe=='freeflow' else '')+cell)
            counts = Counter(); finishes=Counter(); words=[]; cost=0
            expected_counts = ({'SHORT':25, 'MID':25, 'VARY':25, 'OPEN':25, 'LONG':25} if probe=='freeflow' else {'CTRL1':10,'CTRL2':10,'CTRL3':10,'G1':30,'G2':30,'G3':30})
            expected_ids = {f'{c}_{i}' for c,n in expected_counts.items() for i in range(1,n+1)}
            actual_ids = {f.stem for f in folder.glob('*.json')}
            if actual_ids != expected_ids: problems.append(f'{cell}/{probe}: missing={sorted(expected_ids-actual_ids)}, extra={sorted(actual_ids-expected_ids)}')
            for f in sorted(folder.glob('*.json')):
                d=json.loads(f.read_text());raw=d.get('raw',{});choice=(raw.get('choices') or [{}])[0];final=choice.get('message',{}).get('content') or ''
                counts[d.get('condition',f.stem.split('_')[0])]+=1;finishes[choice.get('finish_reason')]+=1;words.append(len(final.split()));cost+=d.get('usage',{}).get('cost',0) or 0
                if not final.strip() or final != d.get('result') or d.get('error') or raw.get('provider')!=pin or raw.get('model')!=model or choice.get('finish_reason')!='stop':
                    problems.append(f'{cell}/{probe}/{f.name}: final/provenance/finish mismatch')
            results.append(dict(cell=cell,probe=probe,samples=len(actual_ids),conditions=dict(counts),finish_reasons=dict(finishes),mean_words=sum(words)/len(words) if words else 0,cost=cost))
    report=dict(results=results,problems=problems)
    (PHASE/'raw_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    result=audit();print(json.dumps(result,indent=2));raise SystemExit(bool(result['problems']))
