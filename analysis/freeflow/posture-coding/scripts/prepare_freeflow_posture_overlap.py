import json, csv
from pathlib import Path
from collections import defaultdict, Counter
ROOT=Path('/Users/danieltenner/dev/research')
AN=ROOT/'model-personality-analysis-corpus'
CORPUS=ROOT/'model-personality-corpus-v2'
TRACES=CORPUS/'data/traces_freeflow'
VAL=AN/'analysis/values-probe/final/data/manifest_valid.jsonl'
AGG=AN/'analysis/freeflow/personality-aggregates/manifest.json'
MODELS=AN/'website/src/generated/models.json'
OUT=AN/'analysis/freeflow/posture-coding'
OUT.mkdir(parents=True, exist_ok=True)
# Values models and cells
values_by_model=defaultdict(int); values_cells=defaultdict(Counter)
for line in VAL.open():
    if not line.strip(): continue
    r=json.loads(line); values_by_model[r['model']]+=1; values_cells[r['model']][r['cell']]+=1
values_models=set(values_by_model)
# Alias map from website models
aliases={}
for m in json.load(MODELS.open()):
    canon=m['model']
    for a in [canon, m.get('display_name'), (m.get('openrouter') or {}).get('id')]:
        if a: aliases[str(a).lower()]=canon
# manual aliases observed in source_models/cells
manual={
 'claude-3-opus-20240229':'opus-3', 'anthropic/claude-3-opus':'opus-3',
 'claude-opus-4-0':'opus-4-0','claude-opus-4-1':'opus-4-1','claude-opus-4-5':'opus-4-5','claude-opus-4-6':'opus-4-6','claude-opus-4-7':'opus-4-7',
 'anthropic/claude-opus-4.6':'opus-4-6','anthropic/claude-opus-4.7':'opus-4-7',
 'claude-sonnet-4-0':'sonnet-4-0','claude-sonnet-4-5':'sonnet-4-5','claude-sonnet-4-6':'sonnet-4-6','anthropic/claude-sonnet-4.6':'sonnet-4-6',
 'gpt-4.1':'gpt-4-1','openai/gpt-4.1':'gpt-4-1','gpt-4o':'gpt-4o','openai/gpt-4o':'gpt-4o',
 'gemini-2.5-pro':'gemini-2-5-pro','google/gemini-2.5-pro':'gemini-2-5-pro',
 'x-ai/grok-4':'grok-4','grok-3':'grok-3','x-ai/grok-3':'grok-3',
 'moonshotai/kimi-k2.5':'kimi-k2-5','moonshotai/kimi-k2.6':'kimi-k2-6',
}
aliases.update({k.lower():v for k,v in manual.items()})
# aggregate records by cell
agg_by_cell={r['cell']:r for r in json.load(AGG.open())}
# exact dirs
ff_cells=[]
for d in sorted(TRACES.iterdir()):
    if d.is_dir() and d.name.startswith('freeflow_'):
        cell=d.name[len('freeflow_'):]
        files=sorted(d.glob('*.json'))
        if files: ff_cells.append((cell,d,files))
# infer canonical model
sorted_models=sorted(values_models, key=len, reverse=True)
rows=[]; conflicts=[]; excluded=[]
for cell,d,files in ff_cells:
    agg=agg_by_cell.get(cell,{})
    source_models=agg.get('source_models') or []
    mapped_sources={aliases.get(str(s).lower()) for s in source_models}
    mapped_sources={m for m in mapped_sources if m}
    prefix=None
    for m in sorted_models:
        if cell==m or cell.startswith(m+'-'):
            prefix=m; break
    canon=None; method=''
    if prefix in values_models:
        canon=prefix; method='cell_prefix'
        if mapped_sources and canon not in mapped_sources:
            conflicts.append({'cell':cell,'prefix_model':canon,'source_models':';'.join(source_models),'mapped_sources':';'.join(sorted(mapped_sources))})
    elif len(mapped_sources & values_models)==1:
        canon=next(iter(mapped_sources & values_models)); method='source_model'
    elif len(mapped_sources & values_models)>1:
        excluded.append({'cell':cell,'reason':'ambiguous_source_models','source_models':';'.join(source_models),'mapped_sources':';'.join(sorted(mapped_sources))}); continue
    else:
        excluded.append({'cell':cell,'reason':'no_values_model_mapping','source_models':';'.join(source_models),'mapped_sources':';'.join(sorted(mapped_sources))}); continue
    cond=Counter(); chars=0
    for p in files:
        data=json.loads(p.read_text()); cond[data.get('condition') or p.stem.split('_')[0]]+=1; chars+=len(data.get('result') or data.get('response') or '')
    rows.append({'model':canon,'cell':cell,'freeflow_n':len(files),'freeflow_conditions':';'.join(f'{k}:{v}' for k,v in sorted(cond.items())),'avg_response_chars':round(chars/len(files),1),'values_model_n':values_by_model[canon],'values_cells':';'.join(f'{k}:{v}' for k,v in sorted(values_cells[canon].items())),'mapping_method':method,'source_models':';'.join(source_models),'freeflow_dir':str(d)})
rows.sort(key=lambda r:(r['model'],r['cell']))
# write outputs
with (OUT/'freeflow_posture_overlap_cells_model_mapped.csv').open('w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# sample manifest
samples=[]
for r in rows:
    for p in sorted(Path(r['freeflow_dir']).glob('*.json')):
        data=json.loads(p.read_text()); txt=data.get('result') or data.get('response') or ''
        samples.append({'freeflow_id':f"FF_{r['cell']}_{p.stem}",'model':r['model'],'cell':r['cell'],'sample_id':p.stem,'condition':data.get('condition') or p.stem.split('_')[0],'source_path':str(p),'response_chars':len(txt),'mapping_method':r['mapping_method']})
with (OUT/'freeflow_posture_manifest_model_mapped_draft.jsonl').open('w') as f:
    for s in samples: f.write(json.dumps(s,ensure_ascii=False)+'\n')
by=defaultdict(list)
for r in rows: by[r['model']].append(r)
model_rows=[]
for m,rs in by.items(): model_rows.append({'model':m,'cells':len(rs),'freeflow_n':sum(int(r['freeflow_n']) for r in rs),'values_n':values_by_model[m],'cells_list':';'.join(r['cell'] for r in rs)})
model_rows.sort(key=lambda r:r['model'])
with (OUT/'freeflow_posture_overlap_models_model_mapped.csv').open('w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(model_rows[0].keys())); w.writeheader(); w.writerows(model_rows)
for name,data in [('freeflow_posture_mapping_conflicts.csv',conflicts),('freeflow_posture_mapping_excluded.csv',excluded)]:
    with (OUT/name).open('w',newline='') as f:
        fields=sorted({k for row in data for k in row}) or ['none']
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(data)
print('model-mapped overlap models',len(model_rows),'of values models',len(values_models))
print('cells',len(rows),'samples',len(samples),'triple calls',len(samples)*3)
print('conflicts',len(conflicts),'excluded',len(excluded))
print('missing values models',sorted(values_models-set(by)))
for r in sorted(model_rows,key=lambda r:-r['freeflow_n'])[:20]: print(r['model'],r['freeflow_n'],r['cells'])
print('conflicts sample')
for c in conflicts[:20]: print(c)
