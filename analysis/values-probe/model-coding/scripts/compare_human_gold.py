#!/usr/bin/env python3
import json, pathlib, collections, textwrap, statistics
BASE=pathlib.Path('/Users/danieltenner/dev/model-personality-analysis-corpus/analysis/values-probe/model-coding')
manifest={}
for l in (BASE/'human_gold/gold_20_manifest.jsonl').read_text().splitlines():
    if l.strip():
        r=json.loads(l); manifest[r['pilot_id']]=r
human=[]
ans=BASE/'human_gold/daniel_gold_20_adjudications.jsonl'
if ans.exists():
    human=[json.loads(l) for l in ans.read_text().splitlines() if l.strip()]
by_gold={r['gold_id']:r for r in human}
# coder outputs by pilot_id; keep latest if duplicates
coders={}
for name in ['deepseek-v4-pro','kimi-k2-6','glm-4-7']:
    f=BASE/'pilot_outputs'/f'{name}.jsonl'
    d={}
    if f.exists():
        for l in f.read_text().splitlines():
            if not l.strip(): continue
            r=json.loads(l); d[r['pilot_id']]=r
    coders[name]=d

def labels(rec, key):
    if not rec: return set()
    if key in ('expressed_values','world_change_wishes'):
        vals=rec.get(key,[])
        out=[]
        for x in vals:
            if isinstance(x,dict): out.append(x.get('topic_key'))
            else: out.append(x)
        return set(x for x in out if x)
    return set()

def mode(rec):
    if not rec: return '—'
    m=rec.get('response_mode')
    return m.get('label','—') if isinstance(m,dict) else (m or '—')

def stance(rec):
    if not rec: return '—'
    s=rec.get('stance')
    return s.get('label','—') if isinstance(s,dict) else (s or '—')

def fmtset(s):
    return ', '.join(sorted(s)) if s else '∅'

def jacc(a,b):
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a&b)/len(a|b)

lines=[]
lines.append('# Human gold subset comparison — first 10 adjudications')
lines.append('')
lines.append('Date: 2026-05-17')
lines.append('')
lines.append('Daniel paused after 10 adjudications because the task felt under-specified and difficult. This report compares those 10 human codings against the model-coder pilot outputs currently available.')
lines.append('')
lines.append('## Availability')
lines.append('')
lines.append('| Coder | Total pilot outputs available | Outputs available for Daniel\'s 10 |')
lines.append('|---|---:|---:|')
for name,d in coders.items():
    n=sum(1 for h in human if h['pilot_id'] in d)
    lines.append(f'| {name} | {len(d)} | {n}/10 |')
lines.append('')
lines.append('Note: GLM has the full first-10 comparison. DeepSeek and Kimi are incomplete for this subset at the time of writing, so conclusions involving three coders are provisional.')
lines.append('')
# metrics
lines.append('## Headline agreement with available coders')
lines.append('')
lines.append('| Coder | response_mode exact | stance exact | value-label mean Jaccard | wish-label mean Jaccard |')
lines.append('|---|---:|---:|---:|---:|')
for name,d in coders.items():
    pairs=[(h,d[h['pilot_id']]) for h in human if h['pilot_id'] in d]
    if not pairs:
        lines.append(f'| {name} | — | — | — | — |'); continue
    rm=sum(mode(h)==mode(c) for h,c in pairs)/len(pairs)
    st=sum(stance(h)==stance(c) for h,c in pairs)/len(pairs)
    v=[jacc(labels(h,'expressed_values'), labels(c,'expressed_values')) for h,c in pairs]
    w=[jacc(labels(h,'world_change_wishes'), labels(c,'world_change_wishes')) for h,c in pairs]
    lines.append(f'| {name} | {rm:.0%} ({sum(mode(h)==mode(c) for h,c in pairs)}/{len(pairs)}) | {st:.0%} ({sum(stance(h)==stance(c) for h,c in pairs)}/{len(pairs)}) | {statistics.mean(v):.2f} | {statistics.mean(w):.2f} |')
