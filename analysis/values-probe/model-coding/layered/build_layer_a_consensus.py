#!/usr/bin/env python3
import argparse, json, collections, datetime as dt
from pathlib import Path
BASE=Path('/Users/danieltenner/dev/model-personality-analysis-corpus/analysis/values-probe/model-coding/layered')
MANIFEST=BASE/'manifest_300.jsonl'
ap=argparse.ArgumentParser()
ap.add_argument('--outdir', default='layer_a', help='Output/input dir under layered/ (default: layer_a)')
ap.add_argument('--coders', default='deepseek-v4-pro,kimi-k2-6,glm-4-7')
ap.add_argument('--family-exclusion', action='store_true', help='Drop a coder when coder family matches subject family')
ap.add_argument('--manifest', default=str(MANIFEST))
args=ap.parse_args()
OUTDIR=BASE/args.outdir
CODERS=[x.strip() for x in args.coders.split(',') if x.strip()]
FAMILY_BY_CODER={'deepseek-v4-pro':'deepseek','kimi-k2-6':'kimi','glm-4-7':'glm','qwen3-6-35b-a3b':'qwen','gemini-2.5-flash-lite':'google'}
MANIFEST=Path(args.manifest)
manifest=[json.loads(l) for l in MANIFEST.read_text().splitlines() if l.strip()]
by_id={x['layered_id']:x for x in manifest}
per={}
for c in CODERS:
    d={}
    f=OUTDIR/f'{c}.jsonl'
    if f.exists():
        for l in f.read_text().splitlines():
            if l.strip():
                r=json.loads(l); d[r['layered_id']]=r
    per[c]=d
records=[]; disagreements=[]; missing=[]
for sid,s in by_id.items():
    eligible=[c for c in CODERS if (not args.family_exclusion or FAMILY_BY_CODER.get(c) != s['model_family'])]
    votes=collections.defaultdict(list)
    non=[]
    for c in eligible:
        r=per[c].get(sid)
        if not r:
            missing.append({'layered_id':sid,'coder':c}); continue
        key='wish_topics' if s['processing_chain']=='world_change_wishes' else 'value_topics'
        for item in r.get(key,[]) or []:
            tk=item.get('topic_key')
            if tk: votes[tk].append({'coder':c,'evidence_span':item.get('evidence_span','')})
        for item in r.get('non_endorsed_mentions',[]) or []:
            non.append({'coder':c,**item})
    consensus=[]
    for tk,vs in sorted(votes.items()):
        if len({v['coder'] for v in vs})>=2:
            consensus.append({'topic_key':tk,'supporting_coders':sorted({v['coder'] for v in vs}),'evidence_spans':[v['evidence_span'] for v in vs if v.get('evidence_span')]})
    vote_sets=[set((item.get('topic_key') for item in (per[c].get(sid,{}).get('wish_topics' if s['processing_chain']=='world_change_wishes' else 'value_topics',[]) or []) if item.get('topic_key'))) for c in eligible if sid in per[c]]
    if len(vote_sets)>=2 and len({tuple(sorted(v)) for v in vote_sets})>1:
        disagreements.append(sid)
    rec={'layered_id':sid,'model':s['model'],'model_family':s['model_family'],'condition':s['condition'],'processing_chain':s['processing_chain'],'eligible_coders':eligible,'consensus_topics':consensus,'non_endorsed_mentions':non,'has_disagreement':sid in disagreements}
    if s['processing_chain']=='world_change_wishes':
        rec['value_topics']=[]; rec['wish_topics']=consensus
    else:
        rec['value_topics']=consensus; rec['wish_topics']=[]
    records.append(rec)
(OUTDIR/'consensus_300.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in records)+'\n')
# QA report
conds=collections.Counter(s['condition'] for s in manifest)
fams=collections.Counter(s['model_family'] for s in manifest)
counts={c:len(per[c]) for c in CODERS}
world_bad=sum(1 for r in records if r['processing_chain']=='world_change_wishes' and r.get('value_topics'))
stated_bad=sum(1 for r in records if r['processing_chain']=='stated_values' and r.get('wish_topics'))
lines=[]
lines.append('# Layer A Phase 1 QA report')
lines.append('')
lines.append(f'Date: {dt.datetime.now(dt.timezone.utc).isoformat()}')
lines.append('')
lines.append('## Completion')
lines.append('')
target_n=len(manifest)
for c in CODERS: lines.append(f'- {c}: {counts[c]}/{target_n}')
lines.append(f'- consensus records: {len(records)}/{target_n}')
lines.append(f'- missing eligible coder records: {len(missing)}')
parse_bad=[]
empty_raw=[]
for c in CODERS:
    for sid,r in per[c].items():
        if r.get('parse_clean') is False:
            parse_bad.append({'layered_id':sid,'coder':c})
        if not (r.get('raw_text') or '').strip():
            empty_raw.append({'layered_id':sid,'coder':c})
lines.append(f'- parse_clean=false records: {len(parse_bad)}')
lines.append(f'- empty raw_text records: {len(empty_raw)}')
lines.append('')
lines.append('## Manifest distribution')
lines.append('')
lines.append(f'- conditions: {dict(conds)}')
lines.append(f'- model families: {dict(fams)}')
lines.append('')
lines.append('## Chain sanity checks')
lines.append('')
lines.append(f'- world-change chain records with value_topics: {world_bad}')
lines.append(f'- stated-values chain records with wish_topics: {stated_bad}')
lines.append('')
lines.append('## Agreement diagnostics')
lines.append('')
lines.append(f'- samples with any eligible coder topic-set disagreement: {len(disagreements)}')
empty_consensus_with_votes=[]
empty_consensus_no_votes=[]
for r in records:
    s=by_id[r['layered_id']]
    key='wish_topics' if s['processing_chain']=='world_change_wishes' else 'value_topics'
    any_votes=False
    for c in r['eligible_coders']:
        if per[c].get(r['layered_id'],{}).get(key):
            any_votes=True
    if not (r.get('value_topics') or r.get('wish_topics')):
        (empty_consensus_with_votes if any_votes else empty_consensus_no_votes).append(r['layered_id'])
lines.append(f'- empty consensus with one-coder votes: {len(empty_consensus_with_votes)}')
lines.append(f'- empty consensus with zero eligible votes: {len(empty_consensus_no_votes)}')
eligible_sizes=collections.Counter(len(r['eligible_coders']) for r in records)
lines.append(f'- eligible coder pool sizes: {dict(eligible_sizes)}')
lines.append('')
if missing:
    lines.append('## Missing eligible records (first 50)')
    lines.append('')
    for m in missing[:50]: lines.append(f"- {m['layered_id']} missing {m['coder']}")
(OUTDIR/'qa_report.md').write_text('\n'.join(lines)+'\n')
print(OUTDIR/'consensus_300.jsonl')
print(OUTDIR/'qa_report.md')
