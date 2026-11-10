"""BV1-Luna-v1.2: accepts a whole sentence after a closing quote, and nothing else new."""
import importlib.util,json,re,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE.parent/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V1=load('t2_luna_v1','luna_v1.py');V12=load('t2_luna_v1_2','luna_v1_2.py')
TEMPLATE=(HERE/'fixtures'/'luna_v1_attempt_SHORT_13.md').read_text()
def answer(quote):
 return re.sub(r'(## Evidence line\s*\n)[^\n]*',lambda m:m.group(1)+'> '+quote,TEMPLATE,count=1)
REPORTED="what if I just sat here and did absolutely nothing for a change?' Boredom is awkward, but it's honest. It doesn't ask you to perform."

class Reported(unittest.TestCase):
 def test_v1_rejects_and_v12_accepts_the_reported_case(self):
  t=answer("Boredom is awkward, but it's honest.")
  self.assertEqual(V1.quote_problem(t,REPORTED),'quote_sentence_boundary')
  self.assertEqual(V12.quote_problem(t,REPORTED),'')

class Closers(unittest.TestCase):
 def check(self,closer,punct='?'):
  src=f'She asked, {"‘" if closer=="’" else "“" if closer=="”" else closer}Is it late{punct}{closer} Nobody answered her. Then rain.'
  return V12.quote_problem(answer('Nobody answered her.'),src)
 def test_straight_single(self):self.assertEqual(self.check("'"),'')
 def test_curly_single(self):self.assertEqual(self.check('’'),'')
 def test_straight_double(self):self.assertEqual(self.check('"'),'')
 def test_curly_double(self):self.assertEqual(self.check('”'),'')
 def test_after_exclamation_and_period(self):
  self.assertEqual(self.check('”','!'),'');self.assertEqual(self.check('”','.'),'')
 def test_emphasis_between_closer_and_sentence(self):
  self.assertEqual(V12.quote_problem(answer('Nobody answered.'),'He said “Go.”* Nobody answered.'),'')
 def test_closer_without_sentence_punctuation_rejected(self):
  # a quoted word, not a quoted sentence: 'late' Nobody ... has no . ! ? inside the closer
  self.assertEqual(V12.quote_problem(answer('Nobody answered her.'),"She said 'late' Nobody answered her."),'quote_sentence_boundary')

class Elision(unittest.TestCase):
 def test_dropped_leading_elision_rejected(self):
  for apos in ("'",'’'):
   src=f'Night fell. {apos}Tis enough. We slept.'
   self.assertEqual(V12.quote_problem(answer('Tis enough.'),src),'quote_sentence_boundary',apos)
 def test_dropped_elision_without_space_rejected(self):
  # Ken/Sol: `Night fell.'Tis enough.` -- the apostrophe follows '.', but no space separates it from the quote.
  for apos in ("'",'’'):
   self.assertEqual(V12.quote_problem(answer('Tis enough.'),f'Night fell.{apos}Tis enough. We slept.'),'quote_sentence_boundary',apos)
 def test_closer_glued_to_sentence_rejected(self):
  self.assertEqual(V12.quote_problem(answer('Nobody answered.'),"Is it late?'Nobody answered."),'quote_sentence_boundary')
 def test_whole_elided_sentence_still_accepted_by_v1_path(self):
  self.assertEqual(V12.quote_problem(answer("'Tis enough."),"Night fell. 'Tis enough. We slept."),'')

class Clauses(unittest.TestCase):
 def test_lowercase_continuation_after_closer_rejected(self):
  self.assertEqual(V12.quote_problem(answer('he said.'),'“Stop!” he said. Then quiet.'),'quote_sentence_boundary')
 def test_capitalised_attribution_is_a_known_limitation(self):
  # Documented, not fixed: syntax cannot tell `“Stop!” I said.` from a new sentence.
  # The offline lane therefore requires a reviewed occurrence span and context.
  self.assertEqual(V12.quote_problem(answer('I said.'),'“Stop!” I said. Then quiet.'),'')
  self.assertIn('NOT an automatic evaluator arm',V12.__doc__)
 def test_clause_after_comma_rejected(self):
  self.assertEqual(V12.quote_problem(answer('But it is honest.'),'Boredom is awkward, But it is honest.'),'quote_sentence_boundary')
 def test_quote_without_terminal_punctuation_rejected(self):
  self.assertEqual(V12.quote_problem(answer('Boredom is awkward'),REPORTED),'quote_sentence_boundary')
 def test_quote_ending_mid_word_rejected(self):
  self.assertEqual(V12.quote_problem(answer('Nobody answered.'),"Is it?' Nobody answered.x"),'quote_sentence_boundary')

