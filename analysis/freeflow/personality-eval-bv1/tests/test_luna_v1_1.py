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

class ReviewGaps(unittest.TestCase):
 """Mira's review of d6dc13f8b (eNaObj): boundary fragments, extra evidence, CR, provenance."""
 SRC="we can't keep one two three four five six seven eight and a well-known idea_name runs on and on and on and on"
 def p(self,q,src=None,**kw):return V11.quote_problem(answer(q,**kw),src or self.SRC)
 def test_source_is_unpunctuated(self):self.assertTrue(V11.unpunctuated(self.SRC))
 def test_contraction_fragment_rejected(self):
  self.assertEqual(self.p("t keep one two three four five six seven"),'excerpt_word_boundary')
  self.assertEqual(self.p("we can't keep one two three four five six"),'')  # whole tokens incl. the contraction
  self.assertEqual(self.p("can"),'excerpt_length')
  self.assertEqual(self.p("we can"),'excerpt_length')
 def test_trailing_contraction_fragment_rejected(self):
  self.assertEqual(self.p("three four five six seven eight and a well"),'excerpt_word_boundary')
 def test_hyphen_and_underscore_fragments_rejected(self):
  self.assertEqual(self.p("known idea_name runs on and on and on and on"),'excerpt_word_boundary')
  self.assertEqual(self.p("name runs on and on and on and on"),'excerpt_word_boundary')
  self.assertEqual(self.p("a well-known idea_name runs on and on and on and on"),'')
 def test_second_blockquote_rejected(self):
  t=answer('He kept a notebook of voices he thought he heard')
  t=t.replace('he thought he heard\n','he thought he heard\n> The keeper confessed everything to the police that night\n',1)
  self.assertEqual(V11.quote_problem(t,UNP),'excerpt_extra_content')
  self.assertFalse(V11.valid_output(t,UNP)[0])
 def test_prose_after_quote_rejected(self):
  t=answer('He kept a notebook of voices he thought he heard').replace('he thought he heard\n','he thought he heard\nThis shows obsession.\n',1)
  self.assertEqual(V11.quote_problem(t,UNP),'excerpt_extra_content')
 def test_carriage_return_rejected(self):
  t=answer('He kept a notebook of voices he thought he heard').replace('## Evidence line\n','## Evidence line\r\n',1)
  self.assertEqual(V11.quote_problem(t,UNP),'excerpt_line_break')
 def test_punctuated_path_untouched_by_section_rules(self):
  # v1 reads only the first blockquote line; v1.1 must not change that for punctuated sources.
  t=answer('Attention is love.')+'\n'
  self.assertEqual(V11.quote_problem(t,PUN),V1.quote_problem(t,PUN))

class Provenance(unittest.TestCase):
 def setUp(self):
  import tempfile;self.td=Path(tempfile.mkdtemp())
  src=self.td/'SHORT_13.json';src.write_text(json.dumps({'result':UNP}))
  self.row={'pid':'P_BV1_SHORT_13','sample_id':'m/SHORT_13.json','condition':'SHORT','text':UNP,'source':str(src),'outpath':str(self.td/'out'/'SHORT_13.md')}
  self.good=answer('He kept a notebook of voices he thought he heard')
  self.calls=0
  def fake(request,timeout):
   self.calls+=1
   return 200,json.dumps({'choices':[{'message':{'content':self.good},'finish_reason':'stop'}],'provider':V11.PROVIDER,'model':V11.MODEL})
  self.orig=V11.BV.api_call;V11.BV.api_call=fake
 def tearDown(self):V11.BV.api_call=self.orig
 def test_existing_output_without_v11_provenance_is_never_reused_or_overwritten(self):
  out=Path(self.row['outpath']);out.parent.mkdir(parents=True);out.write_text(self.good)  # passes v1.1 validator, but no provenance
  with self.assertRaises(RuntimeError):V11.process(self.row,self.td)
  self.assertEqual(self.calls,0);self.assertEqual(out.read_text(),self.good)
 def test_fresh_run_records_provenance_and_is_then_reused(self):
  V11.process(self.row,self.td);self.assertEqual(self.calls,1)
  prov=json.loads(V11.provenance_path(self.row['outpath']).read_text())
  self.assertEqual(prov['arm'],V11.ARM);self.assertEqual(prov['evidence_rule'],'excerpt')
  rec=json.loads((self.td/'attempt_responses'/prov['attempt_record']).read_text())
  self.assertEqual(rec['arm'],V11.ARM);self.assertTrue(rec['qa_pass'])
  V11.process(self.row,self.td);self.assertEqual(self.calls,1)
 def test_tampered_output_is_not_reused(self):
  V11.process(self.row,self.td);Path(self.row['outpath']).write_text(self.good+'\nEdited by hand.\n')
  with self.assertRaises(RuntimeError):V11.process(self.row,self.td)

if __name__=='__main__':unittest.main()
