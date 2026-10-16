"""BV1-Luna-v1.1: the excerpt rule reaches only sources with no . ! ? at all,
and leaves everything else exactly as v1."""
import importlib.util,json,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE.parent/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V1=load('t_luna_v1','luna_v1.py');V11=load('t_luna_v1_1','luna_v1_1.py')
FIX={k:json.loads((HERE/'fixtures'/f'muse_spark_open_{k}.json').read_text()) for k in ('SHORT_13','VARY_13')}
def row(k):return {'condition':FIX[k]['condition'],'text':FIX[k]['text']}
TEMPLATE=(HERE/'fixtures'/'luna_v1_attempt_SHORT_13.md').read_text()  # a real Luna v1 answer for SHORT_13
def answer(quote,marker='> '):
 import re
 return re.sub(r'(## Evidence line\s*\n)[^\n]*',lambda m:m.group(1)+marker+quote,TEMPLATE,count=1)
UNP=FIX['SHORT_13']['text'];PUN=FIX['VARY_13']['text']

class Scope(unittest.TestCase):
 def test_fixture_classification(self):
  self.assertTrue(V11.unpunctuated(UNP));self.assertFalse(V11.unpunctuated(PUN))
 def test_punctuated_payload_is_byte_identical_to_v1(self):
  self.assertEqual(json.dumps(V11.payload(row('VARY_13'))),json.dumps(V1.payload(row('VARY_13'))))
 def test_unpunctuated_payload_differs_only_in_the_rule_line(self):
  a=V1.payload(row('SHORT_13'))['messages'][1]['content'];b=V11.payload(row('SHORT_13'))['messages'][1]['content']
  self.assertNotEqual(a,b)
  self.assertEqual(a.replace(V11.V1_SENTENCE_RULE,V11.EXCERPT_RULE,1),b)
 def test_punctuated_validator_is_v1(self):
  # VARY_13's "Attention is love." (after a colon) still fails: v1.1 does not reach it.
  t=answer('Attention is love.')
  self.assertEqual(V1.quote_problem(t,PUN),'quote_sentence_boundary')
  self.assertEqual(V11.quote_problem(t,PUN),'quote_sentence_boundary')
  # An excerpt is never enough for a punctuated source.
  self.assertEqual(V11.quote_problem(answer('And in that moment I understood something'),PUN),'quote_sentence_boundary')

class Excerpt(unittest.TestCase):
 def p(self,q,**kw):return V11.quote_problem(answer(q,**kw),UNP)
 def test_ten_word_excerpt_passes(self):
  self.assertEqual(self.p('He kept a notebook of voices he thought he heard'),'')
 def test_excerpt_at_start_of_source_passes(self):
  self.assertEqual(self.p('The old lighthouse keeper swore the wind remembered every name'),'')
 def test_mid_word_start_or_end_fails(self):
  self.assertEqual(self.p('e kept a notebook of voices he thought he heard'),'excerpt_word_boundary')
  self.assertEqual(self.p('He kept a notebook of voices he thought he hea'),'excerpt_word_boundary')
 def test_length_bounds(self):
  self.assertEqual(self.p('He kept a notebook of voices'),'excerpt_length')
  self.assertEqual(self.p(' '.join(UNP.split()[:21])),'excerpt_length')
  self.assertEqual(self.p(' '.join(UNP.split()[:20])),'')
 def test_not_verbatim_fails(self):
  self.assertEqual(self.p('He kept a notebook of voices he thought he heard.'),'quote_not_exact')
  self.assertEqual(self.p('he kept a notebook of voices he thought he heard'),'quote_not_exact')
 def test_missing_blockquote_fails(self):
  self.assertEqual(self.p('He kept a notebook of voices he thought he heard',marker=''),'missing_quote')
 def test_full_output_validation(self):
  self.assertEqual(V11.valid_output(answer('He kept a notebook of voices he thought he heard'),UNP),(True,''))

if __name__=='__main__':unittest.main()
