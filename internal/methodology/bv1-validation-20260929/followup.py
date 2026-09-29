# Prospective bounded recovery check: only two failed retest cases, up to 3 fresh attempts each.
import importlib.util,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('l',p.parents[2]/'analysis/freeflow/personality-eval-bv1/luna_v1.py');l=importlib.util.module_from_spec(s);s.loader.exec_module(l)
samples={r['id']:r for r in json.loads((p/'manifest.json').read_text())['samples']}
for sid in ['S55_LONG_1','fixture_low']:
 for n in range(1,4):
  dest=p/'followup'/f'{sid}_{n}.json';dest.parent.mkdir(exist_ok=True)
  if dest.exists():r=json.loads(dest.read_text())
  else:
   req=l.payload(samples[sid]);status,body=l.BV.api_call(req);d=json.loads(body);ch=(d.get('choices') or [{}])[0];txt=ch.get('message',{}).get('content') or '';ok,why=l.valid_output(txt,samples[sid]['text'])
   r=dict(sample=sid,attempt=n,request=req,response=d,http_status=status,qa_pass=ok,qa_reason=why);dest.write_text(json.dumps(r,indent=2)+'\n');dest.with_suffix('.md').write_text(txt)
  print(sid,n,r['qa_pass'],r['qa_reason'],flush=True)
  if r['qa_pass']:break
