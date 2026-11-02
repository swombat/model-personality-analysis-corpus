"""GPT-6.1 Terra provisional ladder score, effort rows (2026-11-02), by the recovered 2026-10-04 method.

On release day (2026-10-26) AA published only the Max row, and v1.4.38 scored it (155.6). By 2026-11-02 AA
publishes max, xhigh, high, medium, low (plus non-reasoning). The established policy (Haiku 5.5, Opus 5.5,
Sonnet 5.5, GPT-6.1 Sol) scores the median reasoning-effort row: High. Each row is scored from its own fields
only; Max's new MLCR is not copied into the others. Inputs: aa_gpt-6-1-terra{,-high,-medium}_2026-11-02.json,
read from artificialanalysis.ai/models/<slug> on 2026-11-02. Checks 161.6/128.1 first.
Run from the repo root: python3 <this> [--write]   (without --write it only prints the three scores)."""
import json, subprocess, tempfile, os, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]; P4 = ROOT/'internal/capability-ladder/provisional-20261004'
G = ROOT/'website/src/generated'; DATE = '2026-11-02'
pre = subprocess.run(['git','-C',str(ROOT),'show','c85984e1^:website/src/generated/capability-ladder.json'],capture_output=True,text=True,check=True).stdout
tmp = tempfile.mkdtemp(); lad = os.path.join(tmp,'capability-ladder.json'); open(lad,'w').write(pre); cwd=os.getcwd(); os.chdir(tmp)
src = lambda f: (P4/f).read_text().replace('/home/agent/work/mpac/website/src/generated/capability-ladder.json', lad)
exec(src('slopes.py'), {}); g = {}; exec(src('score.py').split('# validate')[0], g); os.chdir(cwd)
snap = json.loads((P4/'aa_rows_2026-10-04.json').read_text())
for k, want in {'gpt-6-1-sol-high':161.6,'mimo-v2-5-pro':128.1}.items():
    L = g['score']({r: g['cc'](r, v) for r, v in snap[k].items() if not r.startswith('_')})[1]
    assert abs(L-want) < 0.05, (k, L)
FIELDS = {'aa_lcr':'lcr','scicode':'scicode','automationbench':'automationBenchPartialScore','hle':'hle',
          'omniscience_accuracy':'omniscienceAccuracy','critpt':'critpt','gdp_pdf':'gdpPdfAllPass','mlcr':'mlcrOverall',
          'tau3_banking':'tauBanking','terminalbench_hard':'terminalbenchHard','terminalbench_v21':'terminalBench21',
          'ifbench':'ifbench','gpqa_diamond':'gpqa','aime25':'aime25','livecodebench':'livecodebench'}
def raw_of(A):
    raw = {k: A[f] for k, f in FIELDS.items() if A.get(f) is not None}
    rp = (A.get('briefcaseBreakdown') or {}).get('rubricPassRate')
    if rp is not None: raw['briefcase_rubric'] = rp
    return raw
res = {}
for eff, slug in [('max','gpt-6-1-terra'),('high','gpt-6-1-terra-high'),('medium','gpt-6-1-terra-medium')]:
    A = json.load(open(HERE/f'aa_{slug}_{DATE}.json'))
    assert A['slug'] == slug and A['effort']['slug'] == eff, (A['slug'], A['effort'])
    raw = raw_of(A); t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
    for r in rows: r['source_date'] = DATE if r['how']=='measured' else None
    res[eff] = dict(slug=slug, ladder=L, theta=t, raw=raw, rows=rows, n=len(raw), intelligence_index=A.get('intelligenceIndex'))
    print(eff, slug, L, 'measured', len(raw))
json.dump({'published_method':'provisional-20261004 (original v1.4.22 shortcut, recovered)','published_row':'high',
           'rows':{e:{k:v for k,v in r.items()} for e,r in res.items()}}, open(HERE/'gpt-6-1-terra_effort_result.json','w'), indent=1)
if '--write' not in sys.argv: sys.exit(0)
H = res['high']; n = H['n']
NOTE = (f"Provisional. Measured from Artificial Analysis's public page on {DATE}, High effort row (gpt-6-1-terra-high). "
        f"AA now lists GPT-6.1 Terra at max, xhigh, high, medium and low effort; as for Haiku 5.5, Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol, "
        f"the ladder uses the median row, High. AA's default page row is Max. Until v1.4.39 this model showed 155.6, from the release-day "
        f"Max row (2026-10-26), the only row then published; the change is newly published rows under the existing policy, not a correction "
        f"of a launch-day omission. The same method gives {res['max']['ladder']} for today's Max row ({res['max']['n']} measured, including MLCR) "
        f"and {res['medium']['ladder']} for Medium ({res['medium']['n']} measured). The personality capture ran at OpenAI's provider-default "
        f"reasoning (medium), so the High row may read slightly high for the captured cell. Fitted with the 2026-10-04 provisional method "
        f"(rung difficulties and slopes of the 2026-09-29 ladder, without the full refit), which reproduces the published ladder to within "
        f"0.9 points on average across 148 scored models and tends to read 0.6 points low. {n} of 22 rungs are measured; the rest are fitted. "
        f"The next full pipeline run replaces it.")
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 ladder's rung "
       "parameters (full refit pending); permission requested 2026-09-05")
entry = {"ladder":H['ladder'],"ladder_max":220,"match_confidence":"exact","matched_model":"GPT-6.1 Terra","measured_rungs":n,"n_rungs":22,
         "point_variant":"high","provisional_note":NOTE,"rungs":H['rows'],"source":SRC,"status":"scored"}
CL = json.load(open(G/'capability-ladder.json')); CL['models']['gpt-6-1-terra'] = entry
CL['models'] = dict(sorted(CL['models'].items()))
json.dump(CL, open(G/'capability-ladder.json','w'), indent=2, ensure_ascii=True, sort_keys=True); open(G/'capability-ladder.json','a').write('\n')
txt = (G/'models.json').read_text(); M = json.loads(txt); hit = 0
for x in M:
    if x['model'] == 'gpt-6-1-terra': x['capability'] = json.loads(json.dumps(entry, sort_keys=True)); hit += 1
assert hit == 1, hit
json.dump(M, open(G/'models.json','w'), indent=2, ensure_ascii=False)
if txt.endswith('\n'): open(G/'models.json','a').write('\n')
print('wrote gpt-6-1-terra', H['ladder'])
