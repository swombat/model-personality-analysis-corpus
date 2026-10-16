"""Provisional ladder score for Muse Spark Open (2026-10-16), by the recovered 2026-10-04 method.

Input: AA's currentModel object for artificialanalysis.ai/models/muse-spark-open, read 2026-10-16
(aa_muse-spark-open_currentModel_2026-10-16.json). AA publishes one row for Muse Spark Open, at
xhigh effort. The personality capture ran through Modal at its provider-default reasoning (Meta
serves no OpenRouter endpoint), so the effort match is unverified; flagged in the note. Same method as the v1.4.27 precedent: checks it reproduces 161.6/128.1 first, then writes the site JSON.
Run from the repo root."""
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
A = json.load(open(HERE/'aa_muse-spark-open_currentModel_2026-10-16.json'))
assert A['slug'] == 'muse-spark-open' and A['effort']['slug'] == 'xhigh', (A['slug'], A['effort'])
FIELDS = {'aa_lcr':'lcr','scicode':'scicode','automationbench':'automationBenchPartialScore','hle':'hle',
          'omniscience_accuracy':'omniscienceAccuracy','critpt':'critpt','gdp_pdf':'gdpPdfAllPass','mlcr':'mlcrOverall',
          'tau3_banking':'tauBanking','terminalbench_hard':'terminalbenchHard','terminalbench_v21':'terminalBench21',
          'ifbench':'ifbench','gpqa_diamond':'gpqa','aime25':'aime25','livecodebench':'livecodebench'}
raw = {k: A[f] for k, f in FIELDS.items() if A.get(f) is not None}
rp = (A.get('briefcaseBreakdown') or {}).get('rubricPassRate')
if rp is not None: raw['briefcase_rubric'] = rp
t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
for r in rows: r['source_date'] = '2026-10-16' if r['how']=='measured' else None
json.dump({'published_method':'provisional-20261004 (original v1.4.22 shortcut, recovered)','ladder':L,'raw':raw,
           'aa_variant':'muse-spark-open (xhigh)','intelligence_index':A.get('intelligenceIndex'),'rows':rows},
          open(HERE/'muse-spark-open_result.json','w'),indent=1)
n = len(raw)
NOTE = (f"Provisional. Measured from Artificial Analysis's public page on 2026-10-16, which lists one row for Muse Spark Open, at xhigh effort "
        f"(released 2026-10-15). The personality capture ran through Modal, a third-party host, at its provider-default reasoning, so the effort "
        f"behind these scores may not match the captured cell. Fitted with the 2026-10-04 provisional method "
        f"(rung difficulties and slopes of the 2026-09-29 ladder, without the full refit), which reproduces the published ladder to within "
        f"0.9 points on average across 148 scored models and tends to read 0.6 points low. {n} of 22 rungs are measured; the rest are fitted. "
        f"The next full pipeline run replaces it.")
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 ladder's rung "
       "parameters (full refit pending); permission requested 2026-09-05")
entry = {"ladder":L,"ladder_max":220,"match_confidence":"exact","matched_model":"Muse Spark Open","measured_rungs":n,"n_rungs":22,
         "point_variant":"xhigh","provisional_note":NOTE,"rungs":rows,"source":SRC,"status":"scored"}
CL = json.load(open(G/'capability-ladder.json')); CL['models']['muse-spark-open'] = entry
CL['models'] = dict(sorted(CL['models'].items()))
json.dump(CL, open(G/'capability-ladder.json','w'), indent=2, ensure_ascii=True, sort_keys=True); open(G/'capability-ladder.json','a').write('\n')
txt = (G/'models.json').read_text(); M = json.loads(txt); hit = 0
for x in M:
    if x['model'] == 'muse-spark-open': x['capability'] = json.loads(json.dumps(entry, sort_keys=True)); hit += 1
assert hit == 1, hit
json.dump(M, open(G/'models.json','w'), indent=2, ensure_ascii=False)
if txt.endswith('\n'): open(G/'models.json','a').write('\n')
print('muse-spark-open', L, 'measured', n, 'theta', t)
