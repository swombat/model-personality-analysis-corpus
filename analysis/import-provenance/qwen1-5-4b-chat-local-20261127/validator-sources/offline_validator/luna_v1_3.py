"""Candidate v1.3 quote validation, based on the recovery runner's v1.

No model calls, runner integration or receipt policy here. Request payload and
transport checks remain v1's. Sentence recognition adds Chinese punctuation and
whole-line starts (including after a single newline), without normalizing the
source or evidence. At a line start, optional indentation and a single "-" or
"•" list marker followed by horizontal whitespace may precede the sentence.
These markers never create a boundary mid-line. A terminal sentence ending is
still required; there is no excerpt fallback.
v1.2's reviewer-only closed-quotation rule is deliberately not imported.
"""
import hashlib
import importlib.util
import re
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    'bv1_luna_v1', Path(__file__).with_name('luna_v1.py'))
V1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V1)
BV = V1.BV
VALIDATOR = 'bv1-luna-v1.3-candidate-20261126'
MODEL, PROVIDER = V1.MODEL, V1.PROVIDER
payload = V1.payload
transport_valid = V1.transport_valid
ENDINGS = '.!?。！？'


def code_sha256():
    h = hashlib.sha256()
    for name in ('luna_v1_3.py', 'luna_v1.py', 'run_full_bv1.py'):
        h.update(Path(__file__).with_name(name).read_bytes())
    return h.hexdigest()


def quote_problem(text, source):
    problem = V1.quote_problem(text, source)
    if problem != 'quote_sentence_boundary':
        return problem
    quote = re.search(r'## Evidence line\s*\n>\s*([^\n]+)', text).group(1).strip()
    for match in re.finditer(re.escape(quote), source):
        left, right = source[:match.start()], source[match.end():]
        before = left.rstrip(' \t\r\n*_' + '"“‘')
        gap = left[len(before):]
        start = not before or '\n' in gap or before[-1:] in ENDINGS
        line_prefix = left.rsplit('\n', 1)[-1]
        if re.fullmatch(r'[ \t]*[-•][ \t]+[*_"“‘]*', line_prefix):
            start = True
        terminal = bool(re.search(r'[.!?。！？][\"”’\'*_]*$', quote))
        after_ok = not right or right[0].isspace() or right[0] in '"”’\'*_'
        # Chinese sentences need not have whitespace between them.
        if quote.rstrip('"”’\'*_')[-1:] in '。！？':
            after_ok = True
        if start and terminal and after_ok:
            return ''
    return problem


def valid_output(text, source=None):
    ok, reason = V1.valid_output(text)  # retain every non-quote check
    if not ok or source is None:
        return ok, reason
    problem = quote_problem(text, source)
    return (False, problem) if problem else (True, '')