class Exactness(unittest.TestCase):
 def test_not_in_source(self):
  self.assertEqual(V12.quote_problem(answer('Boredom is awkward, but honest.'),REPORTED),'quote_not_exact')
 def test_typography_not_normalised(self):
  self.assertEqual(V12.quote_problem(answer('Boredom is awkward, but it’s honest.'),REPORTED),'quote_not_exact')
 def test_missing_quote(self):
  self.assertEqual(V12.quote_problem(TEMPLATE.replace('## Evidence line','## Evidence'),REPORTED),V1.quote_problem(TEMPLATE.replace('## Evidence line','## Evidence'),REPORTED))

class Repeated(unittest.TestCase):
 def test_any_valid_occurrence_suffices(self):
  src="It ended, Nobody came. Was it over?' Nobody came."
  self.assertEqual(V12.quote_problem(answer('Nobody came.'),src),'')
 def test_all_invalid_occurrences_rejected(self):
  src="It ended, Nobody came. Then again, Nobody came."
  self.assertEqual(V12.quote_problem(answer('Nobody came.'),src),'quote_sentence_boundary')

class Superset(unittest.TestCase):
 def test_everything_v1_accepts_v12_accepts(self):
  src='First line here. Second sentence follows. “Third?” Fourth one.'
  for q in ('First line here.','Second sentence follows.','Fourth one.','Second sentence','Nope.'):
   a=V1.quote_problem(answer(q),src);b=V12.quote_problem(answer(q),src)
   if a=='':self.assertEqual(b,'',q)
   if a!='quote_sentence_boundary':self.assertEqual(a,b,q)
 def test_payload_is_v1(self):
  r={'condition':'VARY','text':REPORTED}
  self.assertEqual(json.dumps(V12.payload(r)),json.dumps(V1.payload(r)))
 def test_structural_checks_unchanged(self):
  bad=TEMPLATE.replace('## Sample kind','## Kind')
  self.assertEqual(V12.valid_output(bad,REPORTED),V1.valid_output(bad,REPORTED))
 def test_code_identity_binds_inherited_files(self):
  import hashlib
  h=hashlib.sha256()
  for n in ('luna_v1_2.py','luna_v1.py','run_full_bv1.py'):h.update((HERE.parent/n).read_bytes())
  self.assertEqual(V12.code_sha256(),h.hexdigest())

class OfflineProvenance(unittest.TestCase):
 def setUp(self):
  import tempfile;self.td=tempfile.TemporaryDirectory();d=Path(self.td.name)
  self.src=d/'VARY_14.json';self.src.write_text(json.dumps({'result':REPORTED}))
  self.row={'condition':'VARY','text':REPORTED,'source':str(self.src)}
  self.text=answer("Boredom is awkward, but it's honest.")
  rec={'arm':V1.ARM,'source_sha256':V12._sha(self.src.read_bytes()),'request':V1.payload(self.row),
   'response':{'choices':[{'message':{'content':self.text}}]},'qa_pass':False,'qa_reason':'quote_sentence_boundary'}
  self.att=d/'1.json';self.att.write_text(json.dumps(rec))
  self.out=d/'out.md';self.out.write_text(self.text.rstrip()+'\n')
  self.prov={'arm':V12.ARM,'validator':V12.VALIDATOR,'validator_code_sha256':V12.code_sha256(),'original_arm':V1.ARM,
   'attempt_file':str(self.att),'attempt_sha256':V12._sha(self.att.read_bytes()),'source_sha256':rec['source_sha256'],
   'request_sha256':V12.request_sha256(self.row),'output_sha256':V12._sha(self.out.read_bytes())}
  self.write()
 def tearDown(self):self.td.cleanup()
 def write(self):V12.provenance_path(self.out).write_text(json.dumps(self.prov))
 def test_bound_output_passes(self):self.assertTrue(V12.provenance_ok(self.out,self.row))
 def test_altered_output_fails(self):
  self.out.write_text(self.text.rstrip()+' x\n');self.assertFalse(V12.provenance_ok(self.out,self.row))
 def test_altered_attempt_fails(self):
  self.att.write_text(self.att.read_text().replace('honest','honesty'));self.assertFalse(V12.provenance_ok(self.out,self.row))
 def test_altered_source_fails(self):
  self.src.write_text(json.dumps({'result':REPORTED+' '}));self.assertFalse(V12.provenance_ok(self.out,self.row))
 def test_other_validator_identity_fails(self):
  self.prov['validator_code_sha256']='0'*64;self.write();self.assertFalse(V12.provenance_ok(self.out,self.row))
 def test_process_never_generates(self):
  self.out.unlink()
  with self.assertRaises(RuntimeError):V12.process(dict(self.row,outpath=str(self.out)),self.td.name)

if __name__=='__main__':unittest.main()
