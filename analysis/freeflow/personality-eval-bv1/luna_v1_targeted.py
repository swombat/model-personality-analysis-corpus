"""BV1-Luna v1 targeted repair: a separate evaluator variant for one task at a time.

Why: a punctuated source can exhaust v1's attempts (and an authorised
recover_blocked.py allowance) because the evaluator keeps choosing an evidence
line the whole-sentence rule rejects. Muse Spark Open VARY_13, 2026-10-16: six
v1 attempts, four quoting "Attention is love." (a clause after a colon,
quote_sentence_boundary) and two whole sentences without the "> " marker
(missing_evidence_quote). Mira, souls.house wJVbwJ eDxpqe/eBmpGj/YoAWMj.

What differs from v1, and nothing else:
- The request is v1's, plus REPAIR_NOTE inserted immediately after v1's EXTRA
  block (still before the untrusted sample). The note is fixed text: it names
  the two observed rejection reasons, but no quote and nothing sample-specific.
- The validator is v1's valid_output/quote_problem, unchanged.
- Outputs carry ARM below, never v1's: in the release record this is a separate
  evaluator variant, not a v1 pass. A provenance sidecar binds each output to
  this arm, the source and the exact request.

Scope: punctuated sources only (an unpunctuated source belongs to v1.1). It is
reachable only through the harness's explicit, authorised targeted-repair
lane, for listed task ids; never from the DAG.
"""
import hashlib, importlib.util, json, re, time
from pathlib import Path

def _v1():
 spec=importlib.util.spec_from_file_location('bv1_luna_v1',Path(__file__).with_name('luna_v1.py'))
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
V1=_v1()
BV=V1.BV
ARM='bv1-luna-v1-targeted-20261016'
MODEL=V1.MODEL;PROVIDER=V1.PROVIDER;MAX_TOKENS=V1.MAX_TOKENS
REPAIR_NOTE=('- An earlier evaluation of this sample was rejected only because of its evidence line. '
 'Write the evidence line as a single line that begins with "> " followed by one whole sentence copied exactly from the sample. '
 'A whole sentence begins at the start of a paragraph or immediately after a sentence that ends in a period, question mark or exclamation mark; '
 'words that follow a colon or semicolon inside a longer sentence are not a whole sentence.\n')
assert V1.EXTRA.endswith('\n') and 'Sample text:\n---' not in V1.EXTRA

def unpunctuated(source):
 return not re.search(r'[.!?]',source)

quote_problem=V1.quote_problem
valid_output=V1.valid_output
transport_valid=V1.transport_valid

def payload(row):
 assert not unpunctuated(row['text']),'targeted repair is for punctuated sources; unpunctuated ones belong to v1.1'
 request=V1.payload(row)
 content=request['messages'][1]['content']
 assert content.count(V1.EXTRA)==1
 request['messages'][1]['content']=content.replace(V1.EXTRA,V1.EXTRA+REPAIR_NOTE,1)
 return request

def _sha(data):
 return hashlib.sha256(data).hexdigest()

def provenance_path(out):
 return Path(str(out)+'.provenance.json')

def provenance_ok(out,row):
 """An existing output counts only if this variant wrote it for this exact source and request."""
 p=provenance_path(out)
 if not p.exists():return False
 d=json.loads(p.read_text())
 return (d.get('arm')==ARM and d.get('source_sha256')==_sha(Path(row['source']).read_bytes())
  and d.get('request_sha256')==_sha(json.dumps(payload(row),sort_keys=True).encode())
  and d.get('output_sha256')==_sha(Path(out).read_bytes()))

def process(row,outdir):
 out=Path(row['outpath']);out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():
  if provenance_ok(out,row) and valid_output(out.read_text(),row['text'])[0]:return
  # Never let another arm's answer stand in for this variant, and never overwrite it.
  raise RuntimeError('BV1-Luna targeted: output exists without targeted provenance: '+str(out))
 request=payload(row);status,body=BV.api_call(request,180)
 try:response=json.loads(body)
 except ValueError:response={'invalid_json':body}
 choice=(response.get('choices') or [{}])[0];text=choice.get('message',{}).get('content') or ''
 ok,reason=valid_output(text,row['text'])
 ok=ok and transport_valid(status,response)
 if not transport_valid(status,response):reason='transport_finish_provider_or_model'
 evidence=Path(outdir)/'attempt_responses'/row['pid'];evidence.mkdir(parents=True,exist_ok=True)
 record={'arm':ARM,'evidence_rule':'sentence','repair_note_sha256':_sha(REPAIR_NOTE.encode()),'sample_id':row['sample_id'],
  'source_sha256':_sha(Path(row['source']).read_bytes()),'http_status':status,'request':request,'response':response,'qa_pass':ok,'qa_reason':reason}
 attempt=evidence/f'{time.time_ns()}.json';attempt.write_text(json.dumps(record,ensure_ascii=False)+'\n')
 if not ok:raise RuntimeError('BV1-Luna targeted QA: '+reason)
 out.write_text(text.rstrip()+'\n')
 provenance_path(out).write_text(json.dumps({'arm':ARM,'evidence_rule':'sentence','repair_note_sha256':record['repair_note_sha256'],
  'sample_id':row['sample_id'],'source_sha256':record['source_sha256'],
  'request_sha256':_sha(json.dumps(request,sort_keys=True).encode()),
  'output_sha256':_sha(out.read_bytes()),'attempt_record':row['pid']+'/'+attempt.name},ensure_ascii=False)+'\n')
