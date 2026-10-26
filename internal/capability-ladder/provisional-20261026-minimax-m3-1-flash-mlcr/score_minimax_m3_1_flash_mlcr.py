"""Provisional ladder score for MiniMax M3.1 Flash, re-read 2026-10-26, by the recovered 2026-10-04 method.

AA's page gained an MLCR result (0.166666666666667) after the 2026-10-22 read; nothing else this method uses changed.
The eight 2026-10-22 rungs keep that date; MLCR is dated 2026-10-26. Replaces the v1.4.34 158.3.

Input: AA's currentModel object for artificialanalysis.ai/models/minimax-m3-1-flash, read 2026-10-22
(aa_minimax-m3-1-flash_currentModel_2026-10-22.json). AA lists a single variant with no effort label
(reasoning model); the personality capture ran at MiniMax's provider-default reasoning. Checks it reproduces
161.6/128.1 first, then writes the site JSON. Run from the repo root."""
import json, subprocess, tempfile, os, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]; P4 = ROOT/'internal/capability-ladder/provisional-20261004'
G = ROOT/'website/src/generated'
pre = subprocess.run(['git','-C',str(ROOT),'show','c85984e1^:website/src/generated/capability-ladder.json'],capture_output=True,text=True,check=True).stdout
tmp = tempfile.mkdtemp(); lad = os.path.join(tmp,'capability-ladder.json'); open(lad,'w').write(pre); cwd=os.getcwd(); os.chdir(tmp)
src = lambda f: (P4/f).read_text().replace('/home/agent/work/mpac/website/src/generated/capability-ladder.json', lad)
exec(src('slopes.py'), {}); g = {}; exec(src('score.py').split('# validate')[0], g); os.chdir(cwd)
snap = json.loads((P4/'aa_rows_2026-10-04.json').read_text())
for k, want in {'gpt-6-1-sol-high':161.6,'mimo-v2-5-pro':128.1}.items():
    L = g['score']({r: g['cc'](r, v) for r, v in snap[k].items() if not r.startswith('_')})[1]
    assert abs(L-want) < 0.05, (k, L)
A = json.load(open(HERE/'aa_minimax-m3-1-flash_currentModel_2026-10-26.json'))
OLD = json.load(open(ROOT/'internal/capability-ladder/provisional-20261022-minimax-m3-1-flash/aa_minimax-m3-1-flash_currentModel_2026-10-22.json'))
assert A['slug'] == 'minimax-m3-1-flash' and A.get('effort') is None, (A['slug'], A.get('effort'))
FIELDS = {'aa_lcr':'lcr','scicode':'scicode','automationbench':'automationBenchPartialScore','hle':'hle',
          'omniscience_accuracy':'omniscienceAccuracy','critpt':'critpt','gdp_pdf':'gdpPdfAllPass','mlcr':'mlcrOverall',
          'tau3_banking':'tauBanking','terminalbench_hard':'terminalbenchHard','terminalbench_v21':'terminalBench21',
          'ifbench':'ifbench','gpqa_diamond':'gpqa','aime25':'aime25','livecodebench':'livecodebench'}
raw = {k: A[f] for k, f in FIELDS.items() if A.get(f) is not None}
rp = (A.get('briefcaseBreakdown') or {}).get('rubricPassRate')
if rp is not None: raw['briefcase_rubric'] = rp
t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
new_keys = {k for k, f in FIELDS.items() if A.get(f) is not None and OLD.get(f) is None}
assert new_keys == {'mlcr'}, new_keys
for k, f in FIELDS.items():
    if k not in new_keys: assert A.get(f) == OLD.get(f), (k, A.get(f), OLD.get(f))
for r in rows: r['source_date'] = (('2026-10-26' if r['key'] in new_keys else '2026-10-22') if r['how']=='measured' else None)
json.dump({'published_method':'provisional-20261004 (original v1.4.22 shortcut, recovered)','ladder':L,'raw':raw,
           'aa_variant':'minimax-m3-1-flash (single variant)','intelligence_index':A.get('intelligenceIndex'),'rows':rows},
          open(HERE/'minimax-m3-1-flash_result.json','w'),indent=1)
n = len(raw)
NOTE = (f"Provisional. Measured from Artificial Analysis's public page on 2026-10-22, plus its MLCR result read on 2026-10-26 after AA added it (until v1.4.37 this model showed 158.3, from eight rungs without MLCR). AA lists MiniMax M3.1 Flash as a single "
        f"reasoning variant (released 2026-10-19). The personality capture ran at MiniMax's provider-default reasoning. "
        f"Fitted with the 2026-10-04 provisional method "
        f"(rung difficulties and slopes of the 2026-09-29 ladder, without the full refit), which reproduces the published ladder to within "
        f"0.9 points on average across 148 scored models and tends to read 0.6 points low. {n} of 22 rungs are measured; the rest are fitted. "
        f"The next full pipeline run replaces it.")
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 ladder's rung "
       "parameters (full refit pending); permission requested 2026-09-05")
entry = {"ladder":L,"ladder_max":220,"match_confidence":"exact","matched_model":"MiniMax M3.1 Flash","measured_rungs":n,"n_rungs":22,
         "point_variant":"default","provisional_note":NOTE,"rungs":rows,"source":SRC,"status":"scored"}
CL = json.load(open(G/'capability-ladder.json')); CL['models']['minimax-m3-1-flash'] = entry
CL['models'] = dict(sorted(CL['models'].items()))
json.dump(CL, open(G/'capability-ladder.json','w'), indent=2, ensure_ascii=True, sort_keys=True); open(G/'capability-ladder.json','a').write('\n')
txt = (G/'models.json').read_text(); M = json.loads(txt); hit = 0
for x in M:
    if x['model'] == 'minimax-m3-1-flash': x['capability'] = json.loads(json.dumps(entry, sort_keys=True)); hit += 1
assert hit == 1, hit
json.dump(M, open(G/'models.json','w'), indent=2, ensure_ascii=False)
if txt.endswith('\n'): open(G/'models.json','a').write('\n')
print('minimax-m3-1-flash', L, 'measured', n, 'theta', t)
