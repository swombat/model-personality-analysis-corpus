"""Read-only replay inventory. Never writes a binding, edits a response or runs a job."""
from pathlib import Path
import hashlib, importlib.util, json, sqlite3, sys

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True

def module(p):
    spec = importlib.util.spec_from_file_location(p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def replay(check, include_setup_originals=False):
    for lane in sorted(ROOT.glob("remaining_recovery_*/")):
        db = sqlite3.connect(f"file:{lane}/state.sqlite?mode=ro", uri=True)
        with db:
            rows = db.execute("""select j.id, t.used,t.allowance from jobs j
                join targeted_repairs t on j.id=t.id where j.state='blocked'
                and t.used=t.allowance order by j.id""").fetchall()
        db.close()
        if not rows: continue
        base = lane / 'analysis/analysis/freeflow/personality-eval-bv1'
        for job, used, allowance in rows:
            model, stage, sid = job.split('/')
            assert stage == "bv1"
            src = ROOT / f"raw/data/traces_freeflow/freeflow_{model}/{sid}.json"
            sample = json.loads(src.read_bytes())
            source = sample["result"]
            row = dict(text=source, condition=sample["condition"])
            targeted_dir = lane / 'phase/freeflow_bv1_luna_v1_targeted/attempt_responses'
            arms = ('luna_v1','luna_v1_targeted')
            if len(list(targeted_dir.glob(f'*_BV1_{sid}/*.json'))) != used:
                yield dict(job=job, candidate="manual_review_targeted_receipt_count")
                if not include_setup_originals: continue
                arms = ('luna_v1',)
            for arm in arms:
                m = module(base / (arm+'.py'))
                if not m.BV.PROMPT_PATH.exists():
                    m.BV.PROMPT_PATH = ROOT / 'analysis-worktree' / m.BV.PROMPT_PATH.relative_to(lane/'analysis')
                attempts = sorted((lane / 'phase' / ('freeflow_bv1_'+arm) / 'attempt_responses').glob(f'*_BV1_{sid}/*.json'))
                if arm.endswith('targeted'): assert len(attempts)==used
                for p in attempts:
                    a = json.loads(p.read_bytes())
                    assert (a['arm'], a['source_sha256'], a['sample_id'], a['request']) == (
                        m.ARM, sha(src), model+'/'+sid+'.json', m.payload(row))
                    text = a['response']['choices'][0]['message']['content']
                    transport = m.transport_valid(a['http_status'],a['response'])
                    ok,why = m.valid_output(text,source)
                    if not transport: ok,why=False,'transport_finish_provider_or_model'
                    assert (ok,why)==(a['qa_pass'],a['qa_reason'])
                    yield dict(job=job, attempt=p.name, arm=m.ARM, sha256=sha(p),
                               source_sha256=sha(src), old=why,
                               candidate=check(text,source,used,allowance) if transport else why)

if __name__ == '__main__':
    for r in replay(lambda *_:'not_checked'):
        print(json.dumps(r))
