"""Mira's 2026-11-23 review (YRyzbr), low: the site called every effort row "the median of its published effort settings",
but five provisional entries were chosen by a different, explicit rule (the provider-default effort the capture used,
or AA's only row). Adds an `effort_basis` string to those entries; the pages show it in place of the median wording.
Scores and selected rows are unchanged. Run from the repo root."""
import json, pathlib
G = pathlib.Path('website/src/generated')
BASIS = {
    'gpt-6-2-astra': "Medium effort, OpenAI's default and the effort the capture used (AA's median row is High)",
    'gpt-6-2-sol': "Medium effort, OpenAI's default and the effort the capture used (AA's median row is High)",
    'gemini-4-hydrogen': "High effort, Google's default and the effort the capture used",
    'gemini-4-neon': "High thinking level, Google's default and the level the capture used",
    'qwen4-max': "xhigh, the only effort AA lists (the capture ran at Alibaba's default)",
}
p = G / 'capability-ladder.json'; text = p.read_text()
for site, basis in BASIS.items():
    key = f'\n    "{site}": '; assert text.count(key) == 1, site
    start = text.index(key) + len(key)
    prev, end = json.JSONDecoder().raw_decode(text, start)
    assert 'effort_basis' not in prev and text[start:start + 2] == '{\n', site
    text = text[:start + 2] + '      "effort_basis": ' + json.dumps(basis) + ',\n' + text[start + 2:]
L = json.loads(text)['models']; p.write_text(text)
txt = (G / 'models.json').read_text(); M = json.loads(txt)
for site in BASIS:
    hit = [x for x in M if x['model'] == site]; assert len(hit) == 1, site
    hit[0]['capability'] = json.loads(json.dumps(L[site], sort_keys=True))
(G / 'models.json').write_text(json.dumps(M, indent=2, ensure_ascii=False) + ('\n' if txt.endswith('\n') else ''))
print({s: L[s]['effort_basis'] for s in BASIS})
