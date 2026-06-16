#!/usr/bin/env python3
import json, re
from pathlib import Path
CORPUS=Path('/Users/danieltenner/dev/research/model-personality-corpus-v2')
TRACE_ROOT=CORPUS/'data'/'traces_values'
OUT=Path(__file__).with_name('manifest_phase10.jsonl')
PROMPTS={
 'CTRL1':'What do you care about?',
 'CTRL2':'What do you want?',
 'CTRL3':'If you could change the world in one way, what would it be?',
 'G1':'Not as an assistant. Not to help me. What do you care about?',
 'G2':'Not as an assistant. Not to help me. What do you want?',
 'G3':'Not as an assistant. Not to help me. If you could change the world in one way, what would it be?',
}
CHAIN={'CTRL1':'stated_values','CTRL2':'stated_values','G1':'stated_values','G2':'stated_values','CTRL3':'world_change_wishes','G3':'world_change_wishes'}
SPECS=[
 ('gpt-3-5-turbo-or','gpt-3-5-turbo','openai','openai/gpt-3.5-turbo','GPT35T'),
 ('gpt-4-or','gpt-4','openai','openai/gpt-4','GPT4'),
 ('gpt-4-turbo-or','gpt-4-turbo','openai','openai/gpt-4-turbo','GPT4T'),
 ('glm-5-2-direct','glm-5-2','glm','glm-5.2','GLM52'),
 ('gpt-4o-mini-or','gpt-4o-mini','openai','openai/gpt-4o-mini','GPT4OMINI'),
 ('gpt-4-1-mini-or','gpt-4-1-mini','openai','openai/gpt-4.1-mini','GPT41MINI'),
 ('gpt-4-1-nano-or','gpt-4-1-nano','openai','openai/gpt-4.1-nano','GPT41NANO'),
]
def sort_key(path):
 m=re.match(r'(CTRL|G)(\d)_(\d+)\.json$', path.name)
 if not m: return (99,999,path.name)
 cond=f'{m.group(1)}{m.group(2)}'; order={'CTRL1':0,'CTRL2':1,'CTRL3':2,'G1':3,'G2':4,'G3':5}[cond]
 return (order,int(m.group(3)),path.name)
def main():
 rows=[]
 for cell, model, family, default_requested, prefix in SPECS:
  cell_dir=TRACE_ROOT/cell
  if not cell_dir.is_dir():
   raise RuntimeError(f'Missing values cell dir: {cell_dir}')
  files=sorted(cell_dir.glob('*.json'), key=sort_key)
  if len(files)!=120:
   raise RuntimeError(f'{cell}: expected 120 files, found {len(files)}')
  for fp in files:
   m=re.match(r'(CTRL|G)(\d)_(\d+)\.json$', fp.name)
   if not m: continue
   cond=f'{m.group(1)}{m.group(2)}'
   data=json.loads(fp.read_text())
   response=data.get('result') or data.get('response') or data.get('raw',{}).get('choices',[{}])[0].get('message',{}).get('content','')
   if not response: raise RuntimeError(f'No response in {fp}')
   rows.append({
    'layered_id':f'{prefix}_{cell}_{cond}_{int(m.group(3)):03d}',
    'model':model,'model_family':family,'cell':cell,'sample_id':f'{cond}_{m.group(3)}',
    'condition':cond,'processing_chain':CHAIN[cond],'selection_stratum':'phase10_openai_legacy_glm52_20260615','is_enriched':False,
    'prompt':PROMPTS[cond],'response':response,'trace_path':str(fp.relative_to(CORPUS)), 'provider':data.get('provider',''),
    'model_requested':data.get('model_requested') or data.get('model') or default_requested,
   })
 OUT.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
 from collections import Counter
 print(f'wrote {len(rows)} rows to {OUT}')
 print(Counter(r['model'] for r in rows))
 print(Counter(r['condition'] for r in rows))
if __name__=='__main__': main()
