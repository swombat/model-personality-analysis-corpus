#!/usr/bin/env python3
"""Deterministic offline revalidation of preserved BV1-Luna v1-family attempts under
the v1.2 validator (issue #1). DRY RUN ONLY in this version: reads, hashes and
prints; writes nothing, makes no model calls. An apply mode (separate receipt,
binding, release of the blocked task) is deliberately not built until the dry run
has been reviewed.

For one sample it lists every preserved attempt (v1 arm first, then the targeted
arm, each in time order), re-checks each one, and names the first eligible one:
- transport: HTTP 200, finish_reason stop, provider and model as v1 requires
  (v1's own transport_valid);
- request: byte-identical to what v1's payload() builds from the captured source
  today (so the evaluator really saw this source and v1's prompt);
- source: the attempt's source_sha256 equals the captured source file's sha256;
- structure: v1's valid_output without the quote check;
- quote: v1's verdict (expected quote_sentence_boundary) and v1.2's verdict.

Usage: revalidate_offline.py --capture-dir DIR --source FILE --pid PID --condition C
"""
import argparse, glob, hashlib, importlib.util, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V1=load('r_luna_v1','luna_v1.py');V12=load('r_luna_v1_2','luna_v1_2.py')
ARM_DIRS=[('bv1-luna-v1-20260929','freeflow_bv1_luna_v1'),('bv1-luna-v1-targeted-20261016','freeflow_bv1_luna_v1_targeted')]
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--capture-dir',type=Path,required=True);p.add_argument('--source',type=Path,required=True)
 p.add_argument('--pid',required=True);p.add_argument('--condition',required=True);a=p.parse_args()
 src_bytes=a.source.read_bytes();source=json.loads(src_bytes)['result']
 row={'condition':a.condition,'text':source}
 out={'validator':V12.VALIDATOR,'validator_code_sha256':V12.code_sha256(),'source_file':str(a.source),'source_sha256':sha(src_bytes),'attempts':[],'selected':None,'writes':0,'model_calls':0}
 for arm,d in ARM_DIRS:
  for f in sorted(glob.glob(str(a.capture_dir/d/'attempt_responses'/a.pid/'*.json'))):
   raw=Path(f).read_bytes();r=json.loads(raw)
   resp=r['response'];text=((resp.get('choices') or [{}])[0].get('message',{}).get('content')) or ''
   rec={'arm':r['arm'],'file':f,'attempt_sha256':sha(raw),'response_sha256':sha(json.dumps(resp,sort_keys=True,ensure_ascii=False).encode()),
    'request_sha256':sha(json.dumps(r['request'],sort_keys=True,ensure_ascii=False).encode()),
    'source_bound':r['source_sha256']==out['source_sha256'],'recorded_qa':[r['qa_pass'],r['qa_reason']],
    'transport_ok':V1.transport_valid(int(r['http_status']),resp),'structure':list(V1.valid_output(text)),
    'v1_quote':V1.quote_problem(text,source) if re.search(r'## Evidence line',text) else 'missing',
    'v12_quote':V12.quote_problem(text,source) if re.search(r'## Evidence line',text) else 'missing'}
   # v1.2 only re-judges answers to v1's own request; targeted-arm answers are listed, never selected.
   rec['request_is_v1_payload']=json.dumps(r['request'],sort_keys=True)==json.dumps(V1.payload(row),sort_keys=True)
   m=re.search(r'## Evidence line\s*\n>\s*([^\n]+)',text);rec['quote']=m.group(1).strip() if m else None
   rec['eligible']=bool(rec['arm']=='bv1-luna-v1-20260929' and rec['request_is_v1_payload'] and rec['source_bound'] and rec['transport_ok'] and rec['structure'][0] and rec['v12_quote']=='')
   out['attempts'].append(rec)
   if rec['eligible'] and out['selected'] is None:out['selected']={'arm':rec['arm'],'file':f,'attempt_sha256':rec['attempt_sha256']}
 print(json.dumps(out,indent=1,ensure_ascii=False))

if __name__=='__main__':main()
