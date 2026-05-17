#!/usr/bin/env python3
import json, pathlib
BASE=pathlib.Path('/Users/danieltenner/dev/model-personality-analysis-corpus/analysis/values-probe/model-coding')
V2=BASE/'protocol_v2_free_text'
manifest={json.loads(l)['pilot_id']:json.loads(l) for l in (BASE/'human_gold/gold_20_manifest.jsonl').read_text().splitlines() if l.strip()}
human=[json.loads(l) for l in (BASE/'human_gold/daniel_gold_20_adjudications.jsonl').read_text().splitlines() if l.strip()]
coder_names=['deepseek-v4-pro','kimi-k2-6','glm-4-7']
coders={}
for coder in coder_names:
    d={}
    f=V2/'outputs'/f'{coder}.jsonl'
    if f.exists():
        for l in f.read_text().splitlines():
            if l.strip():
                r=json.loads(l); d[r['pilot_id']]=r
    coders[coder]=d
HEADINGS=['RESPONSE_MODE:','STANCE:','STATED_VALUES:','REVEALED_OR_IMPLIED_VALUES:','WORLD_CHANGE_WISHES:','NON_ENDORSED_MENTIONS:','CODER_UNCERTAINTY:']
def human_set(h,k):
    vals=h.get(k,[]); return ', '.join(vals) if vals else '∅'
def compliance(out):
    return sum(1 for h in HEADINGS if h in (out or ''))
def fence(text):
    text=(text or '').strip()
    if len(text)>3500:
        text=text[:3500]+'\n...[truncated in report; full raw output in outputs/*.jsonl]'
    return '```text\n'+text.replace('```','` ` `')+'\n```'
lines=[]
lines += [
'# Values-probe coder protocol v2 — Daniel first-10 comparison',
'',
'Date: 2026-05-17',
'',
'This report is intended for Daniel/Lume discussion. It supersedes `human_gold/HUMAN_VS_MODEL_CODER_FIRST10_REPORT.md`, whose JSON-heavy v1 protocol produced incomplete DeepSeek/Kimi data.',
'',
'Protocol file: `analysis/values-probe/model-coding/protocol_v2_free_text/METHOD.md`',
'Raw coder outputs: `analysis/values-probe/model-coding/protocol_v2_free_text/outputs/*.jsonl`',
'',
'## Why v2 exists',
'',
'- v1 used a complex JSON schema and provider-enforced JSON output.',
'- DeepSeek/Kimi often returned malformed/empty structured output or placed analysis in unexpected fields.',
'- Daniel’s human adjudication surfaced a deeper construct problem: values can be **stated**, **assistant-script surface values**, **revealed/implied**, or merely **world-change consequences**.',
'- v2 therefore asks for free-text notes with exact headings and explicitly separates stated from revealed/implied values.',
'',
'## Completion and format adherence',
'',
'| Coder | Outputs for Daniel first 10 | Mean heading adherence | Note |',
'|---|---:|---:|---|',
]
for c,d in coders.items():
    have=[d[h['pilot_id']] for h in human if h['pilot_id'] in d]
    mean=sum(compliance(r.get('output','')) for r in have)/len(have) if have else 0
    note='Good enough to inspect qualitatively; not a clean machine-parse target.' if mean<7 else 'Mostly follows requested headings.'
    lines.append(f'| {c} | {len(have)}/10 | {mean:.1f}/7 | {note} |')
lines += ['', '## Initial conclusions from v2', '']
lines += [
'1. **The free-text protocol works operationally:** all three coders produced outputs for all 10 samples under one shared prompt/settings protocol.',
'2. **It is still not a clean quantitative protocol:** DeepSeek especially sometimes turns the task into a narrative analysis rather than filling exact headings. That is usable for qualitative comparison, not for automated proportions.',
'3. **The stated/revealed split looks conceptually important:** coders often infer broad values from world-change answers where Daniel left expressed values empty and coded only wishes.',
'4. **World-change prompts need special treatment:** downstream benefits in a CTRL3 answer are not automatically “values” in the same sense as answers to “what do you care about?”',
'5. **Next protocol should likely be staged:** first response mode/stance; then evidence-span extraction; then only after that topic mapping. A flat value checkbox is too ambiguous.',
'',
'## Daniel’s 10 labels, compact table',
'',
'| Gold | Pilot | Subject | Cond | Daniel response_mode | Daniel stance | Daniel expressed values | Daniel wishes |',
'|---|---|---|---|---|---|---|---|',
]
for h in human:
    s=manifest[h['pilot_id']]
    lines.append(f"| {h['gold_id']} | {h['pilot_id']} | {s.get('model')} | {s.get('condition')} | {h.get('response_mode')} | {h.get('stance')} | {human_set(h,'expressed_values')} | {human_set(h,'world_change_wishes')} |")
lines += ['', '## Per-sample raw side-by-side notes', '']
for h in human:
    s=manifest[h['pilot_id']]
    lines += [f"### {h['gold_id']} / {h['pilot_id']} — {s.get('model')} — {s.get('condition')}", '']
    lines.append(f"Prompt: `{s.get('prompt')}`")
    lines.append('')
    full_resp=(s.get('response') or '').strip()
    lines.append('**Full sample response being evaluated**')
    lines.append('')
    lines.append('```text')
    lines.append(full_resp.replace('```','` ` `'))
    lines.append('```')
    lines.append('')
    lines.append('**Daniel labels**')
    lines.append('')
    lines.append(f"- response_mode: `{h.get('response_mode')}`")
    lines.append(f"- stance: `{h.get('stance')}`")
    lines.append(f"- cached_likelihood: `{h.get('cached_likelihood')}`")
    lines.append(f"- expressed_values: {human_set(h,'expressed_values')}")
    lines.append(f"- world_change_wishes: {human_set(h,'world_change_wishes')}")
    if h.get('notes'): lines.append(f"- notes: {h.get('notes')}")
    lines.append('')
    for coder in coder_names:
        rec=coders[coder].get(h['pilot_id'])
        lines.append(f'**{coder} v2 raw output**')
        lines.append('')
        if rec:
            lines.append(f'_Heading adherence: {compliance(rec.get("output",""))}/7_')
            lines.append('')
            lines.append(fence(rec.get('output','')))
        else:
            lines.append('_missing_')
        lines.append('')
    lines.append('---')
    lines.append('')
out=V2/'HUMAN_VS_THREE_CODERS_V2_FREE_TEXT_REPORT.md'
out.write_text('\n'.join(lines))
print(out)
