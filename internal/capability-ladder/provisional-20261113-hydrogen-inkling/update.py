"""Fetch ONLY AA currentModel; reproduce the recovered October 4 fit.

Run from any directory. Network receipts and extracted currentModel objects are
saved beside this file. Other page objects are never benchmark inputs.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATE = "2026-11-13"
FIELDS = {
    "aa_lcr": "lcr", "scicode": "scicode",
    "automationbench": "automationBenchPartialScore", "hle": "hle",
    "omniscience_accuracy": "omniscienceAccuracy", "critpt": "critpt",
    "gdp_pdf": "gdpPdfAllPass", "mlcr": "mlcrOverall",
    "tau3_banking": "tauBanking", "terminalbench_hard": "terminalbenchHard",
    "terminalbench_v21": "terminalBench21", "ifbench": "ifbench",
    "gpqa_diamond": "gpqa", "aime25": "aime25",
    "livecodebench": "livecodebench",
}

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

receipts = {}
models = {}
for slug in ("gemini-4-hydrogen", "gemini-4-hydrogen-high", "inkling-2-small"):
    url = "https://artificialanalysis.ai/models/" + slug
    with urllib.request.urlopen(url, timeout=45) as response:
        body = response.read()
        status = response.status
        final_url = response.url
    html = body.decode()
    chunks = re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', html)
    flight = "".join(json.loads(chunk) for chunk in chunks)
    markers = list(re.finditer(r'"currentModel"\s*:', flight))
    receipt = dict(url=url, final_url=final_url, http_status=status,
                   fetched_date=DATE, html_bytes=len(body),
                   html_sha256=hashlib.sha256(body).hexdigest(),
                   title=re.search(r"<title>(.*?)</title>", html).group(1),
                   decoded_flight_bytes=len(flight.encode()),
                   currentModel_count=len(markers))
    if markers:
        assert len(markers) == 1, receipt
        model, _ = json.JSONDecoder().raw_decode(flight[markers[0].end():])
        assert model["slug"] == slug, model["slug"]
        models[slug] = model
        save(f"aa_{slug}_currentModel_{DATE}.json", model)
    receipts[slug] = receipt
save("fetch_receipts.json", receipts)

# Recover fixed rung parameters from the same historical substrate as precedent.
historical = subprocess.run(
    ["git", "-C", str(ROOT), "show",
     "c85984e1^:website/src/generated/capability-ladder.json"],
    capture_output=True, text=True, check=True).stdout
P4 = ROOT / "internal/capability-ladder/provisional-20261004"
cwd = os.getcwd()
with tempfile.TemporaryDirectory() as tmp:
    ladder = Path(tmp) / "capability-ladder.json"
    ladder.write_text(historical)
    os.chdir(tmp)
    def source(name):
        return (P4 / name).read_text().replace(
            "/home/agent/work/mpac/website/src/generated/capability-ladder.json",
            str(ladder))
    exec(source("slopes.py"), {})
    g = {}
    exec(source("score.py").split("# validate")[0], g)
    os.chdir(cwd)
snapshot = json.loads((P4 / "aa_rows_2026-10-04.json").read_text())
for key, expected in {"gpt-6-1-sol-high": 161.6, "mimo-v2-5-pro": 128.1}.items():
    actual = g["score"]({k: g["cc"](k, v)
                         for k, v in snapshot[key].items()
                         if not k.startswith("_")})[1]
    assert abs(actual - expected) < .05, (key, actual)

SRC = ("Artificial Analysis per-benchmark results (public model pages), "
       "provisionally fitted against the 2026-09-29 ladder's rung parameters "
       "(full refit pending); permission requested 2026-09-05")
entries = {}
for site_slug, aa_slug, name, variant in [
    ("gemini-4-hydrogen", "gemini-4-hydrogen-high", "Gemini 4 Hydrogen", "high"),
    ("inkling-2-small", "inkling-2-small", "Inkling 2 Small", None),
]:
    model = models.get(aa_slug)
    raw = {} if model is None else {
        key: model[field] for key, field in FIELDS.items()
        if model.get(field) is not None}
    rubric = None if model is None else (
        model.get("briefcaseBreakdown") or {}).get("rubricPassRate")
    if rubric is not None:
        raw["briefcase_rubric"] = rubric
    n = len(raw)
    result = dict(published_method="provisional-20261004 (recovered)",
                  aa_variant=aa_slug, raw=raw, measured_rungs=n,
                  point_variant=variant)
    entry = dict(ladder=None, ladder_max=220, match_confidence="exact",
                 matched_model=name, measured_rungs=n, n_rungs=22,
                 point_variant=variant, source=SRC, status="not_scored")
    if n >= 3:
        theta, score, rows = g["score"]({k: g["cc"](k, v) for k, v in raw.items()})
        for row in rows:
            row["source_date"] = DATE if row["how"] == "measured" else None
        result.update(theta=theta, ladder=score, rows=rows,
                      intelligence_index=model.get("intelligenceIndex"))
        entry.update(ladder=score, rungs=rows, status="scored")
        note = (
            f"Provisional. Measured only from Artificial Analysis's currentModel "
            f"object on {DATE}, inkling-2-small. AA assigns no effort label "
            f"(effort is null), so no cross-effort row is borrowed; exact alignment "
            f"with the provider-default personality capture is not established. "
            f"Fitted with the recovered 2026-10-04 provisional method (fixed "
            f"2026-09-29 rung difficulties and recovered slopes, not a full refit), "
            f"which reproduces the published ladder to within 0.9 points on "
            f"average across 148 scored models and tends to read 0.6 points low. "
            f"{n} of 22 rungs measured; the rest fitted. New AA benchmark fields "
            f"outside the existing 22-rung definition are not substituted. "
            f"The next full pipeline run replaces it.")
    else:
        note = (
            f"Unscored as of {DATE}: AA's Gemini 4 Hydrogen and High pages "
            f"exist, but neither exposes a currentModel object in the decoded "
            f"Next Flight payload. No benchmark values were taken from "
            f"initialModels, currentRelease or comparison rows. High is the "
            f"provider-default effort per the task's Google-docs verification; "
            f"the xhigh page default is not substituted. Zero admissible measured "
            f"rungs; at least three are required. Recheck currentModel availability.")
    entry["provisional_note"] = note
    result["note"] = note
    entries[site_slug] = entry
    save(f"{site_slug}_result.json", result)
    save(f"{site_slug}_entry.json", entry)
    print(site_slug, entry["status"], entry["ladder"], n, raw)

path = ROOT / "website/src/generated/capability-ladder.json"
original = subprocess.check_output(
    ["git", "-C", str(ROOT), "show", "HEAD:website/src/generated/capability-ladder.json"])
text = original.decode()
old_models = json.loads(text)["models"]
for slug, entry in sorted(entries.items()):
    assert slug not in old_models
    successor = min(k for k in old_models if k > slug)
    anchor = f'    "{successor}":'
    assert text.count(anchor) == 1
    value = json.dumps(entry, indent=2, ensure_ascii=False, sort_keys=True)
    block = f'    "{slug}": ' + value.replace("\n", "\n    ") + ",\n"
    text = text.replace(anchor, block + anchor)
path.write_bytes(text.encode())
aliases = ROOT / "internal/capability-ladder/aliases.tsv"
existing = subprocess.check_output(
    ["git", "-C", str(ROOT), "show", "HEAD:internal/capability-ladder/aliases.tsv"])
new = [
    "gemini-4-hydrogen\tgemini-4-hydrogen\t2026-11-12\tGemini 4 Hydrogen\texact\tgemini-4-hydrogen-high\texact\tUnscored 2026-11-13: High matches provider default, but both AA default and High pages lack currentModel; comparison data excluded. See provisional-20261113-hydrogen-inkling/.",
    "inkling-2-small\tinkling-2-small\t2026-11-05\tInkling 2 Small\texact\tinkling-2-small\texact\t2026-11-13: AA currentModel only; effort null, provider-default effort equivalence unverified. Provisional fixed-rung fit; see provisional-20261113-hydrogen-inkling/.",
]
for row in new:
    slug = row.split("\t")[0]
    assert not any(line.startswith((slug + "\t").encode()) for line in existing.splitlines())
aliases.write_bytes(existing + (b"" if existing.endswith(b"\n") else b"\n")
                    + ("\n".join(new) + "\n").encode())
