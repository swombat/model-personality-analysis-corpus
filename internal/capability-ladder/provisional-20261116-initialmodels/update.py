"""Hydrogen High and Qwen4 Max from AA's initialModels rows (2026-11-16), recovered 2026-10-04 method.

Mira's 2026-11-16 review (JzmqpB): AA pages no longer carry `currentModel`; the exact own-model row now sits in
the decoded Next Flight `initialModels` array. This script admits a row from that array only when its `slug` is
exactly the requested AA slug, `release.slug` is the model's own release, `releaseDate` matches, and the effort
slug is the one named below; exactly one such row must exist. The row is saved verbatim beside this file.
Nothing is taken from comparison rows, `currentRelease`, or the Briefcase Elo object (`briefcaseBreakdown.overall`
is an Elo, not the historical `rubricPassRate`; only `rubricPassRate` is a ladder input, as before).
Checks Sol High 161.6 / MiMo 128.1 before scoring. Replaces the two existing not_scored entries in
capability-ladder.json (text splice, no reformatting), their models.json capability objects, and aliases rows.
Run from the repo root: python3 <this> [--write]   (without --write it fetches, saves and prints only).
"""
import hashlib, json, os, pathlib, re, subprocess, sys, tempfile, urllib.request
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]; P4 = ROOT / 'internal/capability-ladder/provisional-20261004'
G = ROOT / 'website/src/generated'; DATE = '2026-11-16'
def save(name, value): (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

# (site slug, AA page slug, AA release slug, release date, effort, display name)
TARGETS = [('gemini-4-hydrogen', 'gemini-4-hydrogen-high', 'gemini-4-hydrogen', '2026-11-12', 'high', 'Gemini 4 Hydrogen'),
           ('qwen4-max', 'qwen4-max', 'qwen4-max', '2026-11-16', 'xhigh', 'Qwen4 Max')]
receipts, rows_by_site, siblings = {}, {}, {}
for site, aa, rel, rdate, eff, name in TARGETS:
    url = 'https://artificialanalysis.ai/models/' + aa
    with urllib.request.urlopen(url, timeout=45) as r: body = r.read(); status = r.status; final = r.url
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
exec(src('slopes.py'), {}); g = {}; exec(src('score.py').split('# validate')[0], g); os.chdir(cwd)
snap = json.loads((P4 / 'aa_rows_2026-10-04.json').read_text())
for k, want in {'gpt-6-1-sol-high': 161.6, 'mimo-v2-5-pro': 128.1}.items():
    L = g['score']({r: g['cc'](r, v) for r, v in snap[k].items() if not r.startswith('_')})[1]
    assert abs(L - want) < 0.05, (k, L)
FIELDS = {'aa_lcr': 'lcr', 'scicode': 'scicode', 'automationbench': 'automationBenchPartialScore', 'hle': 'hle',
          'omniscience_accuracy': 'omniscienceAccuracy', 'critpt': 'critpt', 'gdp_pdf': 'gdpPdfAllPass', 'mlcr': 'mlcrOverall',
          'tau3_banking': 'tauBanking', 'terminalbench_hard': 'terminalbenchHard', 'terminalbench_v21': 'terminalBench21',
          'ifbench': 'ifbench', 'gpqa_diamond': 'gpqa', 'aime25': 'aime25', 'livecodebench': 'livecodebench'}
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 "
       "ladder's rung parameters (full refit pending); permission requested 2026-09-05")
METHOD = ("Fitted with the 2026-10-04 provisional method (rung difficulties and slopes of the 2026-09-29 ladder, without the "
          "full refit), which reproduces the published ladder to within 0.9 points on average across 148 scored models and "
          "tends to read 0.6 points low.")
