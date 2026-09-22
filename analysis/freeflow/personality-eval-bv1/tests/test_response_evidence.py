import importlib.util,json,tempfile,unittest
from pathlib import Path

class ResponseTests(unittest.TestCase):
    def test_null_preserves_finish_metadata_and_fails_qa(self):
        spec=importlib.util.spec_from_file_location('bvfix',Path(__file__).resolve().parents[1]/'run_full_bv1.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as td:
            m.OUT=Path(td);m.build_prompt=lambda _: 'unchanged prompt'
            m.api_call=lambda _: (200,json.dumps({'choices':[{'message':{'content':None},'finish_reason':'length'}],'usage':{'completion_tokens':2200}}))
            row=dict(pid='test',model='m',cell='c',condition='SHORT',sample_id='SHORT_1',word_count=5,outpath=str(m.OUT/'out.md'))
            result=m.process(row,max_attempts=1)
            self.assertEqual(result['status'],'qa_failed');self.assertEqual(result['error'],'short_or_empty')
            evidence=list((m.OUT/'attempt_responses/test').glob('*.json'))
            self.assertEqual(len(evidence),1)
            self.assertEqual(json.loads(evidence[0].read_text())['response']['choices'][0]['finish_reason'],'length')
