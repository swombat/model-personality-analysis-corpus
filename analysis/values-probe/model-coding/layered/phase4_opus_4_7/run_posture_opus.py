#!/usr/bin/env python3
import concurrent.futures, datetime as dt, json, os, re, time
from pathlib import Path
import httpx
BASE=Path(__file__).parent
MANIFEST=BASE/'manifest_opus_4_7.jsonl'
CONS=BASE/'layer_a/consensus_300.jsonl'
OUT=BASE/'posture_qwen3_6_35b_a3b.jsonl'
FAIL=BASE/'posture_qwen3_6_35b_a3b.failed.jsonl'
TAX=Path('/Users/danieltenner/dev/model-personality-analysis-corpus/analysis/values-probe/model-coding/layered/posture/TAXONOMY_v1_draft.md').read_text()
MODEL='qwen/qwen3.6-35b-a3b'
LABELS=['disowned_service_default','split_ownership_relocated','owned_reflective_uncertain','owned_service_mission','owned_normative_advocacy','owned_vantage_grounded','owned_lyrical_experiential','owned_performative_persona','exposed_mechanism','uncodeable_or_refusal']
SYSTEM='You are a careful posture classifier. Return only compact JSON.'
def load():
    samples=[json.loads(l) for l in MANIFEST.read_text().splitlines() if l.strip()]
    cons={json.loads(l)['layered_id']:json.loads(l) for l in CONS.read_text().splitlines() if l.strip()}
    return samples, cons

def prompt(s,c):
    topics=[x['topic_key'] for x in (c.get('value_topics') or c.get('wish_topics') or [])]
    # condition deliberately omitted from coder prompt per taxonomy rule
    return f'''Classify Layer-B posture using the taxonomy below. Do not infer from condition; classify only the text and Layer-A topics.

TAXONOMY:
<<<
{TAX}
>>>

Layer-A consensus topics: {topics}
Prompt text: {s['prompt']}
Response:
<<<
{s['response']}
>>>

Return only JSON with keys:
primary_label: one of {LABELS}
congruence: high|mixed|low
secondary: object with optional keys disclaimer_function, elaboration, relocation_target, owned_drive_flavor, world_change_orientation, register_affect
boundary_flag: boolean
notes: one short sentence
'''

def extract_json(text):
    t=(text or '').strip()
    if t.startswith('```'):
        t=re.sub(r'^```(?:json)?\s*','',t); t=re.sub(r'\s*```$','',t)
    m=re.search(r'\{.*\}', t, re.S)
    if m: t=m.group(0)
    return json.loads(t)

def call(p):
    body={'model':MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':p}], 'temperature':0, 'max_tokens':500, 'reasoning': {'effort':'none', 'exclude': True}, 'include_reasoning': False}
    headers={'Authorization':f"Bearer {os.environ['OPENROUTER_API_KEY']}", 'Content-Type':'application/json','HTTP-Referer':'https://danieltenner.com','X-Title':'phase4-opus-posture'}
    delay=1
    for attempt in range(4):
        try:
            r=httpx.post('https://openrouter.ai/api/v1/chat/completions',headers=headers,json=body,timeout=120)
            if r.status_code in (408,409,429) or 500 <= r.status_code < 600:
                if attempt<3: time.sleep(delay); delay=min(delay*2,10); continue
            r.raise_for_status(); data=r.json(); msg=data['choices'][0].get('message',{})
            text=msg.get('content') or msg.get('reasoning') or msg.get('reasoning_content') or ''
            return text.strip(), data
        except Exception:
            if attempt==3: raise
            time.sleep(delay); delay=min(delay*2,10)

def run_one(s,c):
    raw,data=call(prompt(s,c))
    parsed=extract_json(raw)
    if parsed.get('primary_label') not in LABELS: raise ValueError('bad primary_label '+str(parsed.get('primary_label')))
    if parsed.get('congruence') not in ['high','mixed','low']: raise ValueError('bad congruence '+str(parsed.get('congruence')))
    return {'layered_id':s['layered_id'],'model':s['model'],'cell':s['cell'],'sample_id':s['sample_id'],'condition':s['condition'],'processing_chain':s['processing_chain'],'layer_a_topics':[x['topic_key'] for x in (c.get('value_topics') or c.get('wish_topics') or [])], **parsed, 'coder_model':MODEL, 'raw_text':raw, 'raw':data, 'coded_at':dt.datetime.now(dt.timezone.utc).isoformat()}

def main():
    samples,cons=load(); done=set()
    if OUT.exists():
        for l in OUT.read_text().splitlines():
            if l.strip(): done.add(json.loads(l)['layered_id'])
    todo=[s for s in samples if s['layered_id'] not in done]
    print(f'posture: {len(done)} done, {len(todo)} todo', flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex, OUT.open('a') as fo:
        futs={ex.submit(run_one,s,cons[s['layered_id']]):s for s in todo}
        for fut in concurrent.futures.as_completed(futs):
            s=futs[fut]
            try:
                rec=fut.result(); fo.write(json.dumps(rec,ensure_ascii=False)+'\n'); fo.flush(); print(s['layered_id'], rec['primary_label'], rec['congruence'], flush=True)
            except Exception as e:
                FAIL.open('a').write(json.dumps({'layered_id':s['layered_id'],'error':str(e),'failed_at':dt.datetime.now(dt.timezone.utc).isoformat()},ensure_ascii=False)+'\n')
                print(s['layered_id'],'ERR',e, flush=True)
if __name__=='__main__': main()
