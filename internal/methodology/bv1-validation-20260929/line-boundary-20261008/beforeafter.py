import importlib.util,json,glob,csv,os,sys
from pathlib import Path
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
OLD=load('old',sys.argv[1]); NEW=load('new',sys.argv[2])
L='/home/agent/work/mpac/analysis/values-probe/model-coding/layered'
TR='/home/agent/work/model-personality-corpus-v2/data/traces_freeflow'
rows=[];changed=[]
for run in sorted(glob.glob(L+'/*/freeflow_bv1_luna_v1')):
    man={}
    mp=run+'/sample_manifest.tsv'
    if os.path.exists(mp):
        for r in csv.DictReader(open(mp,newline=''),delimiter='\t'):
            man[r['pid'].strip()]=(r['source_json'].strip(),r['output_file'].strip())
    # final outputs
    for pid,(src,out) in man.items():
        if not os.path.exists(out): continue
        text=open(src).read(); source=json.loads(text)['result']; o=open(out).read()
        a=OLD.valid_output(o,source); b=NEW.valid_output(o,source)
        rows.append(('output',pid)); 
        if a!=b: changed.append(('output',pid,a,b))
    # every preserved attempt
    for p in sorted(glob.glob(run+'/attempt_responses/*/*.json')):
        r=json.load(open(p)); pid=p.split('/')[-2]
        src=man.get(pid,(None,))[0]
        if not src:
            cap=run.split('/')[-2]; label=cap.split('_',2)[2]; sid=pid.split('_BV1_')[1]
            src=f'{TR}/freeflow_{label}/{sid}.json'
        source=json.load(open(src))['result']
        o=((r.get('response') or {}).get('choices') or [{}])[0].get('message',{}).get('content') or ''
        a=OLD.valid_output(o,source); b=NEW.valid_output(o,source)
        rows.append(('attempt',p))
        if a!=b: changed.append(('attempt',p.replace(L+'/',''),a,b))
print('runs:',len(glob.glob(L+'/*/freeflow_bv1_luna_v1')),'final outputs checked:',sum(1 for r in rows if r[0]=='output'),'attempt records checked:',sum(1 for r in rows if r[0]=='attempt'))
print('changed decisions:',len(changed))
for c in changed: print(' ',c)
