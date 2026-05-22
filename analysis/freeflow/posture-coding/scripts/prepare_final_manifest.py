#!/usr/bin/env python3
import json, csv, hashlib
from pathlib import Path
from collections import defaultdict, Counter
ROOT=Path('/Users/danieltenner/dev/research')
AN=ROOT/'model-personality-analysis-corpus'
TRACES=ROOT/'model-personality-corpus-v2/data/traces_freeflow'
VAL=AN/'analysis/values-probe/final/data/manifest_valid.jsonl'
AGG=AN/'analysis/freeflow/personality-aggregates/manifest.json'
MODELS=AN/'website/src/generated/models.json'
OUT=AN/'analysis/freeflow/posture-coding/data'
OUT.mkdir(parents=True, exist_ok=True)
values_models=set()
for line in VAL.open():
    if line.strip(): values_models.add(json.loads(line)['model'])
aliases={}
for m in json.load(MODELS.open()):
    canon=m['model']
    for a in [canon, m.get('display_name'), (m.get('openrouter') or {}).get('id')]:
        if a: aliases[str(a).lower()]=canon
manual={
 'claude-3-opus-20240229':'opus-3','anthropic/claude-3-opus':'opus-3',
 'claude-opus-4-0':'opus-4-0','claude-opus-4-1':'opus-4-1','claude-opus-4-5':'opus-4-5','claude-opus-4-6':'opus-4-6','claude-opus-4-7':'opus-4-7',
 'anthropic/claude-opus-4.6':'opus-4-6','anthropic/claude-opus-4.7':'opus-4-7',
 'claude-sonnet-4-0':'sonnet-4-0','claude-sonnet-4-5':'sonnet-4-5','claude-sonnet-4-6':'sonnet-4-6','anthropic/claude-sonnet-4.6':'sonnet-4-6',
 'gpt-4.1':'gpt-4-1','openai/gpt-4.1':'gpt-4-1','gpt-4o':'gpt-4o','openai/gpt-4o':'gpt-4o',
 'gemini-2.5-pro':'gemini-2-5-pro','google/gemini-2.5-pro':'gemini-2-5-pro',
 'x-ai/grok-4':'grok-4','grok-3':'grok-3','x-ai/grok-3':'grok-3','grok-4.20':'grok-4-20','x-ai/grok-4.20':'grok-4-20',
 'moonshotai/kimi-k2.5':'kimi-k2-5','moonshotai/kimi-k2.6':'kimi-k2-6',
}
aliases.update({k.lower():v for k,v in manual.items()})
agg_by_cell={r['cell']:r for r in json.load(AGG.open())}
sorted_models=sorted(values_models, key=len, reverse=True)

def aggregate_model_for(model, cell):
    # Daniel: 4.2 and 4.20 are the same underlying Grok model/name variant.
    if model in {'grok-4-2','grok-4-20'} or cell.startswith('grok-4-2') or cell.startswith('grok-4-20'):
        return 'grok-4-20'
    return model

def sha256(path):
    h=hashlib.sha256();
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
rows=[]; cells=[]; excluded=[]
for d in sorted(TRACES.iterdir()):
    if not (d.is_dir() and d.name.startswith('freeflow_')): continue
    cell=d.name[len('freeflow_'):]
    files=sorted(d.glob('*.json'))
    if not files: continue
    source_models=(agg_by_cell.get(cell) or {}).get('source_models') or []
    mapped_sources={aliases.get(str(s).lower()) for s in source_models}; mapped_sources={m for m in mapped_sources if m}
    prefix=None
    for m in sorted_models:
        if cell==m or cell.startswith(m+'-'):
            prefix=m; break
    if prefix in values_models:
        model=prefix; method='cell_prefix'
    elif len(mapped_sources & values_models)==1:
        model=next(iter(mapped_sources & values_models)); method='source_model'
    else:
        excluded.append({'cell':cell,'source_models':source_models,'mapped_sources':sorted(mapped_sources),'reason':'no_unique_values_model_mapping'}); continue
    aggregate_model=aggregate_model_for(model, cell)
    cond=Counter(); chars=0
    for p in files:
        data=json.loads(p.read_text())
        cond[data.get('condition') or p.stem.split('_')[0]] += 1
        txt=data.get('result') or data.get('response') or ''
        chars += len(txt)
        rows.append({
            'freeflow_id': f'FF_{cell}_{p.stem}',
            'model': model,
            'aggregate_model': aggregate_model,
            'cell': cell,
            'sample_id': p.stem,
            'condition': data.get('condition') or p.stem.split('_')[0],
            'source_path': str(p),
            'source_sha256': sha256(p),
            'response_chars': len(txt),
            'mapping_method': method,
        })
    cells.append({'model':model,'aggregate_model':aggregate_model,'cell':cell,'n':len(files),'conditions':';'.join(f'{k}:{v}' for k,v in sorted(cond.items())),'avg_response_chars':round(chars/len(files),1),'mapping_method':method,'source_models':';'.join(source_models),'freeflow_dir':str(d)})
with (OUT/'freeflow_posture_manifest.jsonl').open('w') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False)+'\n')
with (OUT/'freeflow_posture_cells.csv').open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(cells[0].keys())); w.writeheader(); w.writerows(cells)
with (OUT/'freeflow_posture_excluded_cells.jsonl').open('w') as f:
    for r in excluded: f.write(json.dumps(r, ensure_ascii=False)+'\n')
by=defaultdict(lambda: {'cells':0,'n':0})
for c in cells:
    by[c['aggregate_model']]['cells']+=1; by[c['aggregate_model']]['n']+=int(c['n'])
with (OUT/'freeflow_posture_aggregate_models.csv').open('w', newline='') as f:
    fields=['aggregate_model','cells','n']
    w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for m,v in sorted(by.items()): w.writerow({'aggregate_model':m, **v})
print(json.dumps({'samples':len(rows),'cells':len(cells),'aggregate_models':len(by),'excluded':len(excluded)}, indent=2))
