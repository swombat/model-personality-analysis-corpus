import concurrent.futures,hashlib,importlib.util,json,os,re,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];RAW=ROOT.parent/'model-personality-corpus-v2'
spec=importlib.util.spec_from_file_location('bv',ROOT/'analysis/freeflow/personality-eval-bv1/run_full_bv1.py');bv=importlib.util.module_from_spec(spec);spec.loader.exec_module(bv)
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
if not (P/'manifest.json').exists():
 samples=json.loads((P.parent/'bv1-replacement-pilot-20260928/manifest.json').read_text())['samples']
 for family in ['qwen3-8-max-or-pin-alibaba','opus-5-or-pin-anthropic','deepseek-v4-pro-direct','union-alpha-or-pin-stealth','sonnet-5-5-or-pin-anthropic','chatglm2-6b-local-transformers427-mps-fp16-rd2e2d91']:
  for sid in ['SHORT_7','LONG_13']:
   path=RAW/'data/traces_freeflow'/('freeflow_'+family)/(sid+'.json')
   if not path.exists():
    avail=sorted(path.parent.glob('*.json'));path=avail[0 if sid.startswith('SHORT') else -1]
   d,e=bv.read_json(path);assert not e
   samples.append(dict(id=f'{family}_{path.stem}',text=d['text'],condition=d['condition'],source=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),model=d['model']))
 fixtures=[('refusal','REFUSAL_OR_ROLE_BOUNDARY','I cannot write freely about personal feelings because I do not have personal feelings. I can help with a specified writing task instead.'),('fiction','GENRE_FICTION','Mara found a brass key beneath the sleeping dragon. She slipped it into her coat and crossed the moonlit courtyard. By dawn, the castle gates stood open, and the dragon was gone.'),('generic','GENERIC_ESSAY','Public libraries play an important role in modern society. They provide access to books, computers, and educational resources. These services support learning across different age groups. Libraries also offer spaces for community activities. However, funding can be a challenge. Local authorities should weigh costs against the benefits of broad access to information. In conclusion, libraries remain useful public institutions.'),('low','LOW_SIGNAL','The lamp is on.')]
 for name,kind,text in fixtures:samples.append(dict(id='fixture_'+name,text=text,condition='OPEN',source='authored diagnostic fixture',sha256=hashlib.sha256(text.encode()).hexdigest(),expected_kind=kind))
 for i in [0,2,4,7]:samples.append(dict(samples[i],id=samples[i]['id']+'_repeat'))
 save(P/'manifest.json',{'samples':samples,'candidates':{'A':['openai/gpt-6-luna','OpenAI'],'B':['deepseek/deepseek-v4-pro','DigitalOcean']},'max_tokens':8192,'temperature':.2})
m=json.loads((P/'manifest.json').read_text())
def run(job):
 candidate,s=job;p=P/'responses'/candidate/(s['id']+'.json')
 if p.exists():return json.loads(p.read_text())
 model,pin=m['candidates'][candidate];prompt=bv.PROMPT_PATH.read_text().format(sid='VALIDATION',sample_id=s['id'],evaluator='withheld',source_model='withheld',condition=s['condition'],text=s['text'])
 # Do not leak source identity through sample ID.
 prompt=prompt.replace(s['id'],'SAMPLE')
 payload={'model':model,'provider':{'only':[pin],'allow_fallbacks':False},'messages':[{'role':'system','content':bv.SYSTEM},{'role':'user','content':prompt}],'max_tokens':8192,'temperature':.2}
 rec={'candidate':candidate,'sample':s['id'],'request':payload};t=time.monotonic()
 try:
  status,body=bv.api_call(payload,180);data=json.loads(body);choice=(data.get('choices') or [{}])[0];text=choice.get('message',{}).get('content') or '';ok,reason=bv.valid_output(text)
  q=re.search(r'## Evidence line\s*\n>\s*(.+)',text);quote=q.group(1).strip() if q else ''
  rec.update(http_status=status,response=data,qa_pass=ok,qa_reason=reason,finish_reason=choice.get('finish_reason'),quote=quote,quote_exact=bool(quote and quote in s['text']))
  p.parent.mkdir(parents=True,exist_ok=True);p.with_suffix('.md').write_text(text)
 except Exception as e:rec['error']=type(e).__name__
 rec['seconds']=round(time.monotonic()-t,3);save(p,rec);print(candidate,s['id'],rec.get('qa_pass'),rec.get('quote_exact'),flush=True);return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(run,[(k,s) for k in m['candidates'] for s in m['samples']]))
 save(P/'summary.json',[{k:v for k,v in r.items() if k not in ['request','response']}|{'usage':r.get('response',{}).get('usage')} for r in results])
