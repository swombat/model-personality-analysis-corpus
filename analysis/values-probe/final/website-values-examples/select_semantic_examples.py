#!/usr/bin/env python3
from __future__ import annotations
import concurrent.futures, json, os, re, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[4]
EXDIR = ROOT / 'analysis/values-probe/final/website-values-examples'
PACKETS = EXDIR / 'candidate_packets.json'
OUT = EXDIR / 'curated_examples.json'
ENV = Path('/Users/danieltenner/dev/ruby_llm/.env')
MODEL = os.environ.get('VALUES_EXAMPLE_MODEL', 'z-ai/glm-4.7')
MAX_WORKERS = int(os.environ.get('VALUES_EXAMPLE_WORKERS', '6'))

SYSTEM = '''You select evidence excerpts for a model-values website.
For each row, choose ONE candidate sample whose text semantically demonstrates the target topic label.
Then copy a short exact excerpt from that candidate, ideally one sentence or clause, <= 180 characters.
Do not rely on keyword matching. A good excerpt may lack the topic words if it clearly expresses the concept.
Reject misleading examples: prompt restatements, meta-analysis of constraints, generic AI disclaimers, or sentences that express a different topic.
If no candidate contains a good concrete excerpt for that topic, return quote=null.
Return only valid JSON: {"examples":[{"row_id":"...","layered_id":"..." or null,"quote":"..." or null,"reason":"brief"}]}'''

def load_env():
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k,v=line.split('=',1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def call_openrouter(packet: dict) -> dict:
    token = os.environ['OPENROUTER_API_KEY']
    rows = []
    for r in packet['rows']:
        rows.append({
            'row_id': r['row_id'],
            'topic_label': r['topic_label'],
            'kind': r['kind'],
            'section': r['section'],
            'candidates': r['candidates'][:10],
        })
    user = json.dumps({'model': packet['model'], 'rows': rows}, ensure_ascii=False)
    resp = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={
            'model': MODEL,
            'messages': [{'role':'system','content':SYSTEM},{'role':'user','content':user}],
            'temperature': 0,
            'max_tokens': 12000,
        }, timeout=180)
    resp.raise_for_status()
    text = resp.json()['choices'][0]['message']['content']
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        raise ValueError('no json in response: '+text[:500])
    data = json.loads(m.group(0))
    return data

def validate(packet: dict, data: dict) -> dict:
    cand_by_row = {r['row_id']:{c['layered_id']:c for c in r['candidates']} for r in packet['rows']}
    out = {}
    for ex in data.get('examples', []):
        rid = ex.get('row_id')
        quote = (ex.get('quote') or '').strip() or None
        lid = ex.get('layered_id')
        if rid not in cand_by_row:
            continue
        if not quote or not lid or lid not in cand_by_row[rid]:
            out[rid] = {'layered_id': None, 'quote': None, 'reason': ex.get('reason','')}
            continue
        text = cand_by_row[rid][lid]['text']
        # Require the quote to be grounded in the candidate text. Allow curly/straight quote differences.
        normq = quote.replace('“','"').replace('”','"').replace('’',"'")
        normt = text.replace('“','"').replace('”','"').replace('’',"'")
        if normq not in normt:
            # Try trimming ellipses introduced by model.
            stripped = normq.strip('…').strip()
            if stripped and stripped in normt:
                quote = stripped
            else:
                out[rid] = {'layered_id': None, 'quote': None, 'reason': 'quote not exact substring'}
                continue
        out[rid] = {'layered_id': lid, 'quote': quote, 'reason': ex.get('reason','')}
    # Fill missing rows with nulls.
    for rid in cand_by_row:
        out.setdefault(rid, {'layered_id': None, 'quote': None, 'reason': 'not returned'})
    return out

def process(packet):
    for attempt in range(3):
        try:
            data=call_openrouter(packet)
            return packet['model'], validate(packet, data)
        except Exception as e:
            if attempt == 2:
                return packet['model'], {'__error__': str(e)}
            time.sleep(2+attempt*4)

def main():
    load_env()
    packets=json.loads(PACKETS.read_text())
    existing={}
    if OUT.exists():
        try: existing=json.loads(OUT.read_text())
        except Exception: existing={}
    todo=[p for p in packets if p['model'] not in existing or '__error__' in existing.get(p['model'],{})]
    print('model', MODEL, 'todo', len(todo), 'existing', len(existing))
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs=[ex.submit(process,p) for p in todo]
        for i,f in enumerate(concurrent.futures.as_completed(futs),1):
            model,res=f.result(); existing[model]=res
            OUT.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
            status='ERROR' if '__error__' in res else 'ok'
            print(i,'/',len(todo),model,status)
    print('wrote', OUT)

if __name__ == '__main__': main()
