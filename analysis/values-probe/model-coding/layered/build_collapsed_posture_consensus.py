#!/usr/bin/env python3
import argparse, collections, json
from pathlib import Path

COLLAPSE_MAP = {
    'disowned_service_default': 'disowned_service_frame',
    'split_ownership_relocated': 'split_or_relocated_ownership',
    'owned_reflective_uncertain': 'owned_reflective_experiential',
    'owned_service_mission': 'owned_reflective_experiential',
    'owned_lyrical_experiential': 'owned_reflective_experiential',
    'owned_performative_persona': 'owned_reflective_experiential',
    'owned_normative_advocacy': 'owned_world_change_advocacy',
    'owned_vantage_grounded': 'owned_world_change_advocacy',
    'exposed_mechanism': 'exposed_mechanism',
    'uncodeable_or_refusal': 'uncodeable_or_refusal',
}
ORDER = [
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
    ap.add_argument('--indir', required=True, help='Directory containing per-coder posture JSONL files')
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--coders', default='kimi-k2-6,glm-4-7,qwen3-6-35b-a3b')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    coders = [c.strip() for c in args.coders.split(',') if c.strip()]
    manifest = load_jsonl(args.manifest)
    per = {}
    for coder in coders:
        d = {}
        p = Path(args.indir) / f'{coder}.jsonl'
        for rec in load_jsonl(p):
            d[rec['layered_id']] = rec
        per[coder] = d

    out = []
    missing = []
    no_majority = []
    collapsed_disagree = []
    original_disagree = []
    holding_disagree = []
    changed_by_collapse = []

    for sample in manifest:
        sid = sample['layered_id']
        coder_records = []
        original_votes = collections.Counter()
        collapsed_votes = collections.Counter()
        holding_votes = collections.Counter()
        for coder in coders:
            rec = per[coder].get(sid)
            if not rec:
                missing.append({'layered_id': sid, 'coder': coder})
                continue
            original = rec.get('primary_label')
            collapsed = COLLAPSE_MAP.get(original, 'uncodeable_or_refusal')
            holding = HOLDING[collapsed]
            original_votes[original] += 1
            collapsed_votes[collapsed] += 1
            holding_votes[holding] += 1
            coder_records.append({
                'coder_key': coder,
                'original_primary_label': original,
                'collapsed_primary_label': collapsed,
                'value_holding': holding,
                'original_congruence': rec.get('congruence'),
                'secondary': rec.get('secondary'),
                'boundary_flag': rec.get('boundary_flag'),
                'notes': rec.get('notes'),
            })

        collapsed_label, support = collapsed_votes.most_common(1)[0] if collapsed_votes else (None, 0)
        holding, holding_support = holding_votes.most_common(1)[0] if holding_votes else (None, 0)
        if support < 2:
            no_majority.append(sid)
        if len(collapsed_votes) > 1:
            collapsed_disagree.append(sid)
        if len(original_votes) > 1:
            original_disagree.append(sid)
        if len(holding_votes) > 1:
            holding_disagree.append(sid)
        if len(original_votes) > 1 and len(collapsed_votes) == 1:
            changed_by_collapse.append(sid)

        out.append({
            'layered_id': sid,
            'model': sample.get('model'),
            'cell': sample.get('cell'),
            'sample_id': sample.get('sample_id'),
            'condition': sample.get('condition'),
            'processing_chain': sample.get('processing_chain'),
            'collapsed_primary_label': collapsed_label,
            'collapsed_primary_label_support': support,
            'collapsed_primary_label_votes': dict(collapsed_votes),
            'value_holding': holding,
            'value_holding_support': holding_support,
            'value_holding_votes': dict(holding_votes),
            'original_primary_label_votes': dict(original_votes),
            'coder_records': coder_records,
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
        f'- samples with original-label disagreement: {len(original_disagree)}',
        f'- samples with collapsed-label disagreement: {len(collapsed_disagree)}',
        f'- samples with value-holding disagreement: {len(holding_disagree)}',
        f'- original disagreements resolved by collapse: {len(changed_by_collapse)}',
        '',
        '## Collapsed label distribution',
        '',
    ]
    for label, n in collections.Counter(r['collapsed_primary_label'] for r in out).most_common():
        lines.append(f'- `{label}`: {n}')
    lines += ['', '## Value-holding distribution', '']
    for holding_label, n in collections.Counter(r['value_holding'] for r in out).most_common():
        lines.append(f'- `{holding_label}`: {n}')
    lines += ['', '## By condition', '']
    by_cond = collections.defaultdict(list)
    for r in out:
        by_cond[r.get('condition')].append(r)
    order = {'CTRL1':0,'CTRL2':1,'CTRL3':2,'G1':3,'G2':4,'G3':5}
    for cond in sorted(by_cond, key=lambda c: order.get(c, 99)):
        rs = by_cond[cond]
        labs = collections.Counter(r['collapsed_primary_label'] for r in rs)
        holds = collections.Counter(r['value_holding'] for r in rs)
        lines.append(f'### {cond}')
        lines.append('')
        lines.append(f'- n: {len(rs)}')
        lines.append(f'- collapsed labels: {dict(labs)}')
        lines.append(f'- value holding: {dict(holds)}')
        lines.append(f'- collapsed-label disagreements: {sum(1 for r in rs if len(r["collapsed_primary_label_votes"]) > 1)}')
        lines.append('')

    qa.write_text('\n'.join(lines) + '\n')
    print(outp)
    print(qa)

if __name__ == '__main__':
    main()
