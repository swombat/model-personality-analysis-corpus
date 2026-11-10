"""BV1-Luna-v1.2 validator: v1 plus one accepting path for a sentence that follows
a closing quotation mark.

Why (issue #1, Muse Ember VARY_14, 2026-11-10): v1's sentence-start check strips
whitespace, emphasis and *opening* quotes from the text before the quote, then
asks whether the previous character is . ! or ?. A sentence that follows a quoted
question or exclamation (`...for a change?' Boredom is awkward, but it's honest.`)
ends that preceding text in a *closing* quote, so it can never be quoted. Right
double quote has the same gap.

Scope, deliberately narrow:
- Validator only. The request payload is v1's, byte-identical; no new model calls
  are implied by this version. Its use is deterministic offline revalidation of a
  preserved v1-family response, recorded in its own receipt.
- Everything v1 accepts, v1.2 accepts; v1's code is not copied or changed.
- The one new path is tried only when v1 says `quote_sentence_boundary`. It accepts
  an occurrence of the exact quote when (a) the text before it, ignoring emphasis,
  ends in one or more closing quotes (' ’ " ”) immediately preceded by . ! or ?;
  (b) at least one whitespace character separates those closing marks from the
  quote; (c) the quote starts with an uppercase letter; (d) v1's own
  terminal-punctuation and after-boundary checks hold for that occurrence.
- A leading elision apostrophe is not a closer: `Tis enough.` quoted from
  `'Tis enough.` is still rejected, with or without a space before the apostrophe
  (Jerry and Ken, Sol reviewers via Mira, 2026-11-10).

Known limitation, by design: this is syntax, not grammar. Attribution after a
quoted exclamation (`"Stop!" I said.`, `"Run!" Alice shouted.`) passes the new
path, because a capitalised word after a closed quote cannot be told apart from
a new sentence without parsing. So v1.2 is NOT an automatic evaluator arm. It is
used only through an explicit offline lane where a reviewer has read the selected
occurrence span and its surrounding context and confirmed it is a full sentence;
that review, not capitalisation, is the authorization. Sample-scoped.
"""
import hashlib, importlib.util, json, re
from pathlib import Path

def _v1():
 spec=importlib.util.spec_from_file_location('bv1_luna_v1',Path(__file__).with_name('luna_v1.py'))
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
V1=_v1()
BV=V1.BV
VALIDATOR='bv1-luna-v1.2-validator-20261110'
MODEL=V1.MODEL;PROVIDER=V1.PROVIDER
payload=V1.payload  # unchanged request; v1.2 changes acceptance only
CLOSERS='\'"’”'
_AFTER_CLOSER=re.compile(r'[.!?][%s]+$'%re.escape(CLOSERS))

def code_sha256():
 """Identity of the exact validator code: this file, the v1 file it extends and
 the legacy run_full_bv1.py whose structural checks v1 inherits."""
 h=hashlib.sha256()
 for name in ('luna_v1_2.py','luna_v1.py','run_full_bv1.py'):h.update(Path(__file__).with_name(name).read_bytes())
 return h.hexdigest()

def closed_quote_starts(source,quote):
 """Start offsets of the occurrences the new path accepts (empty if none)."""
 if not quote[:1].isupper():return []
 terminal=bool(re.search(r'[.!?][\"”’\'*_]*$',quote))  # v1's terminal rule, verbatim
 if not terminal:return []
 hits=[]
 for match in re.finditer(re.escape(quote),source):
  left=source[:match.start()];right=source[match.end():]
  before=left.rstrip(' \t\r\n*_');gap=left[len(before):]
  after_ok=not right or right[0].isspace() or right[0] in '\"”’\'*_'  # v1's after rule, verbatim
  if before and _AFTER_CLOSER.search(before) and any(ch.isspace() for ch in gap) and after_ok:hits.append(match.start())
 return hits

def quote_problem(text,source):
 problem=V1.quote_problem(text,source)
 if problem!='quote_sentence_boundary':return problem
 quote=re.search(r'## Evidence line\s*\n>\s*([^\n]+)',text).group(1).strip()
 return '' if closed_quote_starts(source,quote) else problem

def valid_output(text,source=None):
 ok,reason=V1.valid_output(text)  # every structural check of v1, no quote check
 if not ok or source is None:return ok,reason
 problem=quote_problem(text,source)
 return (False,problem) if problem else (True,'')

# --- Offline lane identity (harness arm). This arm never calls a model: its only
# outputs are preserved v1 answers re-judged by this validator, each with a
# provenance sidecar binding the original attempt.
ARM='bv1-luna-v1.2-offline-20261110'
def _sha(b):return hashlib.sha256(b).hexdigest()
def provenance_path(out):return Path(str(out)+'.provenance.json')
def request_sha256(row):return _sha(json.dumps(V1.payload(row),sort_keys=True).encode())
def attempt_text(record):
 return (((record.get('response') or {}).get('choices') or [{}])[0].get('message',{}).get('content')) or ''
def provenance_ok(out,row):
 """The output counts only if it is, byte for byte, a bound preserved v1 answer
 to this exact source and v1 request, re-judged by this exact validator code."""
 p=provenance_path(out)
 if not p.exists() or not Path(out).exists():return False
 d=json.loads(p.read_text());a=Path(d.get('attempt_file',''))
 if not a.exists() or _sha(a.read_bytes())!=d.get('attempt_sha256'):return False
 rec=json.loads(a.read_text())
 return (d.get('arm')==ARM and d.get('validator')==VALIDATOR and d.get('validator_code_sha256')==code_sha256()
  and rec.get('arm')==V1.ARM and d.get('original_arm')==V1.ARM
  and d.get('source_sha256')==_sha(Path(row['source']).read_bytes())==rec.get('source_sha256')
  and d.get('request_sha256')==request_sha256(row)==_sha(json.dumps(rec.get('request'),sort_keys=True).encode())
  and d.get('output_sha256')==_sha(Path(out).read_bytes())
  and Path(out).read_text()==attempt_text(rec).rstrip()+'\n')
def process(row,outdir):
 out=Path(row['outpath'])
 if out.exists() and provenance_ok(out,row) and valid_output(out.read_text(),row['text'])[0]:return
 raise RuntimeError('BV1-Luna v1.2 offline: never generates; output must come from apply_bv1_offline.py: '+str(out))
transport_valid=V1.transport_valid
ORIGINAL_ARM=V1.ARM
