"""Google Gemini 4 Carbon provisional ladder score (2026-11-11), by the recovered 2026-10-04 method.
Adapted from provisional-20261110-muse-ember/score_muse_ember.py. AA lists one full row, Gemini 4 Carbon (High),
its default; the capture ran at Google's provider-default reasoning. Writes gemini-4-carbon_result.json and
gemini-4-carbon_entry.json beside itself."""
import json, subprocess, tempfile, os, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.path.expanduser('~/work/mpac')); P4 = ROOT/'internal/capability-ladder/provisional-20261004'
DATE = '2026-11-11'
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

A = json.load(open(HERE/f'aa_gemini-4-carbon_{DATE}.json'))
assert A['slug'] == 'gemini-4-carbon' and A['effort']['slug'] == 'high', (A['slug'], A['effort'])
raw = raw_of(A); n = len(raw); assert n >= 3, raw
t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
for r in rows: r['source_date'] = DATE if r['how']=='measured' else None
print('high', L, 'measured', n, sorted(raw))
json.dump({'published_method':'provisional-20261004 (original v1.4.22 shortcut, recovered)','published_row':'high',
           'ladder':L,'theta':t,'raw':raw,'aa_variant':'gemini-4-carbon (high)','intelligence_index':A.get('intelligenceIndex'),'rows':rows},
          open(HERE/'gemini-4-carbon_result.json','w'),indent=1)
NOTE = (f"Provisional. Measured from Artificial Analysis's public page on {DATE}, High effort row (gemini-4-carbon), AA's default and the only full row. "
        f"The personality capture ran at Google's provider-default reasoning. "
        f"Fitted with the 2026-10-04 provisional method (rung difficulties and slopes of the 2026-09-29 ladder, without the full refit), which reproduces the published ladder to within "
        f"0.9 points on average across 148 scored models and tends to read 0.6 points low. {n} of 22 rungs are measured; the rest are fitted, so this score is less certain than most. "
        f"The next full pipeline run replaces it.")
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 ladder's rung "
       "parameters (full refit pending); permission requested 2026-09-05")
entry = {"ladder":L,"ladder_max":220,"match_confidence":"exact","matched_model":"Gemini 4 Carbon","measured_rungs":n,"n_rungs":22,
         "point_variant":"high","provisional_note":NOTE,"rungs":rows,"source":SRC,"status":"scored"}
json.dump(entry, open(HERE/'gemini-4-carbon_entry.json','w'), indent=2, ensure_ascii=True, sort_keys=True)
