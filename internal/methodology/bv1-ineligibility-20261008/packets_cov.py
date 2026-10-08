import importlib.util,sys,json,csv
from pathlib import Path
W=Path('/home/agent/work/mpac-linefix'); S=Path(sys.argv[1])
sys.path.insert(0,'/home/agent/work/mpc-inelig/scripts/capture_harness'); import ineligibility as INEL
cell='haiku-5-5-or-pin-anthropic'; model='anthropic/claude-haiku-5.5'
rows=list(csv.DictReader(open(S/'haiku_manifest.tsv'),delimiter='\t'))
keep=[r for r in rows if Path(r['sample_id']).stem!='MID_15']
with open(S/'haiku_124.tsv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter='\t');w.writeheader();w.writerows(keep)
cov=INEL.coverage([dict(sample_id=r['sample_id'],**({'ineligible':True,'receipt_sha256':'x'} if Path(r['sample_id']).stem=='MID_15' else {})) for r in rows],[Path(r['sample_id']).stem for r in rows])
def run(coverage,manifest):
    s=importlib.util.spec_from_file_location('pn',W/'analysis/values-probe/model-coding/layered/phase35_union_alpha_20260917/build_aggregate_packets.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.PHASE=W; m.MANIFEST=manifest; m.ROOT=W; m.CELLS={cell:model}; m.COVERAGE=coverage
    old=sys.argv; sys.argv=[old[0]]
    try: m.main()
    finally: sys.argv=old
run(cov,S/'haiku_124.tsv')
out=W/'analysis/freeflow/personality-aggregates'/cell
meta=json.loads((out/'packet.metadata.json').read_text())
print('samples',meta['samples'],'expected',meta.get('bv1_expected'),'ineligible',[i['sample'] for i in meta['bv1_ineligible']])
print([l for l in (out/'packet.md').read_text().splitlines() if 'BV1 analysis' in l][0][:260])
bad=dict(cov,evaluated_ids=sorted(cov['evaluated_ids'][1:]+['MID_15']))
try: run(bad,S/'haiku_124.tsv'); print('MISMATCH NOT CAUGHT')
except RuntimeError as e: print('mismatch rejected:',e)
try: run(None,S/'haiku_124.tsv'); print('124 WITHOUT COVERAGE NOT CAUGHT')
except RuntimeError as e: print('124 without coverage rejected:',e)
