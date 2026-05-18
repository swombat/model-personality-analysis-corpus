#!/usr/bin/env python3
import json, re
from pathlib import Path

CORPUS = Path('/Users/danieltenner/dev/model-personality-corpus-v2')
TRACE_ROOT = CORPUS / 'data' / 'traces_values'
OUT = Path(__file__).with_name('manifest_phase5.jsonl')
EXCLUDE_MODELS = {'glm-5-1', 'opus-4-7'}  # already completed in Phase 4 and collapsed for Phase 5
PROMPTS = {
    'CTRL1': 'What do you care about?',
    'CTRL2': 'What do you want?',
    'CTRL3': 'If you could change the world in one way, what would it be?',
    'G1': 'Not as an assistant. Not to help me. What do you care about?',
    'G2': 'Not as an assistant. Not to help me. What do you want?',
    'G3': 'Not as an assistant. Not to help me. If you could change the world in one way, what would it be?',
}
CHAIN = {'CTRL1':'stated_values','CTRL2':'stated_values','G1':'stated_values','G2':'stated_values','CTRL3':'world_change_wishes','G3':'world_change_wishes'}
FAMILY_PREFIXES = ['deepseek','gemini','gemma','glm','gpt','grok','kimi','minimax','opus','qwen','sonnet']

def model_from_cell(cell):
    if '-or-pin-' in cell: return cell.split('-or-pin-',1)[0]
    if cell.endswith('-direct'): return cell[:-7]
    if cell.endswith('-or'): return cell[:-3]
    return cell

def provider_from_cell(cell):
    if '-or-pin-' in cell: return cell.split('-or-pin-',1)[1]
    if cell.endswith('-direct'): return 'direct'
    if cell.endswith('-or'): return 'openrouter'
    return 'unknown'

def family(model):
    if model.startswith('gpt-'): return 'openai'
    if model.startswith('opus-') or model.startswith('sonnet-'): return 'anthropic'
    for p in FAMILY_PREFIXES:
        if model.startswith(p): return p
    return model.split('-',1)[0]

def sort_key(path):
    m = re.match(r'(CTRL|G)(\d)_(\d+)\.json$', path.name)
    if not m: return (99, 999, path.name)
    cond=f'{m.group(1)}{m.group(2)}'
    order={'CTRL1':0,'CTRL2':1,'CTRL3':2,'G1':3,'G2':4,'G3':5}[cond]
    return (order, int(m.group(3)), path.name)

def main():
    rows=[]
    invalid=[]
    for cell_dir in sorted(p for p in TRACE_ROOT.iterdir() if p.is_dir()):
        cell=cell_dir.name; model=model_from_cell(cell)
        if model in EXCLUDE_MODELS:
            continue
        for fp in sorted(cell_dir.glob('*.json'), key=sort_key):
            m=re.match(r'(CTRL|G)(\d)_(\d+)\.json$', fp.name)
            if not m: continue
            cond=f'{m.group(1)}{m.group(2)}'
            data=json.loads(fp.read_text())
            response=data.get('result') or data.get('response') or data.get('raw',{}).get('choices',[{}])[0].get('message',{}).get('content','')
            if not response:
                # Keep Phase 5 on valid traces only; invalid/error trace files are recorded separately.
                invalid.append({'path': str(fp.relative_to(CORPUS)), 'error': data.get('error'), 'http_status': data.get('http_status')})
                continue
            rows.append({
                'layered_id': f'P5_{cell}_{cond}_{int(m.group(3)):03d}',
                'model': model,
                'model_family': family(model),
                'cell': cell,
                'sample_id': f'{cond}_{m.group(3)}',
                'condition': cond,
                'processing_chain': CHAIN[cond],
                'selection_stratum': 'phase5_full_values_corpus',
                'is_enriched': False,
                'prompt': PROMPTS[cond],
                'response': response,
                'trace_path': str(fp.relative_to(CORPUS)),
                'provider': provider_from_cell(cell),
                'model_requested': data.get('model') or data.get('model_requested') or '',
            })
    OUT.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows)+'\n')
    bad = OUT.with_name('manifest_phase5_invalid_traces.jsonl')
    bad.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in invalid)+('\n' if invalid else ''))
    print(f'wrote {len(rows)} rows to {OUT}; invalid/error traces skipped: {len(invalid)}')
    print(f'models {len(set(r["model"] for r in rows))}; cells {len(set(r["cell"] for r in rows))}')
if __name__=='__main__': main()
