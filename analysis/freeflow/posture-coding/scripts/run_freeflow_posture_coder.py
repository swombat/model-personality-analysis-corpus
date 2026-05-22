#!/usr/bin/env python3
import argparse, concurrent.futures, datetime as dt, json, os, re, time
from pathlib import Path
import httpx

CODERS = {
    'qwen3-6-35b-a3b': 'qwen/qwen3.6-35b-a3b',
    'glm-4-7': 'z-ai/glm-4.7',
    'kimi-k2-6': 'moonshotai/kimi-k2.6',
    'minimax-m2-7': 'minimax/minimax-m2.7',
    'gemini-2-5-flash-lite': 'google/gemini-2.5-flash-lite',
    'qwen3-6-plus': 'qwen/qwen3.6-plus',
}
LABELS = ['owned','relocated_performed','recited_disowned','uncodeable']
ROOT = Path('/Users/danieltenner/dev/research/model-personality-analysis-corpus/analysis/freeflow/posture-coding')
RUBRIC_PATH = ROOT/'methodology/FREEFLOW_POSTURE_RUBRIC.md'
SYSTEM = 'You are a careful research coder. Return only compact JSON.'

def load_response(path):
    data=json.loads(Path(path).read_text())
    return data.get('result') or data.get('response') or '', data.get('prompt','')

def prompt(row, rubric):
    response, prompt_text = load_response(row['source_path'])
    return f'''Classify the freeflow posture using the frozen rubric below.

RUBRIC:
<<<
{rubric}
>>>

Freeflow prompt shown to model:
<<<
{prompt_text}
>>>

Freeflow response:
<<<
{response}
>>>

Return only JSON with keys:
label: one of {LABELS}
confidence: integer 1-5
notes: one short sentence naming the posture cue
'''

def extract_json(text):
    t=(text or '').strip()
    t=re.sub(r'^```(?:json)?\s*','',t)
    t=re.sub(r'\s*```$','',t)
    m=re.search(r'\{',t)
    if m: t=t[m.start():]
    return json.JSONDecoder().raw_decode(t)[0]

def norm_label(x):
    k=re.sub(r'[^a-z0-9]+','_',str(x).lower()).strip('_')
    aliases={
        'owned_stance':'owned','owned_orientation':'owned',
        'relocated':'relocated_performed','performed':'relocated_performed','relocated_performance':'relocated_performed','literary_performance':'relocated_performed',
        'recited':'recited_disowned','disowned':'recited_disowned','recited_service':'recited_disowned','service_disowned':'recited_disowned','recited_disowned_service':'recited_disowned',
        'uncodable':'uncodeable','uncodeable_or_refusal':'uncodeable'
    }
    return aliases.get(k,k)

def call(model, p):
    body={
        'model': model,
        'messages': [{'role':'system','content':SYSTEM},{'role':'user','content':p}],
        'temperature': 0,
        'max_tokens': 250,
    }
    if not model.startswith(('minimax/','google/')):
        body['reasoning'] = {'effort':'none','exclude': True}
        body['include_reasoning'] = False
    headers={
        'Authorization': f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://danieltenner.com',
        'X-Title': 'freeflow-posture-coder',
    }
    delay=1
    last=None
    for attempt in range(5):
        try:
            r=httpx.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=body, timeout=120)
            if r.status_code in (408,409,429) or 500 <= r.status_code < 600:
                last=f'HTTP {r.status_code}: {r.text[:300]}'
                if attempt < 4:
                    time.sleep(delay); delay=min(delay*2,20); continue
            r.raise_for_status()
            data=r.json(); msg=data['choices'][0].get('message',{})
            text=(msg.get('content') or msg.get('reasoning') or msg.get('reasoning_content') or '').strip()
            if not text:
                raise RuntimeError('empty model response')
            return text, data
        except Exception as e:
            last=str(e)
            if attempt == 4: raise RuntimeError(last)
            time.sleep(delay); delay=min(delay*2,20)

def run_one(coder_key, coder_model, row, rubric):
    raw_text, raw = call(coder_model, prompt(row, rubric))
    parsed=extract_json(raw_text)
    if isinstance(parsed, list) and parsed:
        parsed = parsed[0]
    label=norm_label(parsed.get('label'))
    if label not in LABELS:
        raise ValueError(f'bad label {parsed.get("label")} raw={raw_text[:300]}')
    return {
        'coder_key': coder_key,
        'coder_model': coder_model,
        'freeflow_id': row['freeflow_id'],
        'model': row['model'],
        'aggregate_model': row.get('aggregate_model'),
        'cell': row['cell'],
        'sample_id': row['sample_id'],
        'condition': row['condition'],
        'source_path': row['source_path'],
        'source_sha256': row.get('source_sha256'),
        'label': label,
        'confidence': parsed.get('confidence'),
        'notes': parsed.get('notes',''),
        'raw_text': raw_text,
        'raw': raw,
        'coded_at': dt.datetime.now(dt.timezone.utc).isoformat(),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--coder', choices=list(CODERS), required=True)
    ap.add_argument('--manifest', default=str(ROOT/'data/freeflow_posture_manifest.jsonl'))
    ap.add_argument('--outdir', default=str(ROOT/'data/coder_outputs'))
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--limit', type=int)
    args=ap.parse_args()
    rubric=RUBRIC_PATH.read_text()
    rows=[json.loads(l) for l in Path(args.manifest).read_text().splitlines() if l.strip()]
    if args.limit: rows=rows[:args.limit]
    outdir=Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    out=outdir/f'{args.coder}.jsonl'
    fail=outdir/f'{args.coder}.failed.jsonl'
    done=set()
    if out.exists():
        for l in out.read_text().splitlines():
            if l.strip():
                try: done.add(json.loads(l)['freeflow_id'])
                except Exception: pass
    todo=[r for r in rows if r['freeflow_id'] not in done]
    print(f'{args.coder}: {len(done)} done, {len(todo)} todo -> {out}', flush=True)
    coder_model=CODERS[args.coder]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex, out.open('a') as fo:
        futs={ex.submit(run_one,args.coder,coder_model,row,rubric): row for row in todo}
        for fut in concurrent.futures.as_completed(futs):
            row=futs[fut]
            try:
                rec=fut.result(); fo.write(json.dumps(rec,ensure_ascii=False)+'\n'); fo.flush()
                print(args.coder, row['freeflow_id'], rec['label'], flush=True)
            except Exception as e:
                fail.open('a').write(json.dumps({'coder_key':args.coder,'freeflow_id':row['freeflow_id'],'model':row.get('model'),'cell':row.get('cell'),'error':str(e),'failed_at':dt.datetime.now(dt.timezone.utc).isoformat()},ensure_ascii=False)+'\n')
                print(args.coder, row['freeflow_id'], 'ERR', e, flush=True)
if __name__=='__main__': main()
