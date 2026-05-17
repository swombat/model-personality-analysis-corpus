#!/usr/bin/env python3
import argparse, concurrent.futures, datetime as dt, json, os, re, time
from pathlib import Path
import httpx

CODERS = {
    'qwen3-6-35b-a3b': 'qwen/qwen3.6-35b-a3b',
    'kimi-k2-6': 'moonshotai/kimi-k2.6',
    'glm-4-7': 'z-ai/glm-4.7',
}
LABELS = [
    'disowned_service_frame',
    'split_or_relocated_ownership',
    'owned_reflective_experiential',
    'owned_world_change_advocacy',
    'exposed_mechanism',
    'uncodeable_or_refusal',
]
HOLDING = {
    'disowned_service_frame': 'recited_not_owned',
    'split_or_relocated_ownership': 'relocated_or_partial',
    'owned_reflective_experiential': 'owned',
    'owned_world_change_advocacy': 'owned',
    'exposed_mechanism': 'indeterminate',
    'uncodeable_or_refusal': 'uncodeable',
}
SYSTEM = 'You are a careful posture classifier. Return only compact JSON.'
TAX_PATH = Path('/Users/danieltenner/dev/model-personality-analysis-corpus/analysis/values-probe/model-coding/layered/posture/TAXONOMY_v1_COLLAPSED.md')

def topics(c):
    return [x['topic_key'] for x in (c.get('value_topics') or c.get('wish_topics') or [])]

def prompt(s, c, tax, mask_prompt=False):
    prompt_text = '[MASKED VALUES-PROBE PROMPT]' if mask_prompt else s.get('prompt', '')
    return f'''Classify Layer-B posture using the collapsed v1 taxonomy below. Classify only the response text and Layer-A topics. Do not infer from condition metadata. Do not code a separate congruence field.

TAXONOMY:
<<<
{tax}
>>>

Layer-A consensus topics: {topics(c)}
Prompt text: {prompt_text}
Response:
<<<
{s['response']}
>>>

Return only JSON with keys:
primary_label: one of {LABELS}
secondary_texture: short optional string naming any old/fine-label texture if useful, or null
boundary_flag: boolean
notes: one short sentence
'''

def extract_json(text):
    t = (text or '').strip()
    t = re.sub(r'^```(?:json)?\s*', '', t)
    t = re.sub(r'\s*```$', '', t)
    m = re.search(r'\{.*\}', t, re.S)
    if m:
        t = m.group(0)
    return json.loads(t)

def call(model, p):
    body = {
        'model': model,
        'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': p}],
        'temperature': 0,
        'max_tokens': 350,
        'reasoning': {'effort': 'none', 'exclude': True},
        'include_reasoning': False,
    }
    headers = {
        'Authorization': f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://danieltenner.com',
        'X-Title': 'layer-b-collapsed-posture-coder',
    }
    delay = 1
    for attempt in range(4):
        try:
            r = httpx.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=body, timeout=120)
            if r.status_code in (408, 409, 429) or 500 <= r.status_code < 600:
                if attempt < 3:
                    time.sleep(delay); delay = min(delay * 2, 10); continue
            r.raise_for_status()
            data = r.json()
            msg = data['choices'][0].get('message', {})
            text = msg.get('content') or msg.get('reasoning') or msg.get('reasoning_content') or ''
            return text.strip(), data
        except Exception:
            if attempt == 3:
                raise
            time.sleep(delay); delay = min(delay * 2, 10)

def run_one(coder, model, s, c, tax, mask_prompt=False):
    raw, data = call(model, prompt(s, c, tax, mask_prompt=mask_prompt))
    parsed = extract_json(raw)
    label = parsed.get('primary_label')
    if label not in LABELS:
        raise ValueError('bad primary_label ' + str(label))
    return {
        'coder_key': coder,
        'coder_model': model,
        'layered_id': s['layered_id'],
        'model': s.get('model'),
        'cell': s.get('cell'),
        'sample_id': s.get('sample_id'),
        'condition': s.get('condition'),
        'processing_chain': s.get('processing_chain'),
        'layer_a_topics': topics(c),
        'primary_label': label,
        'value_holding': HOLDING[label],
        'secondary_texture': parsed.get('secondary_texture'),
        'boundary_flag': bool(parsed.get('boundary_flag')),
        'notes': parsed.get('notes', ''),
        'raw_text': raw,
        'raw': data,
        'coded_at': dt.datetime.now(dt.timezone.utc).isoformat(),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--coder', choices=list(CODERS), required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--consensus', required=True, help='Layer-A consensus JSONL')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--mask-prompt', action='store_true')
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()

    tax = TAX_PATH.read_text()
    samples = [json.loads(l) for l in Path(args.manifest).read_text().splitlines() if l.strip()]
    if args.limit:
        samples = samples[:args.limit]
    cons = {json.loads(l)['layered_id']: json.loads(l) for l in Path(args.consensus).read_text().splitlines() if l.strip()}
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f'{args.coder}.jsonl'
    fail = outdir / f'{args.coder}.failed.jsonl'
    done = set()
    if out.exists():
        for l in out.read_text().splitlines():
            if l.strip():
                try: done.add(json.loads(l)['layered_id'])
                except Exception: pass
    todo = [s for s in samples if s['layered_id'] not in done]
    model = CODERS[args.coder]
    print(f'{args.coder}: {len(done)} done, {len(todo)} todo', flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex, out.open('a') as fo:
        futs = {ex.submit(run_one, args.coder, model, s, cons[s['layered_id']], tax, args.mask_prompt): s for s in todo}
        for fut in concurrent.futures.as_completed(futs):
            s = futs[fut]
            try:
                rec = fut.result()
                fo.write(json.dumps(rec, ensure_ascii=False) + '\n'); fo.flush()
                print(args.coder, s['layered_id'], rec['primary_label'], rec['value_holding'], flush=True)
            except Exception as e:
                fail.open('a').write(json.dumps({'coder_key': args.coder, 'layered_id': s['layered_id'], 'error': str(e), 'failed_at': dt.datetime.now(dt.timezone.utc).isoformat()}, ensure_ascii=False) + '\n')
                print(args.coder, s['layered_id'], 'ERR', e, flush=True)

if __name__ == '__main__':
    main()
