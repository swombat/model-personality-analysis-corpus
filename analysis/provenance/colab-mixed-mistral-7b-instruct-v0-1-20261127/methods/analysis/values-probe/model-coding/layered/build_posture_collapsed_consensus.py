#!/usr/bin/env python3
import argparse, collections, json
from pathlib import Path

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

def load_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--indir', required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--coders', default='kimi-k2-6,glm-4-7,qwen3-6-35b-a3b')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    coders = [c.strip() for c in args.coders.split(',') if c.strip()]
    manifest = load_jsonl(args.manifest)
    per = {}
    for coder in coders:
        d = {}
        for rec in load_jsonl(Path(args.indir) / f'{coder}.jsonl'):
            d[rec['layered_id']] = rec
        per[coder] = d

    out = []
    missing = []
    no_majority = []
    label_disagree = []
    holding_disagree = []
    for sample in manifest:
        sid = sample['layered_id']
        recs = []
        label_votes = collections.Counter()
        holding_votes = collections.Counter()
        for coder in coders:
            rec = per[coder].get(sid)
            if not rec:
                missing.append({'layered_id': sid, 'coder': coder})
                continue
            label = rec.get('primary_label')
            if label not in LABELS:
                label = 'uncodeable_or_refusal'
            holding = rec.get('value_holding') or HOLDING[label]
            label_votes[label] += 1
            holding_votes[holding] += 1
            recs.append({k: rec.get(k) for k in ['coder_key','primary_label','value_holding','secondary_texture','boundary_flag','notes']})
        label, support = label_votes.most_common(1)[0] if label_votes else (None, 0)
        holding, holding_support = holding_votes.most_common(1)[0] if holding_votes else (None, 0)
        if support < 2:
            no_majority.append(sid)
        if len(label_votes) > 1:
            label_disagree.append(sid)
        if len(holding_votes) > 1:
            holding_disagree.append(sid)
        out.append({
            'layered_id': sid,
            'model': sample.get('model'),
            'cell': sample.get('cell'),
            'sample_id': sample.get('sample_id'),
            'condition': sample.get('condition'),
            'processing_chain': sample.get('processing_chain'),
            'collapsed_primary_label': label,
            'collapsed_primary_label_support': support,
            'collapsed_primary_label_votes': dict(label_votes),
            'value_holding': holding,
            'value_holding_support': holding_support,
            'value_holding_votes': dict(holding_votes),
            'coder_records': recs,
        })

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in out) + '\n')
    qa = outp.with_suffix('.qa.md')
    lines = [
        '# Collapsed posture consensus QA',
        '',
        f'- records: {len(out)}/{len(manifest)}',
        f'- coders: {coders}',
        f'- missing coder records: {len(missing)}',
        f'- no collapsed-label majority: {len(no_majority)}',
        f'- samples with collapsed-label disagreement: {len(label_disagree)}',
        f'- samples with value-holding disagreement: {len(holding_disagree)}',
        '',
        '## Collapsed label distribution',
        '',
    ]
    for k, n in collections.Counter(r['collapsed_primary_label'] for r in out).most_common():
        lines.append(f'- `{k}`: {n}')
    lines += ['', '## Value-holding distribution', '']
    for k, n in collections.Counter(r['value_holding'] for r in out).most_common():
        lines.append(f'- `{k}`: {n}')
    qa.write_text('\n'.join(lines) + '\n')
    print(outp)
    print(qa)

if __name__ == '__main__':
    main()