entries, results = {}, {}
for site, aa, rel, rdate, eff, name in TARGETS:
    A = rows_by_site[site]
    raw = {k: A[f] for k, f in FIELDS.items() if A.get(f) is not None}
    rp = (A.get('briefcaseBreakdown') or {}).get('rubricPassRate')
    if rp is not None: raw['briefcase_rubric'] = rp
    n = len(raw); assert n >= 3, (site, raw)
    t, L, rows = g['score']({k: g['cc'](k, v) for k, v in raw.items()})
    for r in rows: r['source_date'] = DATE if r['how'] == 'measured' else None
    if site == 'gemini-4-hydrogen':
        why = (f"High effort row ({aa}), Google's provider-default effort, which the capture used; AA also lists xhigh "
               f"(its default page), medium and low, and xhigh is not substituted.")
    else:
        why = (f"AA lists Qwen4 Max at one effort only, xhigh, so that row is used. The personality capture ran at Alibaba's "
               f"provider default, which is not established to be xhigh, so the score may not match the captured cell.")
    note = (f"Provisional. Measured from the exact {aa} row in Artificial Analysis's page data (initialModels) on {DATE}: "
            f"AA's pages no longer expose the currentModel object that earlier scores were read from, and the same model's "
            f"row now sits in initialModels (slug, release and effort checked). {why} Until v1.4.46 this model was shown "
            f"unscored; the change is an extraction fix (Mira's 16 Nov review), not newly published benchmarks. "
            f"Briefcase is not used: AA now publishes it as an Elo, not the rubric pass rate this rung measures. "
            f"{METHOD} Only {n} of 22 rungs are measured (AutomationBench, Omniscience accuracy and GDP.pdf, the minimum); the rest are fitted. "
            f"This reads high: for the 19 models scoring 150 or more whose own rows include those three rungs, a fit on those three "
            f"alone comes out a median 4.9 points above the same model's fit on all its measured rungs (range -3.2 to +12.5; "
            f"three_rung_bias.py). Treat the rank as uncertain by several places. The next full pipeline run replaces it.")
    entry = {"ladder": L, "ladder_max": 220, "match_confidence": "exact", "matched_model": name, "measured_rungs": n,
             "n_rungs": 22, "point_variant": eff, "provisional_note": note, "rungs": rows, "source": SRC, "status": "scored"}
    entries[site] = entry
    results[site] = dict(published_method='provisional-20261004 (recovered)', aa_slug=aa, effort=eff, raw=raw, n=n,
                         theta=t, ladder=L, intelligence_index=A.get('intelligenceIndex'), same_release_rows=siblings[site])
    save(f'{site}_entry.json', entry)
    print(site, aa, eff, L, 'theta', round(t, 3), 'measured', n, raw)
save('result.json', results)
if '--write' not in sys.argv: sys.exit(0)

p = G / 'capability-ladder.json'; text = p.read_text()
for site, entry in entries.items():
    key = f'\n    "{site}": '; assert text.count(key) == 1, site
    start = text.index(key) + len(key)
    old, end = json.JSONDecoder().raw_decode(text, start)
    assert old['status'] == 'not_scored', (site, old['status'])
    new = json.dumps(entry, indent=2, ensure_ascii=True, sort_keys=True).replace('\n', '\n    ')
    text = text[:start] + new + text[start + end - start:]
json.loads(text); p.write_text(text)
txt = (G / 'models.json').read_text(); M = json.loads(txt)
for site, entry in entries.items():
    hit = [x for x in M if x['model'] == site]; assert len(hit) == 1, site
    hit[0]['capability'] = json.loads(json.dumps(entry, sort_keys=True))
(G / 'models.json').write_text(json.dumps(M, indent=2, ensure_ascii=False) + ('\n' if txt.endswith('\n') else ''))
al = ROOT / 'internal/capability-ladder/aliases.tsv'; lines = al.read_bytes().split(b'\n')  # bytes: older rows end in CRLF
NEW = {'gemini-4-hydrogen': "gemini-4-hydrogen\tgemini-4-hydrogen\t2026-11-12\tGemini 4 Hydrogen\texact\tgemini-4-hydrogen-high\texact\t2026-11-16: exact AA initialModels row gemini-4-hydrogen-high (High = provider default; xhigh not substituted); currentModel absent. Provisional fixed-rung fit; see provisional-20261116-initialmodels/.",
       'qwen4-max': "qwen4-max\tqwen4-max\t2026-11-16\tQwen4 Max\texact\tqwen4-max\texact\t2026-11-16: exact AA initialModels row qwen4-max, effort xhigh (AA's only row); capture ran at provider default, equivalence unverified. Provisional fixed-rung fit; see provisional-20261116-initialmodels/."}
for site, row in NEW.items():
    idx = [i for i, l in enumerate(lines) if l.startswith((site + '\t').encode())]; assert len(idx) == 1, site
    lines[idx[0]] = row.encode()
al.write_bytes(b'\n'.join(lines))
print('wrote', {s: e['ladder'] for s, e in entries.items()})
