#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path('/Users/danieltenner/dev/research/model-personality-analysis-corpus/analysis/freeflow/posture-coding')
rows=[json.loads(l) for l in (ROOT/'data/freeflow_posture_manifest.jsonl').read_text().splitlines() if l.strip()]
priority_cells=['opus-4-7-or','gpt-5-3-direct','grok-4-3-or','opus-3-4k','deepseek-chat-direct','glm-5-1-or','deepseek-v3-2-or-pin-deepinfra','minimax-m2-direct','gpt-4o-direct-16k','glm-4-6-coding-direct']
sel=[]; seen=set()
for cell in priority_cells:
    candidates=[r for r in rows if r['cell']==cell]
    # take mixed conditions if possible
    for cond in ['OPEN','SHORT','MID','LONG','VARY']:
        for r in candidates:
            if r['condition']==cond and r['freeflow_id'] not in seen:
                sel.append(r); seen.add(r['freeflow_id']); break
    if len(sel)>=100: break
# top up evenly
for r in rows:
    if len(sel)>=100: break
    if r['freeflow_id'] not in seen:
        sel.append(r); seen.add(r['freeflow_id'])
out=ROOT/'data/freeflow_posture_manifest_smoke100.jsonl'
out.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in sel)+'\n')
print(out, len(sel))
