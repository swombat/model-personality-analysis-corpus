import importlib.util,json,pathlib,hashlib,sys,time,collections
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
A=pathlib.Path('/Users/danieltenner/dev/research/model-personality-analysis-corpus')
R=A.parent/'model-personality-corpus-v2'
OUT=pathlib.Path(__file__).resolve().parent

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
style=module('style',A/'internal/metrics-trial/freeflow_metrics.py')
params=dict(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=200000,sublinear_tf=True,norm='l2')
meta={m['model'] for m in json.loads((A/'website/src/generated/models.json').read_text()) if m.get('status')!='redirect'}
docs=[];labels=[];conditions=[];finger=hashlib.sha256()
for p in sorted((A/'website/public/data/samples').glob('*.json')):
 d=json.loads(p.read_text())
 if d['model'] not in meta or d['model'] in ('glm-5-3','glm-5-3-flash','glm-5-3-flashx'):continue
 for s in d['samples']:
  if s['type']=='freeflow' and s.get('result'):
   docs.append(s['result']);labels.append(d['model']);conditions.append(s['condition'])
 finger.update(p.name.encode()+p.read_bytes())
cells={'glm-5-3':'glm-5-3-or-pin-z-ai-20260825','glm-5-3-flash':'glm-5-3-flash-or-pin-z-ai-20260826','glm-5-3-flashx':'glm-5-3-flashx-or-pin-zai'}
raws={};metrics={}
for model,cell in cells.items():
 rows=[];mm=[]
 for p in sorted((R/'data/traces_freeflow'/('freeflow_'+cell)).glob('*.json')):
  d=json.loads(p.read_text())
  assert d['result']==d['raw']['choices'][0]['message']['content'];assert d['result'].strip()
  rows.append(d);m=style.compute_sample_metrics(d['result'],d['prompt'],d.get('usage',{}),None);m['condition']=d['condition'];
  if d['condition']!='LONG': mm.append(m)
  finger.update(p.name.encode()+p.read_bytes())
  if model in cells:docs.append(d['result']);labels.append(model);conditions.append(d['condition'])
 assert len(rows)==125
 raws[model]=rows;metrics[model]=mm
 # Verify control bundle exactly matches audited raw corpus.
 if model!='glm-5-3-flashx':
  assert sorted(d['result'] for d in rows)==sorted(t for t,l in zip(docs,labels) if l==model)
print('Fitting',len(docs),'documents',len(set(labels)),'models',flush=True)
labels=np.array(labels);conditions=np.array(conditions);models=sorted(set(labels));X=TfidfVectorizer(**params).fit_transform(docs)
print('Matrix',X.shape,flush=True)
centroids=normalize(np.vstack([np.asarray(X[labels==m].mean(axis=0)) for m in models]));sim=cosine_similarity(centroids)
result={'method':'Published map char_wb TF-IDF centroid cosine; refit entire current published sample corpus plus125FlashX samples. No projection needed.','parameters':params,'documents':len(docs),'models':len(models),'source_fingerprint':finger.hexdigest(),'pairs':{},'nearest':{},'style':{},'condition_pairs':{},'split_half':{}}
for a in cells:
 i=models.index(a);result['nearest'][a]=[{'model':models[j],'cosine':float(sim[i,j])} for j in np.argsort(-sim[i]) if j!=i][:10]
 for b in cells:
  if a<b:result['pairs'][a+' vs '+b]=float(sim[i,models.index(b)])
for condition in sorted(set(conditions[labels=='glm-5-3-flashx'])):
 cs=normalize(np.vstack([np.asarray(X[(labels==m)&(conditions==condition)].mean(axis=0)) for m in cells]));ss=cosine_similarity(cs)
 result['condition_pairs'][condition]={'base_flashx':float(ss[0,2]),'flash_flashx':float(ss[1,2]),'base_flash':float(ss[0,1])}
nonlong=normalize(np.vstack([np.asarray(X[(labels==m)&(conditions!='LONG')].mean(axis=0)) for m in cells]))
result['nonlong_similarity']=dict(zip(['base_flash','base_flashx','flash_flashx'],[float(v) for v in cosine_similarity(nonlong)[np.triu_indices(3,1)]]))
result['style_scope']='100 samples/model: SHORT,MID,OPEN,VARY; LONG excluded equally for all three due to15 length finishes in base GLM5.3'
result['raw_finish_counts']={m:dict(collections.Counter(d['raw']['choices'][0]['finish_reason'] for d in rr)) for m,rr in raws.items()}
rng=np.random.default_rng(20260922)
# Independent stratified bootstrap: sample IDs are replicate labels, not pairs.
keys=['words','sent_len_mean','para_len_mean','n_paras','heading_rate','has_title','emdash_rate','i_rate','you_rate','we_rate','ai_selfref','hedge_rate','abstract_rate','concrete_rate','ttr_200','mtld','opener_meta','dialogue_rate']
for k in keys:
 values={m:np.array([r[k] if r[k] != '' else np.nan for r in rr],float) for m,rr in metrics.items()}
 means={m:float(np.nanmean(v)) for m,v in values.items()};diffs=[]
 for _ in range(2000):
  boot={}
  for m,rr in metrics.items():
   ids=np.concatenate([rng.choice([i for i,r in enumerate(rr) if r['condition']==c],25) for c in sorted({r['condition'] for r in rr})])
   boot[m]=float(np.nanmean(values[m][ids]))
  diffs.append(boot['glm-5-3-flashx']-boot['glm-5-3'])
 result['style'][k]={'means':means,'flashx_minus_base_CI95':np.percentile(diffs,[2.5,97.5]).tolist()}
for model in cells:
 vals=[]
 for _ in range(100):
  a=[];b=[]
  for cond in sorted(set(conditions[(labels==model)&(conditions!='LONG')])):
   ids=np.flatnonzero((labels==model)&(conditions==cond));rng.shuffle(ids);a.extend(ids[:12]);b.extend(ids[12:])
  va=np.asarray(X[a].mean(axis=0));vb=np.asarray(X[b].mean(axis=0));vals.append(float(cosine_similarity(va,vb)[0,0]))
 result['split_half'][model]={'median':float(np.median(vals)),'range95':np.percentile(vals,[2.5,97.5]).tolist(),'note':'48vs52 samples, LONG excluded; finite-sample reference, not a formal equivalence test'}
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'sample-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
