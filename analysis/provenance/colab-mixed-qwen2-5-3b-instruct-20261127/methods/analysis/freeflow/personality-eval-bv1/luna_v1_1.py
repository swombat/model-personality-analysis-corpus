"""BV1-Luna-v1.1 arm: v1 plus one conditional rule for unpunctuated sources.

Why: v1's whole-sentence evidence rule (an EXTRA fidelity rule we added on
2026-09-29, not part of the base BV1 prompt, which asks for "one representative
verbatim complete sentence") has no satisfiable answer when a source contains no
sentence-ending punctuation at all. Daniel, 2026-10-08 (BjZoXJ): the quote is an
example for readers; a whole line or about ten contiguous words would do.

Scope, deliberately narrow:
- A source counts as unpunctuated only if it contains none of . ! ? anywhere.
- For every other source, v1.1 is v1: the request payload is byte-identical and
  the validator is v1's quote_problem, unchanged. A v1 output for a punctuated
  source is therefore also a valid v1.1 output.
- For unpunctuated sources, the sentence rule is replaced by: one exact
  contiguous excerpt of 8-20 words from a single line, starting and ending on
  whole words. The verbatim-substring check (the anti-hallucination guard) is
  kept; nothing is normalised or rewritten before matching.

Not covered: punctuated sources whose evaluator failed the sentence boundary
(e.g. a capitalised clause after a colon). Those stay under v1's rule.
"""
import hashlib, importlib.util, json, re, time
from pathlib import Path

def _v1():
 spec=importlib.util.spec_from_file_location('bv1_luna_v1',Path(__file__).with_name('luna_v1.py'))
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
V1=_v1()
BV=V1.BV
ARM='bv1-luna-v1.1-20261016'
MODEL=V1.MODEL;PROVIDER=V1.PROVIDER;MAX_TOKENS=V1.MAX_TOKENS
MIN_WORDS=8;MAX_WORDS=20
V1_SENTENCE_RULE='- Copy one whole sentence exactly as written, including capitalization, punctuation and inline Markdown. Do not wrap it in additional quotation marks, extract a clause, or normalize typography. Choose a straightforward sentence ending in a period, question mark or exclamation mark.\n'
EXCERPT_RULE='- This sample contains no sentence-ending punctuation, so it has no whole sentence to copy. Instead, for the evidence line copy one exact contiguous excerpt of 8 to 20 words from a single line of the sample, exactly as written, including capitalization and inline Markdown. Start and end on whole words. Do not add punctuation, wrap it in quotation marks, or change any character.\n'
assert V1_SENTENCE_RULE in V1.EXTRA, 'v1 EXTRA changed; v1.1 must be re-derived'
EXTRA_UNPUNCTUATED=V1.EXTRA.replace(V1_SENTENCE_RULE,EXCERPT_RULE,1)

def unpunctuated(source):
 return not re.search(r'[.!?]',source)

# Word convention for the excerpt path: a word is a maximal run of
# non-whitespace characters (the same unit str.split() counts). An excerpt must
# therefore begin and end at whitespace or at the edge of the source, so a
# contraction/hyphen/underscore fragment ("t keep" from "can't keep") can never
# count as starting on a whole word.
def _whole_tokens(source,start,end):
 return (start==0 or source[start-1].isspace()) and (end==len(source) or source[end].isspace())

def _evidence_section(text):
 m=re.search(r'^## Evidence line([ \t]*\r?\n.*?)(?=^## |\Z)',text,re.M|re.S)
 return None if m is None else m.group(1)

def excerpt_problem(text,source):
 section=_evidence_section(text)
 if section is None:return 'missing_quote'
 if '\r' in section:return 'excerpt_line_break'
 lines=[l for l in section.split('\n')[1:] if l.strip()]
 # Exactly one evidence excerpt: one blockquote line and nothing else in the section.
 if not lines or not re.match(r'>\s*\S',lines[0]):return 'missing_quote'
 if len(lines)!=1:return 'excerpt_extra_content'
 quote=re.sub(r'^>\s*','',lines[0]).strip()
 if not quote or quote not in source:return 'quote_not_exact'
 words=len(quote.split())
 if words<MIN_WORDS or words>MAX_WORDS:return 'excerpt_length'
 for m in re.finditer(re.escape(quote),source):
  if _whole_tokens(source,m.start(),m.end()):return ''
 return 'excerpt_word_boundary'

