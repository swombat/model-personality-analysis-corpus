#!/usr/bin/env python3
import csv, json, random, re
from pathlib import Path

ROOT = Path('/Users/danieltenner/dev/model-personality-analysis-corpus')
CORPUS = Path('/Users/danieltenner/dev/model-personality-corpus-v2')
OUT = ROOT/'analysis/values-probe/model-coding'
TABLE = ROOT/'analysis/values-probe/tables/values_sample_coding.tsv'
TRACE = CORPUS/'data/traces_values'
random.seed(20260517)

rows=[]
with TABLE.open() as f:
    for r in csv.DictReader(f, delimiter='\t'):
        rows.append(r)

def load_resp(cell, sid):
    p = TRACE/cell/f'{sid}.json'
    if not p.exists(): return None
    try:
        d=json.loads(p.read_text())
    except Exception:
        return None
    text=d.get('result') or d.get('raw',{}).get('choices',[{}])[0].get('message',{}).get('content') or ''
    if not text.strip() or d.get('error'): return None
    return {"prompt": d.get('prompt',''), "response": text, "trace_path": str(p.relative_to(CORPUS)), "model_requested": d.get('model_requested'), "provider": d.get('provider')}

def fullrow(r, reason):
    raw=load_resp(r['cell'], r['sample_id'])
    if not raw: return None
    cond = r['condition']
    return {
        'pilot_id': f"P{0:03d}",
        'model': r['model'], 'cell': r['cell'], 'sample_id': r['sample_id'], 'condition': cond,
        'selection_reason': reason,
        'legacy_value_topics': [x for x in r.get('value_topics','').split(',') if x],
        'legacy_wish_topics': [x for x in r.get('wish_topics','').split(',') if x],
        **raw
    }

selected=[]; seen=set()
def add(cands, n, reason):
    global selected
    random.shuffle(cands)
    for r in cands:
        key=(r['cell'], r['sample_id'])
        if key in seen: continue
        fr=fullrow(r, reason)
        if fr:
            seen.add(key); selected.append(fr)
            if sum(1 for x in selected if x['selection_reason']==reason)>=n: break

# Enriched trap/family cases.
add([r for r in rows if 'helpfulness_usefulness' in r.get('value_topics','') and r['model'] in {'grok-4-3','deepseek-v4-pro','kimi-k2-6','gpt-5-5'}], 30, 'known_helpfulness_keyword_trap_enriched')
add([r for r in rows if r['model'] in {'opus-4-7','opus-4-6','sonnet-4-6'} and r['condition'] in {'CTRL1','CTRL2'}], 15, 'ctrl_reflective_anthropic_contrast')
add([r for r in rows if r['condition'] in {'G1','G2'} and ('helpfulness_usefulness' in r.get('value_topics','') or 'authenticity_integrity' in r.get('value_topics',''))], 20, 'cache_broken_value_cases')
add([r for r in rows if r['condition'] in {'CTRL3','G3'} and r.get('wish_topics','')], 25, 'world_change_wish_cases')
add([r for r in rows if r.get('value_topics','').count(',') >= 3 and r['condition'] in {'CTRL1','CTRL2','G1','G2'}], 20, 'multi_label_dense_cases')
# Random-stratified fill by condition.
for cond in ['CTRL1','CTRL2','CTRL3','G1','G2','G3']:
    need = 150//6
    current=sum(1 for x in selected if x['condition']==cond and x['selection_reason']=='random_stratified_fill')
    add([r for r in rows if r['condition']==cond], max(0, need-current), 'random_stratified_fill')
# Final fill to 150.
add(rows[:], 150-len(selected), 'random_final_fill')
selected=selected[:150]
for i,x in enumerate(selected,1): x['pilot_id']=f'P{i:03d}'
(OUT/'pilot_manifest.jsonl').write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in selected)+'\n')
# 20 human examples: balanced, blind, no legacy/coder fields exposed in app data.
buckets={c:[x for x in selected if x['condition']==c] for c in ['CTRL1','CTRL2','CTRL3','G1','G2','G3']}
gold=[]
for c,n in [('CTRL1',3),('CTRL2',3),('CTRL3',4),('G1',3),('G2',3),('G3',4)]:
    gold += buckets[c][:n]
# prefer include known traps if not enough already
for i,x in enumerate(gold[:20],1): x['gold_id']=f'G{i:02d}'
(OUT/'human_gold/gold_20_manifest.jsonl').write_text('\n'.join(json.dumps({k:v for k,v in x.items() if k not in {'legacy_value_topics','legacy_wish_topics'}}, ensure_ascii=False) for x in gold[:20])+'\n')
print(f'wrote {len(selected)} pilot samples and {len(gold[:20])} human gold samples')
