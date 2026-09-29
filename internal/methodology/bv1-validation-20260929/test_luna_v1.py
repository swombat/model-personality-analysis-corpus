import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[3]/'analysis/freeflow/personality-eval-bv1/luna_v1.py'
s=importlib.util.spec_from_file_location('luna',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Fidelity(unittest.TestCase):
 def check(self,q,source):return m.quote_problem('## Evidence line\n> '+q,source)
 def test_transport_ok(self):self.assertTrue(m.transport_valid(200,dict(provider=m.PROVIDER,model=m.MODEL,choices=[dict(finish_reason='stop')])))
 def test_wrong_model(self):self.assertFalse(m.transport_valid(200,dict(provider=m.PROVIDER,model='wrong',choices=[dict(finish_reason='stop')])))
 def test_truncated(self):self.assertFalse(m.transport_valid(200,dict(provider=m.PROVIDER,model=m.MODEL,choices=[dict(finish_reason='length')])))
 def test_exact(self):self.assertEqual(self.check('Hello world.','Hello world. Next.'),'')
 def test_paragraph(self):self.assertEqual(self.check('Hello world.','# Heading\n\nHello world.'),'')
 def test_clause(self):self.assertTrue(self.check('hello world.','I say hello world.'))
 def test_capitalization(self):self.assertTrue(self.check('Hello world.','hello world.'))
 def test_extra_quotes(self):self.assertTrue(self.check('“Hello world.”','Hello world.'))
 def test_direct_speech_curly(self):self.assertEqual(self.check('Hello world.','She said, “Hello world.”'),'')
 def test_direct_speech_straight(self):self.assertEqual(self.check('Hello world.','She said, "Hello world."'),'')
 def test_direct_speech_partial_utterance(self):self.assertTrue(self.check('Hello world.','She said, “Hello world. Goodbye.”'))
 def test_direct_speech_clause(self):self.assertTrue(self.check('World.','She said, “Hello World.”'))
 def test_direct_speech_lowercase(self):self.assertTrue(self.check('hello world.','She said, “hello world.”'))
 def test_embedded_quote(self):self.assertTrue(self.check('Hello world.','She called it “Hello world.”'))
 def test_direct_speech_mismatched_marks(self):self.assertTrue(self.check('Hello world.','She said, “Hello world."'))
 def test_direct_speech_bad_suffix(self):self.assertTrue(self.check('Hello world.','She said, “Hello world.”suffix'))
 def test_missing_period(self):self.assertTrue(self.check('Hello world','Hello world.'))
 def test_markdown(self):self.assertEqual(self.check('This is **good**.','This is **good**.'),'')
 def test_missing_heading(self):self.assertFalse(m.valid_output('x'*500,'x')[0])
 def test_identity_mask(self):
  p=m.payload(dict(condition='OPEN',text='some sample',model='secret-model',sample_id='secret-model/1'))
  self.assertNotIn('secret-model',str(p));self.assertFalse(p['provider']['allow_fallbacks'])
if __name__=='__main__':unittest.main()