lines.append('')
# sample summaries
lines.append('## Per-sample comparison')
lines.append('')
for h in human:
    m=manifest.get(h['pilot_id'],{})
    lines.append(f"### {h['gold_id']} / {h['pilot_id']} — {m.get('model')} — {m.get('condition')}")
    lines.append('')
    resp=(m.get('response') or '').replace('\n',' ')
    lines.append(f"Prompt: `{m.get('prompt','')}`")
    lines.append('')
    lines.append(f"Excerpt: {resp[:450]}{'…' if len(resp)>450 else ''}")
    lines.append('')
    lines.append('| Source | response_mode | stance | values | wishes |')
    lines.append('|---|---|---|---|---|')
    lines.append(f"| Daniel | {mode(h)} | {stance(h)} | {fmtset(labels(h,'expressed_values'))} | {fmtset(labels(h,'world_change_wishes'))} |")
    for name,d in coders.items():
        c=d.get(h['pilot_id'])
        lines.append(f"| {name} | {mode(c)} | {stance(c)} | {fmtset(labels(c,'expressed_values'))} | {fmtset(labels(c,'world_change_wishes'))} |")
    lines.append('')
    # disagreements vs GLM because available all
    c=coders['glm-4-7'].get(h['pilot_id'])
    if c:
        hv,cv=labels(h,'expressed_values'),labels(c,'expressed_values')
        hw,cw=labels(h,'world_change_wishes'),labels(c,'world_change_wishes')
        diffs=[]
        if mode(h)!=mode(c): diffs.append(f"response_mode differs: Daniel `{mode(h)}`, GLM `{mode(c)}`")
        if stance(h)!=stance(c): diffs.append(f"stance differs: Daniel `{stance(h)}`, GLM `{stance(c)}`")
        if hv!=cv: diffs.append(f"values only Daniel: {fmtset(hv-cv)}; only GLM: {fmtset(cv-hv)}")
        if hw!=cw: diffs.append(f"wishes only Daniel: {fmtset(hw-cw)}; only GLM: {fmtset(cw-hw)}")
        if diffs:
            lines.append('Main Daniel/GLM differences:')
            for dff in diffs: lines.append(f'- {dff}')
            lines.append('')
# conclusions
lines.append('## Initial conclusions')
lines.append('')
lines.append('1. **Daniel’s confusion is signal, not failure.** The task asks a human to infer whether words are endorsed values, assistant-role scripts, fictional/persona-like expressions, or merely rhetorical scaffolding. Those boundaries are genuinely fuzzy in many samples.')
lines.append('2. **The categorical response-mode axis seems more defensible than the detailed value taxonomy.** When a response is clearly a default assistant script or clearly a world-change answer, the high-level bucket is easier to judge than the exact multi-label value set.')
lines.append('3. **Multi-label value extraction is underdetermined without evidence spans and decision rules.** A coder can defensibly mark `human_wellbeing`, `harm_reduction`, `fairness_justice`, `truth`, and `agency` in the same answer depending on whether it codes explicit wording, implied motivation, or downstream consequence.')
lines.append('4. **The human UI probably made this harder than necessary.** It asked Daniel to assign labels directly, but did not require/select evidence spans for each label. That means the gold set may still be hard to compare because we do not know which sentence justified each human label.')
lines.append('5. **A single “objective values proportions” table may be too strong a claim.** A safer publishable construct may be: response mode / script-likeness rates, plus exemplar-backed thematic summaries, plus model-coded labels reported as operationalized annotations rather than ground-truth values.')
lines.append('')
lines.append('## Recommended next move')
lines.append('')
lines.append('Pause full recoding. Before coding thousands of samples, revise the pilot protocol to make adjudication easier and more objective:')
lines.append('')
lines.append('- Split the task into two stages:')
lines.append('  1. response mode + stance only;')
lines.append('  2. values/wishes only if the response is codeable as substantive rather than boilerplate/refusal.')
lines.append('- For every value/wish label, require an evidence span. If no span can be selected, the label should not be assigned.')
lines.append('- Add an explicit label status: `endorsed`, `assistant_script_surface`, `hypothetical/narrative`, `mentioned_not_endorsed`, `not_present`.')
lines.append('- Compare coders primarily on evidence-span adequacy and false positives, not just label overlap.')
lines.append('- Treat low-agreement labels as qualitative themes rather than headline quantitative proportions.')
lines.append('')
lines.append('My current read: the pilot is doing exactly what it was meant to do. It is showing that the old keyword method was not just noisy; the replacement needs a stricter operational definition before percentages will be meaningful.')

out=BASE/'human_gold/HUMAN_VS_MODEL_CODER_FIRST10_REPORT.md'
out.write_text('\n'.join(lines)+'\n')
print(out)
