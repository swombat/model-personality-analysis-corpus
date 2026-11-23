"""Refresh Hydrogen High, Qwen4 Max (xhigh) and Gemini 4 Neon High from AA's initialModels rows (2026-11-23).

Mira's 2026-11-23 review (YRyzbr): AA now publishes mlcrOverall on the exact Hydrogen High and Qwen4 Max xhigh rows
(previously fitted), and revised Neon High's MLCR (0.283333 -> 0.288889). Same admission rule as
provisional-20261116-initialmodels/update.py: exact slug, own release, release date and effort, exactly one row,
saved verbatim. Same recovered 2026-10-04 method; Sol High 161.6 / MiMo 128.1 guard checked before scoring.
Briefcase Elo is never used (only rubricPassRate is a ladder input). Also measures how far a fit on the four rungs
these models now share (AutomationBench, Omniscience accuracy, GDP.pdf, MLCR) strays from the all-rung fit, for models
at 150+ whose rows include all four (four_rung_bias.json). Replaces the three existing *scored* entries in
capability-ladder.json (text splice) and their models.json capability objects.
Run from the repo root: python3 <this> [--write]
"""
import hashlib, json, os, pathlib, re, subprocess, sys, tempfile, urllib.request, statistics, io, contextlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]; P4 = ROOT / 'internal/capability-ladder/provisional-20261004'
G = ROOT / 'website/src/generated'; DATE = '2026-11-23'
def save(name, value): (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

# (site slug, AA row slug, AA release slug, release date, effort, display name)
TARGETS = [('gemini-4-hydrogen', 'gemini-4-hydrogen-high', 'gemini-4-hydrogen', '2026-11-12', 'high', 'Gemini 4 Hydrogen'),
           ('qwen4-max', 'qwen4-max', 'qwen4-max', '2026-11-16', 'xhigh', 'Qwen4 Max'),
           ('gemini-4-neon', 'gemini-4-neon-high', 'gemini-4-neon', '2026-11-18', 'high', 'Gemini 4 Neon')]
receipts, rows_by_site, siblings = {}, {}, {}
for site, aa, rel, rdate, eff, name in TARGETS:
    url = 'https://artificialanalysis.ai/models/' + rel
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as r:
        body = r.read(); status = r.status; final = r.url
    html = body.decode()
    flight = ''.join(json.loads(c) for c in re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', html))
    marks = list(re.finditer(r'"initialModels"\s*:', flight)); assert len(marks) == 1, (aa, len(marks))
    arr, _ = json.JSONDecoder().raw_decode(flight[marks[0].end():])
    hits = [x for x in arr if isinstance(x, dict) and x.get('slug') == aa]
    assert len(hits) == 1, (aa, len(hits)); A = hits[0]
    assert (A.get('release') or {}).get('slug') == rel, A.get('release')
    assert A.get('releaseDate') == rdate, A.get('releaseDate')
    assert (A.get('effort') or {}).get('slug') == eff, A.get('effort')
    siblings[site] = sorted(((x.get('effort') or {}).get('slug'), x['slug']) for x in arr
                            if isinstance(x, dict) and (x.get('release') or {}).get('slug') == rel)
    receipts[aa] = dict(url=url, final_url=final, http_status=status, fetched_date=DATE, html_bytes=len(body),
                        html_sha256=hashlib.sha256(body).hexdigest(), title=re.search(r'<title>(.*?)</title>', html).group(1),
                        decoded_flight_bytes=len(flight.encode()), currentModel_count=len(re.findall(r'"currentModel"\s*:', flight)),
                        initialModels_len=len(arr), exact_row_count=len(hits), same_release_rows=siblings[site])
    save(f'aa_{aa}_initialModels_row_{DATE}.json', A); rows_by_site[site] = A
save('fetch_receipts.json', receipts)

pre = subprocess.run(['git', '-C', str(ROOT), 'show', 'c85984e1^:website/src/generated/capability-ladder.json'],
                     capture_output=True, text=True, check=True).stdout
tmp = tempfile.mkdtemp(); lad = os.path.join(tmp, 'capability-ladder.json'); open(lad, 'w').write(pre); cwd = os.getcwd(); os.chdir(tmp)
src = lambda f: (P4 / f).read_text().replace('/home/agent/work/mpac/website/src/generated/capability-ladder.json', lad)
with contextlib.redirect_stdout(io.StringIO()):
    exec(src('slopes.py'), {}); g = {}; exec(src('score.py').split('# validate')[0], g)
os.chdir(cwd)
snap = json.loads((P4 / 'aa_rows_2026-10-04.json').read_text())
for k, want in {'gpt-6-1-sol-high': 161.6, 'mimo-v2-5-pro': 128.1}.items():
    L = g['score']({r: g['cc'](r, v) for r, v in snap[k].items() if not r.startswith('_')})[1]
    assert abs(L - want) < 0.05, (k, L)
print('guard ok')

# four-rung bias, same construction as provisional-20261116-initialmodels/three_rung_bias.py
lad_now = json.loads((G / 'capability-ladder.json').read_text())['models']
K4 = ('automationbench', 'omniscience_accuracy', 'gdp_pdf', 'mlcr'); out = []
for k, v in lad_now.items():
    if not v.get('ladder') or k in ('gemini-4-hydrogen', 'qwen4-max', 'gemini-4-neon', 'glm-5-3-flashx'): continue
    d = {x['key']: x['points'] / 10 for x in v.get('rungs', []) if x['how'] == 'measured'}
    if all(n in d for n in K4) and v.get('measured_rungs', 0) >= 6:
        full = g['score']({n: g['cc'](n, val) for n, val in d.items()})[1]
        four = g['score']({n: g['cc'](n, d[n]) for n in K4})[1]
        out.append(dict(model=k, published=v['ladder'], refit_all=full, four_only=four, delta=round(four - full, 2), measured=v['measured_rungs']))
fr = [o['delta'] for o in out if o['published'] >= 150]
bias = dict(rungs=K4, all=dict(n=len(out), median=round(statistics.median([o['delta'] for o in out]), 2)),
            published_150_plus=dict(n=len(fr), median=round(statistics.median(fr), 2), min=min(fr), max=max(fr)), rows=out)
save('four_rung_bias.json', bias); print('four-rung bias 150+', bias['published_150_plus'], 'all', bias['all'])
B = bias['published_150_plus']

FIELDS = {'aa_lcr': 'lcr', 'scicode': 'scicode', 'automationbench': 'automationBenchPartialScore', 'hle': 'hle',
          'omniscience_accuracy': 'omniscienceAccuracy', 'critpt': 'critpt', 'gdp_pdf': 'gdpPdfAllPass', 'mlcr': 'mlcrOverall',
          'tau3_banking': 'tauBanking', 'terminalbench_hard': 'terminalbenchHard', 'terminalbench_v21': 'terminalBench21',
          'ifbench': 'ifbench', 'gpqa_diamond': 'gpqa', 'aime25': 'aime25', 'livecodebench': 'livecodebench'}
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 "
       "ladder's rung parameters (full refit pending); permission requested 2026-09-05")
METHOD = ("Fitted with the 2026-10-04 provisional method (rung difficulties and slopes of the 2026-09-29 ladder, without the "
          "full refit), which reproduces the published ladder to within 0.9 points on average across 148 scored models and "
          "tends to read 0.6 points low.")
WHY = {'gemini-4-hydrogen': "High effort row (gemini-4-hydrogen-high), Google's provider-default effort, which the capture used; AA also lists xhigh (its default page), medium and low, and xhigh is not substituted.",
       'qwen4-max': "AA lists Qwen4 Max at one effort only, xhigh, so that row is used. The personality capture ran at Alibaba's provider default, which is not established to be xhigh, so the score may not match the captured cell.",
       'gemini-4-neon': "High thinking-level row (gemini-4-neon-high), Google's default, which the capture used (provider-default reasoning); AA also lists low, medium and xhigh (its default page is xhigh), and those are not substituted."}
CHANGE = {'gemini-4-hydrogen': "Refreshed on {d}: AA now publishes MLCR on this row ({m}), which was previously fitted; the score was {old} from three measured rungs (v1.4.46).",
          'qwen4-max': "Refreshed on {d}: AA now publishes MLCR on this row ({m}), which was previously fitted; the score was {old} from three measured rungs (v1.4.46).",
          'gemini-4-neon': "Refreshed on {d}: AA revised this row's MLCR from 0.283333 to {m}; the score was {old} (v1.4.48)."}
old = json.loads((G / 'capability-ladder.json').read_text())['models']
entries, results = {}, {}
for site, aa, rel, rdate, eff, name in TARGETS:
    A = rows_by_site[site]
    raw = {k: A[f] for k, f in FIELDS.items() if A.get(f) is not None}
    rp = (A.get('briefcaseBreakdown') or {}).get('rubricPassRate')
    if rp is not None: raw['briefcase_rubric'] = rp
    n = len(raw); assert n >= 3, (site, raw)
    t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
    for r in rows: r['source_date'] = DATE if r['how'] == 'measured' else None
    change = CHANGE[site].format(d=DATE, m=round(raw['mlcr'], 6) if 'mlcr' in raw else 'absent', old=old[site]['ladder'])
    note = (f"Provisional. Measured from the exact {aa} row in Artificial Analysis's page data (initialModels) on {DATE} "
            f"(slug, release and effort checked). {WHY[site]} {change} This is newly published upstream data, not a correction of an omission. "
            f"Briefcase is not used: AA now publishes it as an Elo, not the rubric pass rate this rung measures. "
            f"{METHOD} Only {n} of 22 rungs are measured ({', '.join(sorted(raw))}); the rest are fitted. "
            f"Few-rung fits read high: for the {B['n']} models scoring 150 or more whose own rows include AutomationBench, Omniscience accuracy, "
            f"GDP.pdf and MLCR, a fit on those four alone comes out a median {B['median']:+.1f} points against the same model's fit on all its "
            f"measured rungs (range {B['min']:+.1f} to {B['max']:+.1f}; provisional-20261123-mlcr-refresh/four_rung_bias.json). "
            f"Treat the rank as uncertain by several places. The next full pipeline run replaces it.")
    entry = {"ladder": L, "ladder_max": 220, "match_confidence": "exact", "matched_model": name, "measured_rungs": n,
             "n_rungs": 22, "point_variant": eff, "provisional_note": note, "rungs": rows, "source": SRC, "status": "scored"}
    entries[site] = entry
    results[site] = dict(published_method='provisional-20261004 (recovered)', aa_slug=aa, effort=eff, raw=raw, n=n, theta=t, ladder=L,
                         previous_ladder=old[site]['ladder'], intelligence_index=A.get('intelligenceIndex'), same_release_rows=siblings[site])
    save(f'{site}_entry.json', entry)
    print(site, aa, eff, old[site]['ladder'], '->', L, 'theta', round(t, 3), 'measured', n, raw)
save('result.json', results)
if '--write' not in sys.argv: sys.exit(0)

p = G / 'capability-ladder.json'; text = p.read_text()
for site, entry in entries.items():
    key = f'\n    "{site}": '; assert text.count(key) == 1, site
    start = text.index(key) + len(key)
    prev, end = json.JSONDecoder().raw_decode(text, start)
    assert prev['status'] == 'scored', (site, prev['status'])
    new = json.dumps(entry, indent=2, ensure_ascii=True, sort_keys=True).replace('\n', '\n    ')
    text = text[:start] + new + text[end:]
json.loads(text); p.write_text(text)
txt = (G / 'models.json').read_text(); M = json.loads(txt)
for site, entry in entries.items():
    hit = [x for x in M if x['model'] == site]; assert len(hit) == 1, site
    hit[0]['capability'] = json.loads(json.dumps(entry, sort_keys=True))
(G / 'models.json').write_text(json.dumps(M, indent=2, ensure_ascii=False) + ('\n' if txt.endswith('\n') else ''))
print('wrote', {s: e['ladder'] for s, e in entries.items()})
