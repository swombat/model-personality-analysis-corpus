"""Claude Fable 5.2 provisional ladder score, effort rows (2026-11-09), by the recovered 2026-10-04 method.
Adapted from provisional-20261102-gpt-6-1-terra-effort/score_gpt_6_1_terra_effort.py. Policy (2026-11-02): score the
High row. Each row is scored from its own fields only. Scratch version: reads ~/work/mpac read-only, writes only
fable-5-2_result.json and fable-5-2_entry.json beside itself."""
import json, subprocess, tempfile, os, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.path.expanduser('~/work/mpac')); P4 = ROOT/'internal/capability-ladder/provisional-20261004'
DATE = '2026-11-09'
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
for eff, slug in [('max','claude-fable-5-2'),('high','claude-fable-5-2-high'),('medium','claude-fable-5-2-medium')]:
    A = json.load(open(HERE/(f'aa_{slug}_{DATE}.json')))
    assert A['slug'] == slug and A['effort']['slug'] == eff, (A['slug'], A['effort'])
    raw = raw_of(A)
    if len(raw) < 3: print(eff, 'unscored'); continue
    t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
    for r in rows: r['source_date'] = DATE if r['how']=='measured' else None
    res[eff] = dict(slug=slug, ladder=L, theta=t, raw=raw, rows=rows, n=len(raw), intelligence_index=A.get('intelligenceIndex'))
    print(eff, slug, L, 'measured', len(raw), sorted(raw))
H = res['high']; n = H['n']
json.dump({'published_method':'provisional-20261004 (original v1.4.22 shortcut, recovered)','published_row':'high',
           'ladder':H['ladder'],'raw':H['raw'],'aa_variant':'claude-fable-5-2-high (high)','intelligence_index':H['intelligence_index'],
           'rows':H['rows'],'all_efforts':{e:{k:v for k,v in r.items() if k!='rows'} for e,r in res.items()}},
          open(HERE/'fable-5-2_result.json','w'),indent=1)
NOTE = (f"Provisional. Measured from Artificial Analysis's public page on {DATE}, High effort row (claude-fable-5-2-high). "
        f"AA lists Claude Fable 5.2 at max, xhigh, high, medium and low effort; as for Haiku 5.5, Opus 5.5, Sonnet 5.5, GPT-6.1 Sol and GPT-6.1 Terra, "
        f"the ladder uses the median row, High. AA's default page row is Max; the same method gives {res['max']['ladder']} for the Max row "
        f"({res['max']['n']} measured) and {res['medium']['ladder']} for Medium ({res['medium']['n']} measured). Each row is scored from its own fields only. "
        f"The personality capture ran at the provider default, so the High row may not match the captured cell. Fitted with the 2026-10-04 provisional method "
        f"(rung difficulties and slopes of the 2026-09-29 ladder, without the full refit), which reproduces the published ladder to within "
        f"0.9 points on average across 148 scored models and tends to read 0.6 points low. {n} of 22 rungs are measured; the rest are fitted. "
        f"The next full pipeline run replaces it.")
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 ladder's rung "
       "parameters (full refit pending); permission requested 2026-09-05")
entry = {"ladder":H['ladder'],"ladder_max":220,"match_confidence":"exact","matched_model":"Claude Fable 5.2","measured_rungs":n,"n_rungs":22,
         "point_variant":"high","provisional_note":NOTE,"rungs":H['rows'],"source":SRC,"status":"scored"}
json.dump(entry, open(HERE/'fable-5-2_entry.json','w'), indent=2, ensure_ascii=True, sort_keys=True)
