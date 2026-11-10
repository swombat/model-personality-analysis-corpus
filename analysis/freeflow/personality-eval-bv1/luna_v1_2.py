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
  an occurrence of the exact quote when (a) the text before it, ignoring
  whitespace and emphasis, ends in one or more closing quotes (' ’ " ”)
  immediately preceded by . ! or ?; (b) the quote starts with an uppercase letter
  (so `"Stop!" he said.` stays a clause); (c) v1's own terminal-punctuation and
  after-boundary checks hold for that occurrence.
- A leading elision apostrophe is not a closer: `Tis enough.` quoted from
  `'Tis enough.` is still rejected, because no sentence punctuation precedes the
  apostrophe (Jerry/Sol counterexample, Mira 2026-11-10).
"""
import hashlib, importlib.util, re
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
 """Identity of the exact validator code (this file plus the v1 file it extends)."""
 h=hashlib.sha256()
 for name in ('luna_v1_2.py','luna_v1.py'):h.update(Path(__file__).with_name(name).read_bytes())
 return h.hexdigest()

def _closed_quote_start(source,quote):
 if not quote[:1].isupper():return False
 terminal=bool(re.search(r'[.!?][\"”’\'*_]*$',quote))  # v1's terminal rule, verbatim
 if not terminal:return False
 for match in re.finditer(re.escape(quote),source):
  left=source[:match.start()];right=source[match.end():]
  before=left.rstrip(' \t\r\n*_')
  after_ok=not right or right[0].isspace() or right[0] in '\"”’\'*_'  # v1's after rule, verbatim
  if before and _AFTER_CLOSER.search(before) and after_ok:return True
 return False

def quote_problem(text,source):
 problem=V1.quote_problem(text,source)
 if problem!='quote_sentence_boundary':return problem
 quote=re.search(r'## Evidence line\s*\n>\s*([^\n]+)',text).group(1).strip()
 return '' if _closed_quote_start(source,quote) else problem

def valid_output(text,source=None):
 ok,reason=V1.valid_output(text)  # every structural check of v1, no quote check
 if not ok or source is None:return ok,reason
 problem=quote_problem(text,source)
 return (False,problem) if problem else (True,'')
