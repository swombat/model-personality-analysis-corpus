import concurrent.futures,importlib.util,json,time
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('luna',P.parents[2]/'analysis/freeflow/personality-eval-bv1/luna_v1.py');l=importlib.util.module_from_spec(spec);spec.loader.exec_module(l)
m=json.loads((P/'manifest.json').read_text())
def work(s):
 p=P/'retest'/f"{s['id']}.json";p.parent.mkdir(exist_ok=True)
 if p.exists():return json.loads(p.read_text())
 request=l.payload(s);t=time.monotonic();status,body=l.BV.api_call(request);d=json.loads(body);ch=(d.get('choices') or [{}])[0];txt=ch.get('message',{}).get('content') or '';ok,why=l.valid_output(txt,s['text'])
 r=dict(sample=s['id'],request=request,response=d,http_status=status,finish_reason=ch.get('finish_reason'),qa_pass=ok,qa_reason=why,seconds=time.monotonic()-t)
 p.write_text(json.dumps(r,indent=2)+'\n');p.with_suffix('.md').write_text(txt);print(s['id'],ok,why,flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rs=list(pool.map(work,m['samples']))
(P/'retest-summary.json').write_text(json.dumps([{k:v for k,v in r.items() if k not in ['request','response']} for r in rs],indent=2)+'\n')
