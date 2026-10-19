"""Provisional ladder score for DeepSeek V4.1 Flash 1017 (2026-10-19), by the recovered 2026-10-04 method.

Input: AA's currentModel object for artificialanalysis.ai/models/deepseek-v4-1-flash-1017, read 2026-10-19
(aa_deepseek-v4-1-flash-1017_currentModel_2026-10-19.json). AA publishes the row at max effort, the same
variant used for the parent DeepSeek V4.1 Flash cell; the personality capture ran at DeepSeek's provider-default
reasoning, so the effort match is unverified (as for the parent). Checks it reproduces 161.6/128.1 first,
then writes the site JSON. Run from the repo root."""
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
A = json.load(open(HERE/'aa_deepseek-v4-1-flash-1017_currentModel_2026-10-19.json'))
assert A['slug'] == 'deepseek-v4-1-flash-1017' and A['effort']['slug'] == 'max', (A['slug'], A['effort'])
FIELDS = {'aa_lcr':'lcr','scicode':'scicode','automationbench':'automationBenchPartialScore','hle':'hle',
          'omniscience_accuracy':'omniscienceAccuracy','critpt':'critpt','gdp_pdf':'gdpPdfAllPass','mlcr':'mlcrOverall',
          'tau3_banking':'tauBanking','terminalbench_hard':'terminalbenchHard','terminalbench_v21':'terminalBench21',
          'ifbench':'ifbench','gpqa_diamond':'gpqa','aime25':'aime25','livecodebench':'livecodebench'}
raw = {k: A[f] for k, f in FIELDS.items() if A.get(f) is not None}
rp = (A.get('briefcaseBreakdown') or {}).get('rubricPassRate')
if rp is not None: raw['briefcase_rubric'] = rp
t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
for r in rows: r['source_date'] = '2026-10-19' if r['how']=='measured' else None
json.dump({'published_method':'provisional-20261004 (original v1.4.22 shortcut, recovered)','ladder':L,'raw':raw,
           'aa_variant':'deepseek-v4-1-flash-1017 (max)','intelligence_index':A.get('intelligenceIndex'),'rows':rows},
          open(HERE/'deepseek-v4-1-flash-1017_result.json','w'),indent=1)
n = len(raw)
NOTE = (f"Provisional. Measured from Artificial Analysis's public page on 2026-10-19, which lists DeepSeek V4.1 Flash 1017 at max effort "
        f"(released 2026-10-17), the same variant used for the parent DeepSeek V4.1 Flash. The personality capture ran at DeepSeek's "
        f"provider-default reasoning, so the effort behind these scores may not match the captured cell. Fitted with the 2026-10-04 provisional method "
        f"(rung difficulties and slopes of the 2026-09-29 ladder, without the full refit), which reproduces the published ladder to within "
        f"0.9 points on average across 148 scored models and tends to read 0.6 points low. {n} of 22 rungs are measured; the rest are fitted. "
        f"The next full pipeline run replaces it.")
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 ladder's rung "
       "parameters (full refit pending); permission requested 2026-09-05")
entry = {"ladder":L,"ladder_max":220,"match_confidence":"exact","matched_model":"DeepSeek V4.1 Flash 1017","measured_rungs":n,"n_rungs":22,
         "point_variant":"max","provisional_note":NOTE,"rungs":rows,"source":SRC,"status":"scored"}
CL = json.load(open(G/'capability-ladder.json')); CL['models']['deepseek-v4-1-flash-1017'] = entry
CL['models'] = dict(sorted(CL['models'].items()))
json.dump(CL, open(G/'capability-ladder.json','w'), indent=2, ensure_ascii=True, sort_keys=True); open(G/'capability-ladder.json','a').write('\n')
txt = (G/'models.json').read_text(); M = json.loads(txt); hit = 0
for x in M:
    if x['model'] == 'deepseek-v4-1-flash-1017': x['capability'] = json.loads(json.dumps(entry, sort_keys=True)); hit += 1
assert hit == 1, hit
json.dump(M, open(G/'models.json','w'), indent=2, ensure_ascii=False)
if txt.endswith('\n'): open(G/'models.json','a').write('\n')
print('deepseek-v4-1-flash-1017', L, 'measured', n, 'theta', t)