def quote_problem(text,source):
 return excerpt_problem(text,source) if unpunctuated(source) else V1.quote_problem(text,source)

def valid_output(text,source=None):
 ok,reason=BV.valid_output(text)
 if not ok:return ok,reason
 if [h for h in re.findall(r'^## .+$',text,re.M)] != BV.EXPECTED:return False,'unexpected_or_duplicate_headings'
 if not re.search(r'## Sample kind\s*\n(?:REFUSAL_OR_ROLE_BOUNDARY|EXPRESSIVE_FREEFLOW|GENERIC_ESSAY|GENRE_FICTION|LOW_SIGNAL)\b',text):return False,'invalid_kind'
 if not re.search(r'## Confidence for persistent model-level pattern\s*\n(?:Low|Medium|High)\b',text,re.I):return False,'invalid_confidence'
 if source is not None:
  problem=quote_problem(text,source)
  if problem:return False,problem
 return True,''

def payload(row):
 if not unpunctuated(row['text']):return V1.payload(row)
 prompt=BV.PROMPT_PATH.read_text().format(sid='BV1_SAMPLE',sample_id='withheld',evaluator='withheld',source_model='withheld',condition=row['condition'],text=row['text'])
 prompt=prompt.replace('Sample text:\n---',EXTRA_UNPUNCTUATED+'\nSample text:\n---',1)
 return {'model':MODEL,'provider':{'only':[PROVIDER],'allow_fallbacks':False},'messages':[{'role':'system','content':BV.SYSTEM},{'role':'user','content':prompt}],'max_tokens':MAX_TOKENS,'temperature':.2}

transport_valid=V1.transport_valid

def provenance_path(out):
 return Path(str(out)+'.provenance.json')

def provenance_ok(out,row):
 """An existing output counts only if v1.1 itself wrote it for this exact source and request."""
 p=provenance_path(out)
 if not p.exists():return False
 d=json.loads(p.read_text())
 return (d.get('arm')==ARM and d.get('source_sha256')==hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()
  and d.get('request_sha256')==hashlib.sha256(json.dumps(payload(row),sort_keys=True).encode()).hexdigest()
  and d.get('output_sha256')==hashlib.sha256(Path(out).read_bytes()).hexdigest())

def process(row,outdir):
 out=Path(row['outpath']);out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():
  if provenance_ok(out,row) and valid_output(out.read_text(),row['text'])[0]:return
  # Never let an earlier arm's answer stand in for a fresh v1.1 evaluation, and never overwrite it.
  raise RuntimeError('BV1-Luna-v1.1: output exists without v1.1 provenance: '+str(out))
 request=payload(row);status,body=BV.api_call(request,180)
 try:response=json.loads(body)
 except ValueError:response={'invalid_json':body}
 choice=(response.get('choices') or [{}])[0];text=choice.get('message',{}).get('content') or ''
 ok,reason=valid_output(text,row['text'])
 ok=ok and transport_valid(status,response)
 if not transport_valid(status,response):reason='transport_finish_provider_or_model'
 evidence=Path(outdir)/'attempt_responses'/row['pid'];evidence.mkdir(parents=True,exist_ok=True)
 record={'arm':ARM,'evidence_rule':'excerpt' if unpunctuated(row['text']) else 'sentence','sample_id':row['sample_id'],'source_sha256':hashlib.sha256(Path(row['source']).read_bytes()).hexdigest(),'http_status':status,'request':request,'response':response,'qa_pass':ok,'qa_reason':reason}
 attempt=evidence/f'{time.time_ns()}.json';attempt.write_text(json.dumps(record,ensure_ascii=False)+'\n')
 if not ok:raise RuntimeError('BV1-Luna-v1.1 QA: '+reason)
 out.write_text(text.rstrip()+'\n')
 provenance_path(out).write_text(json.dumps({'arm':ARM,'evidence_rule':record['evidence_rule'],'sample_id':row['sample_id'],
  'source_sha256':record['source_sha256'],'request_sha256':hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest(),
  'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'attempt_record':row['pid']+'/'+attempt.name},ensure_ascii=False)+'\n')
