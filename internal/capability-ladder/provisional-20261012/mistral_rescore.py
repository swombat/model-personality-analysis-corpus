"""Re-score Mistral Large 4 with the recovered 2026-10-04 provisional method (v1.4.26).

Method reconciliation, not new benchmark evidence: the inputs are the AA row Mistral was
scored from on 2026-10-07 (../provisional-20261007/aa_mistral-large-4_currentModel_2026-10-07.json),
unchanged. v1.4.23 fitted them with the 2026-10-07 rebuild (143.3); this applies the original
2026-10-04 method (../provisional-20261004/), the one used for GPT-6.1 Sol, MiMo-V2.5-Pro and
Claude Haiku 5.5, so every provisional score uses one method until the full refresh.
Checks the method reproduces 161.6/128.1 first, then writes the site JSON.
Run from the repo root."""
import json, subprocess, tempfile, os, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]; P4 = ROOT/'internal/capability-ladder/provisional-20261004'
G = ROOT/'website/src/generated'
pre = subprocess.run(['git','-C',str(ROOT),'show','c85984e1^:website/src/generated/capability-ladder.json'],capture_output=True,text=True,check=True).stdout
tmp = tempfile.mkdtemp(); lad = os.path.join(tmp,'capability-ladder.json'); open(lad,'w').write(pre); cwd=os.getcwd(); os.chdir(tmp)
src = lambda f: (P4/f).read_text().replace('/home/agent/work/mpac/website/src/generated/capability-ladder.json', lad)
exec(src('slopes.py'), {}); g = {}; exec(src('score.py').split('# validate')[0], g); os.chdir(cwd)
snap = json.loads((P4/'aa_rows_2026-10-04.json').read_text())
for k, want in {'gpt-6-1-sol-high':161.6,'mimo-v2-5-pro':128.1}.items():
    L = g['score']({r: g['cc'](r, v) for r, v in snap[k].items() if not r.startswith('_')})[1]
    assert abs(L-want) < 0.05, (k, L)
A = json.load(open(ROOT/'internal/capability-ladder/provisional-20261007/aa_mistral-large-4_currentModel_2026-10-07.json'))
raw = {'aa_lcr':A['lcr'],'scicode':A['scicode'],'automationbench':A['automationBenchPartialScore'],
       'briefcase_rubric':A['briefcaseBreakdown']['rubricPassRate'],'hle':A['hle'],
       'omniscience_accuracy':A['omniscienceAccuracy'],'critpt':A['critpt'],'gdp_pdf':A['gdpPdfAllPass']}
t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
assert L == 146.5, L
for r in rows: r['source_date'] = '2026-10-07' if r['how']=='measured' else None
json.dump({'published_method':'provisional-20261004 (original v1.4.22 shortcut, recovered)','ladder':L,'raw':raw,
           'previous_published':143.3,'previous_method':'provisional-20261007 rebuild (v1.4.23)','rows':rows},
          open(pathlib.Path(__file__).with_name('mistral-large-4-0_result_20261004_method.json'),'w'),indent=1)
NOTE = ("Provisional. Measured from Artificial Analysis's public page on 2026-10-07, where the model is listed as Mistral Large 4 Preview "
        "(released 2026-10-06, one reasoning row), and fitted with the 2026-10-04 provisional method (rung difficulties and slopes of the "
        "2026-09-29 ladder, without the full refit), which reproduces the published ladder to within 0.9 points on average across 148 scored "
        "models and tends to read 0.6 points low. Until v1.4.26 this model showed 143.3, from the 2026-10-07 rebuilt variant of that shortcut; "
        "the change to 146.5 is method reconciliation on the same inputs, not new benchmark evidence. Several Artificial Analysis benchmarks "
        "(MLCR, τ³-Banking, Terminal-Bench Hard and 2.1, IFBench, GPQA) are not yet published for this model, so 14 of 22 rungs are fitted. "
        "The next full pipeline run replaces it.")
CL = json.load(open(G/'capability-ladder.json')); e = CL['models']['mistral-large-4-0']
e.update(ladder=L, rungs=rows, provisional_note=NOTE)
json.dump(CL, open(G/'capability-ladder.json','w'), indent=2, ensure_ascii=True, sort_keys=True); open(G/'capability-ladder.json','a').write('\n')
txt = (G/'models.json').read_text(); M = json.loads(txt)
for x in M:
    if x['model'] == 'mistral-large-4-0': x['capability'] = json.loads(json.dumps(e, sort_keys=True))
json.dump(M, open(G/'models.json','w'), indent=2, ensure_ascii=False)
if txt.endswith('\n'): open(G/'models.json','a').write('\n')
print('mistral-large-4-0', L)
