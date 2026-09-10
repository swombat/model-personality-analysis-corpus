#!/usr/bin/env python3
"""Add only these two completed model artifacts without regenerating neighbors."""
import importlib.util
import json
import sys
from pathlib import Path
PHASE=Path(__file__).resolve().parent
ROOT=PHASE.parents[4]
CELLS={'deepseek-v4-1-flash-or-pin-deepseek':'deepseek-v4-1-flash','mercury-2-5-or-pin-inception':'mercury-2-5'}
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def merge_index(path, rows, key):
    existing=json.loads(path.read_text()) if path.exists() else []
    newkeys={r[key] for r in rows};merged=[r for r in existing if r[key] not in newkeys]+rows
    path.write_text(json.dumps(sorted(merged,key=lambda r:r[key]),indent=2,ensure_ascii=False)+'\n')
def main():
    cards=module('phase34_cards',ROOT/'internal/scripts/analysis-scripts/build_personality_model_cards.py')
    profiles=module('phase34_profiles',ROOT/'internal/scripts/analysis-scripts/build_personality_model_profiles.py')
    agg=module('phase34_aggregate',ROOT/'internal/scripts/analysis-scripts/run_personality_cell_aggregates.py')
    metas=[];cardrows=[];profilerows=[]
    for cell,model in CELLS.items():
        meta=json.loads((agg.AGG/cell/'packet.metadata.json').read_text());assert meta['samples']==125
        result=agg.process(meta,False);print(json.dumps(result),flush=True)
        text=(ROOT/meta['aggregate']).read_text();body=cards.clean_card_text(cards.section(text,'Cell-level freeflow read'))
        assert body;cards.assert_public_card_clean(model,body)
        path=cards.CARDS/f'{model}.md';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(f'# {model} — freeflow personality card\n\n_Based on 125 freeflow samples._\n\n{body}\n')
        cardrows.append(dict(model=model,safe=model,variants=1,samples=125,card=str(path.relative_to(ROOT)),difference_decision='SINGLE_VARIANT'))
        txt,row=profiles.build_profile(model,[meta]);(profiles.PROFILES/f'{model}.md').write_text(txt);profilerows.append(row);metas.append(meta)
    merge_index(agg.AGG/'manifest.json',metas,'cell')
    merge_index(cards.OUT/'index.json',cardrows,'model');merge_index(profiles.OUT/'index.json',profilerows,'model')
    for out,rows,folder in [(cards.OUT,cardrows,'cards'),(profiles.OUT,profilerows,'profiles')]:
        f=out/'README.md';s=f.read_text()
        for row in rows:
            if f']({folder}/{row["safe"]}.md)' not in s:s+=f'- [{row["model"]}]({folder}/{row["safe"]}.md) — samples: 125\n'
        f.write_text(s)
    print('Isolated profiles and cards assembled',flush=True)
if __name__=='__main__':main()
