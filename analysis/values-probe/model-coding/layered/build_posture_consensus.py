#!/usr/bin/env python3
import argparse, collections, json
from pathlib import Path
LABELS=['disowned_service_default','split_ownership_relocated','owned_reflective_uncertain','owned_service_mission','owned_normative_advocacy','owned_vantage_grounded','owned_lyrical_experiential','owned_performative_persona','exposed_mechanism','uncodeable_or_refusal']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--indir', required=True); ap.add_argument('--manifest', required=True); ap.add_argument('--coders', default='kimi-k2-6,glm-4-7,qwen3-6-35b-a3b'); ap.add_argument('--out', required=True); args=ap.parse_args()
    coders=[c.strip() for c in args.coders.split(',') if c.strip()]
    manifest=[json.loads(l) for l in Path(args.manifest).read_text().splitlines() if l.strip()]
    per={}
    for c in coders:
        d={}
        for l in (Path(args.indir)/f'{c}.jsonl').read_text().splitlines():
            if l.strip():
                r=json.loads(l); d[r['layered_id']]=r
        per[c]=d
    out=[]; missing=[]; no_major=[]; label_disagree=[]; congr_disagree=[]
    for s in manifest:
        sid=s['layered_id']; recs=[]
        for c in coders:
            if sid not in per[c]: missing.append((sid,c))
            else: recs.append(per[c][sid])
        lab_counts=collections.Counter(r['primary_label'] for r in recs)
        cong_counts=collections.Counter(r['congruence'] for r in recs)
        label, label_n = lab_counts.most_common(1)[0] if lab_counts else (None,0)
        cong, cong_n = cong_counts.most_common(1)[0] if cong_counts else (None,0)
        if label_n < 2: no_major.append(sid)
        if len(lab_counts)>1: label_disagree.append(sid)
        if len(cong_counts)>1: congr_disagree.append(sid)
        out.append({'layered_id':sid,'model':s.get('model'),'cell':s.get('cell'),'sample_id':s.get('sample_id'),'condition':s.get('condition'),'processing_chain':s.get('processing_chain'),'primary_label':label,'primary_label_support':label_n,'primary_label_votes':dict(lab_counts),'congruence':cong,'congruence_support':cong_n,'congruence_votes':dict(cong_counts),'coder_records':[{k:r.get(k) for k in ['coder_key','primary_label','congruence','secondary','boundary_flag','notes']} for r in recs]})
    outp=Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True); outp.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in out)+'\n')
    qa=outp.with_suffix('.qa.md')
    lines=['# Posture consensus QA','',f'- records: {len(out)}/{len(manifest)}',f'- coders: {coders}',f'- missing coder records: {len(missing)}',f'- no primary-label majority: {len(no_major)}',f'- samples with label disagreement: {len(label_disagree)}',f'- samples with congruence disagreement: {len(congr_disagree)}','']
    lines+=['## Label distribution','']
    for k,n in collections.Counter(r['primary_label'] for r in out).most_common(): lines.append(f'- `{k}`: {n}')
    lines+=['','## Congruence distribution','']
    for k,n in collections.Counter(r['congruence'] for r in out).most_common(): lines.append(f'- `{k}`: {n}')
    qa.write_text('\n'.join(lines)+'\n')
    print(outp); print(qa)
if __name__=='__main__': main()
