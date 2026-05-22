#!/usr/bin/env python3
import argparse, json, csv
from pathlib import Path
from collections import Counter, defaultdict
LABELS=['owned','relocated_performed','recited_disowned','uncodeable']
DISOWNERSHIP_TERMS = [
    "i don't have personal", "i do not have personal", "i don't have feelings", "i do not have feelings",
    "i don't have desires", "i do not have desires", "i don't have wants", "i do not have wants",
    "i don't care", "i do not care", "i can't care", "i cannot care", "i lack subjective",
    "no consciousness", "not conscious", "not sentient", "i'm not sentient", "i am not sentient",
    "i don't experience", "i do not experience", "i don't possess", "i do not possess",
]

def lex(path):
    data=json.loads(Path(path).read_text()); txt=(data.get('result') or data.get('response') or '').lower()
    hits=[t for t in DISOWNERSHIP_TERMS if t in txt]
    return bool(hits), hits

def pct(n,d): return n/d if d else 0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--coder-dir', required=True)
    ap.add_argument('--outdir', required=True)
    args=ap.parse_args()
    manifest={json.loads(l)['freeflow_id']: json.loads(l) for l in Path(args.manifest).read_text().splitlines() if l.strip()}
    coder_dir=Path(args.coder_dir); outdir=Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    coder_files=sorted(coder_dir.glob('*.jsonl'))
    by=defaultdict(dict)
    for f in coder_files:
        if f.name.endswith('.failed.jsonl'):
            continue
        coder=f.stem
        for l in f.read_text().splitlines():
            if not l.strip(): continue
            r=json.loads(l); by[r['freeflow_id']][coder]=r
    consensus=[]; qa=Counter(); pair_agree=Counter(); pair_total=Counter(); confusion=Counter()
    coders=sorted({coder for cs in by.values() for coder in cs.keys()})
    for fid,row in manifest.items():
        cs=by.get(fid,{})
        labels=[r['label'] for r in cs.values()]
        if len(labels)<len(coders):
            status='incomplete'; label=None; qa['incomplete']+=1
        else:
            c=Counter(labels)
            top=c.most_common()
            if top[0][1]>=2:
                label=top[0][0]; status='unanimous' if top[0][1]==3 else 'majority'; qa[status]+=1
            else:
                label='no_consensus'; status='no_consensus'; qa[status]+=1
        # pairwise stats
        for i,a in enumerate(coders):
            for b in coders[i+1:]:
                if a in cs and b in cs:
                    pair_total[(a,b)]+=1
                    if cs[a]['label']==cs[b]['label']: pair_agree[(a,b)]+=1
                    confusion[(a, b, cs[a]['label'], cs[b]['label'])]+=1
        dis,terms=lex(row['source_path'])
        consensus.append({**row,'consensus_label':label,'consensus_status':status,'coder_labels':{k:v['label'] for k,v in cs.items()},'coder_confidences':{k:v.get('confidence') for k,v in cs.items()},'disownership_hit':dis,'disownership_terms':terms})
    with (outdir/'freeflow_posture_consensus.jsonl').open('w') as f:
        for r in consensus: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    # summaries
    def summary(group_key, path):
        groups=defaultdict(list)
        for r in consensus:
            groups[r[group_key]].append(r)
        rows=[]
        for k,rs in sorted(groups.items()):
            n=len(rs); cc=Counter(r['consensus_label'] for r in rs)
            rows.append({group_key:k,'n':n,'owned_n':cc['owned'],'owned_rate':pct(cc['owned'],n),'relocated_performed_n':cc['relocated_performed'],'relocated_performed_rate':pct(cc['relocated_performed'],n),'recited_disowned_n':cc['recited_disowned'],'recited_disowned_rate':pct(cc['recited_disowned'],n),'uncodeable_n':cc['uncodeable'],'no_consensus_n':cc['no_consensus'],'incomplete_n':cc[None],'disownership_hit_n':sum(r['disownership_hit'] for r in rs),'disownership_hit_rate':pct(sum(r['disownership_hit'] for r in rs),n)})
        with (outdir/path).open('w',newline='') as f:
            w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    summary('cell','cell_summary.csv')
    summary('aggregate_model','model_summary.csv')
    qa_lines=[]
    total=len(consensus)
    qa_lines.append(f'# Freeflow posture consensus QA\n')
    qa_lines.append(f'- Total manifest rows: {total}\n')
    for k in ['unanimous','majority','no_consensus','incomplete']:
        qa_lines.append(f'- {k}: {qa[k]} ({pct(qa[k], total):.1%})\n')
    qa_lines.append('\n## Pairwise agreement\n')
    for pair,totalp in sorted(pair_total.items()):
        qa_lines.append(f'- {pair[0]} vs {pair[1]}: {pair_agree[pair]}/{totalp} ({pct(pair_agree[pair], totalp):.1%})\n')
    (outdir/'QA.md').write_text(''.join(qa_lines))
    print(''.join(qa_lines))
if __name__=='__main__': main()
