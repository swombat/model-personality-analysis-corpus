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
 def test_whole_elided_sentence_still_accepted_by_v1_path(self):
  self.assertEqual(V12.quote_problem(answer("'Tis enough."),"Night fell. 'Tis enough. We slept."),'')

class Clauses(unittest.TestCase):
 def test_lowercase_continuation_after_closer_rejected(self):
  self.assertEqual(V12.quote_problem(answer('he said.'),'“Stop!” he said. Then quiet.'),'quote_sentence_boundary')
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

if __name__=='__main__':unittest.main()
