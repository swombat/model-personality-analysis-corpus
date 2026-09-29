#!/usr/bin/env python3
"""Scoped Sonnet 5.5 generation; preserve older cached pages on partial checkouts.
Run from any cwd. Uses existing generator, committed metadata and sibling v2 corpus.
Run generate_map.py separately: it uses the preserved public sample bundles,
not missing older canonical values. See the Sonnet handoff.
"""
import json, shutil, tempfile
from pathlib import Path
import generate_data as g

def main():
    target = 'sonnet-5-5'
    original = json.loads((g.GENERATED/'models.json').read_text())
    rows = [r for r in json.loads(g.PROFILE_INDEX.read_text()) if r['model']==target]
    assert len(rows)==1
    destination, samples = g.GENERATED, g.PUBLIC_SAMPLES
    with tempfile.TemporaryDirectory(prefix='sonnet55-') as tmp:
        tmp = Path(tmp)
        shutil.copytree(destination,tmp/'generated')
        (tmp/'index.json').write_text(json.dumps(rows))
        g.PROFILE_INDEX=tmp/'index.json';g.GENERATED=tmp/'generated';g.PUBLIC_SAMPLES=tmp/'samples'
        g.main()
        generated=json.loads((g.GENERATED/'models.json').read_text());assert len(generated)==1
        m=generated[0];assert m['model']==target and m['lab']=='Anthropic'
        assert m['analyzed_freeflow_samples']==125 and m['analyzed_values_samples']==120
        assert m['published_freeflow_samples']==125 and m['published_values_samples']==120
        assert 'No layered values-probe analysis' not in m['values_summary_markdown']
        assert m['openrouter']['id']=='anthropic/claude-sonnet-5.5'
        combined=[r for r in original if r['model']!=target]+generated
        combined.sort(key=lambda m:(m['lab'],m['model']))
        assert {r['model']:r for r in original if r['model']!=target}=={r['model']:r for r in combined if r['model']!=target}
        (destination/'models.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2))
        shutil.copy2(g.PUBLIC_SAMPLES/f'{target}.json',samples/f'{target}.json')
        print('Only Sonnet 5.5 added/refreshed; all other model objects preserved.')
if __name__=='__main__':main()
