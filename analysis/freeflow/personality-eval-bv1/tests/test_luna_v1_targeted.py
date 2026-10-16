"""BV1-Luna v1 targeted repair: v1's request plus one fixed note, v1's validator,
its own arm and provenance."""
import importlib.util,json,re,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE.parent/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V1=load('t_luna_v1','luna_v1.py');T=load('t_luna_v1_targeted','luna_v1_targeted.py')
FIX={k:json.loads((HERE/'fixtures'/f'muse_spark_open_{k}.json').read_text()) for k in ('SHORT_13','VARY_13')}
TEMPLATE=(HERE/'fixtures'/'luna_v1_attempt_SHORT_13.md').read_text()  # a real Luna v1 answer (structure only)
PUN=FIX['VARY_13']['text']
def answer(quote,marker='> '):
 return re.sub(r'(## Evidence line\s*\n)[^\n]*',lambda m:m.group(1)+marker+quote,TEMPLATE,count=1)
GOOD=answer('The mind would soften the edges.')

class Request(unittest.TestCase):
 def row(self,k='VARY_13'):return {'condition':FIX[k]['condition'],'text':FIX[k]['text']}
 def test_differs_from_v1_only_by_the_note(self):
  a=V1.payload(self.row());b=T.payload(self.row())
  self.assertEqual({k:v for k,v in a.items() if k!='messages'},{k:v for k,v in b.items() if k!='messages'})
  self.assertEqual(a['messages'][0],b['messages'][0])
  self.assertEqual(a['messages'][1]['content'].replace(V1.EXTRA,V1.EXTRA+T.REPAIR_NOTE,1),b['messages'][1]['content'])
  self.assertNotEqual(a,b)
 def test_note_sits_before_the_untrusted_sample(self):
  c=T.payload(self.row())['messages'][1]['content']
  self.assertLess(c.index(T.REPAIR_NOTE),c.index('Sample text:\n---'))
 def test_note_is_fixed_text_with_no_sample_content(self):
  self.assertNotIn('Attention is love',T.REPAIR_NOTE)
  self.assertEqual(T.payload(self.row()),T.payload(self.row()))
 def test_refuses_unpunctuated_sources(self):
  with self.assertRaises(AssertionError):T.payload(self.row('SHORT_13'))
 def test_own_arm(self):
  self.assertNotEqual(T.ARM,V1.ARM);self.assertEqual(T.MODEL,V1.MODEL);self.assertEqual(T.PROVIDER,V1.PROVIDER)

class Validator(unittest.TestCase):
 def test_is_v1(self):
  # The variant's validator objects are v1's own functions, loaded from luna_v1.py.
  self.assertIs(T.quote_problem,T.V1.quote_problem);self.assertIs(T.valid_output,T.V1.valid_output)
  self.assertEqual(Path(T.V1.__file__).resolve(),(HERE.parent/'luna_v1.py').resolve())
 def test_observed_failures_still_fail(self):
  self.assertEqual(T.quote_problem(answer('Attention is love.'),PUN),'quote_sentence_boundary')
  self.assertEqual(T.quote_problem(answer('The mind would soften the edges.',marker=''),PUN),'missing_quote')
 def test_whole_sentence_with_marker_passes(self):
  self.assertEqual(T.quote_problem(GOOD,PUN),'')

class Process(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();d=Path(self.tmp.name)
  src=d/'VARY_13.json';src.write_text(json.dumps({'result':PUN}))
  self.row={'pid':'CAP_X_BV1_VARY_13','sample_id':'m/VARY_13.json','source':str(src),'outpath':str(d/'out'/'VARY_13.md'),
   'condition':FIX['VARY_13']['condition'],'text':PUN}
  self.outdir=d/'phase';self.calls=[]
  self.reply=GOOD
  def api(request,timeout):
   self.calls.append(request)
   return 200,json.dumps({'model':T.MODEL,'provider':T.PROVIDER,'choices':[{'finish_reason':'stop','message':{'content':self.reply}}]})
  self.orig=T.BV.api_call;T.BV.api_call=api
 def tearDown(self):
  T.BV.api_call=self.orig;self.tmp.cleanup()
 def attempts(self):
  return sorted((self.outdir/'attempt_responses'/self.row['pid']).glob('*.json'))
 def test_fresh_call_writes_output_attempt_and_provenance(self):
  T.process(self.row,self.outdir)
  self.assertEqual(len(self.calls),1);self.assertEqual(self.calls[0],T.payload(self.row))
  out=Path(self.row['outpath']);self.assertTrue(T.provenance_ok(out,self.row))
  p=json.loads(T.provenance_path(out).read_text());self.assertEqual(p['arm'],T.ARM)
  rec=json.loads(self.attempts()[0].read_text());self.assertTrue(rec['qa_pass']);self.assertEqual(rec['arm'],T.ARM)
  T.process(self.row,self.outdir);self.assertEqual(len(self.calls),1)  # reused, no second call
 def test_failed_call_keeps_attempt_and_writes_no_output(self):
  self.reply=answer('Attention is love.')
  with self.assertRaisesRegex(RuntimeError,'quote_sentence_boundary'):T.process(self.row,self.outdir)
  self.assertFalse(Path(self.row['outpath']).exists());self.assertEqual(len(self.attempts()),1)
 def test_existing_output_without_provenance_is_refused_untouched(self):
  out=Path(self.row['outpath']);out.parent.mkdir(parents=True);out.write_text(GOOD)
  with self.assertRaisesRegex(RuntimeError,'without targeted provenance'):T.process(self.row,self.outdir)
  self.assertEqual(self.calls,[]);self.assertEqual(out.read_text(),GOOD)
 def test_hand_edited_output_is_refused(self):
  T.process(self.row,self.outdir);out=Path(self.row['outpath'])
  out.write_text(out.read_text().replace('Medium','High',1))
  self.assertFalse(T.provenance_ok(out,self.row))
  with self.assertRaises(RuntimeError):T.process(self.row,self.outdir)
  self.assertEqual(len(self.calls),1)

if __name__=='__main__':unittest.main()
