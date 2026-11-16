"""Qwen4 Max ladder check (2026-11-16). Fetch ONLY AA currentModel, as
provisional-20261113-hydrogen-inkling/update.py. If currentModel is absent the
model is recorded unscored; currentRelease/initialModels/comparison rows are
never benchmark inputs. Run from this worktree over a clean HEAD for the two
tracked files it edits (capability-ladder.json, aliases.tsv)."""
import hashlib, json, re, subprocess, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]; DATE = "2026-11-16"
SLUG = "qwen4-max"
def save(name, value): (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
url = "https://artificialanalysis.ai/models/" + SLUG
with urllib.request.urlopen(url, timeout=45) as r: body = r.read(); status = r.status; final = r.url
html = body.decode()
flight = "".join(json.loads(c) for c in re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', html))
markers = list(re.finditer(r'"currentModel"\s*:', flight))
receipt = dict(url=url, final_url=final, http_status=status, fetched_date=DATE, html_bytes=len(body),
               html_sha256=hashlib.sha256(body).hexdigest(), title=re.search(r"<title>(.*?)</title>", html).group(1),
               decoded_flight_bytes=len(flight.encode()), currentModel_count=len(markers))
save("fetch_receipts.json", {SLUG: receipt})
assert not markers, "currentModel present: score it with the hydrogen-inkling fit instead"
SRC = ("Artificial Analysis per-benchmark results (public model pages), provisionally fitted against the 2026-09-29 "
       "ladder's rung parameters (full refit pending); permission requested 2026-09-05")
NOTE = (f"Unscored as of {DATE}: AA's Qwen4 Max page exists (HTTP 200, correct title, release date 2026-11-16) but "
        f"exposes no currentModel object in the decoded Next Flight payload. No benchmark values were taken from "
        f"currentRelease (which carries only an Intelligence Index), initialModels or comparison rows. Zero admissible "
        f"measured rungs; at least three are required. Recheck currentModel availability.")
entry = dict(ladder=None, ladder_max=220, match_confidence="exact", matched_model="Qwen4 Max", measured_rungs=0,
             n_rungs=22, point_variant=None, provisional_note=NOTE, source=SRC, status="not_scored")
save(f"{SLUG}_entry.json", entry)
path = ROOT / "website/src/generated/capability-ladder.json"
text = subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:website/src/generated/capability-ladder.json"]).decode()
old = json.loads(text)["models"]; assert SLUG not in old
anchor = f'    "{min(k for k in old if k > SLUG)}":'; assert text.count(anchor) == 1
block = f'    "{SLUG}": ' + json.dumps(entry, indent=2, ensure_ascii=False, sort_keys=True).replace("\n", "\n    ") + ",\n"
path.write_bytes(text.replace(anchor, block + anchor).encode())
aliases = ROOT / "internal/capability-ladder/aliases.tsv"
existing = subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:internal/capability-ladder/aliases.tsv"])
row = (f"{SLUG}\t{SLUG}\t2026-11-16\tQwen4 Max\texact\t{SLUG}\texact\tUnscored 2026-11-16: AA page lacks currentModel; "
       f"currentRelease Intelligence Index not used. See provisional-20261116-qwen4-max/.")
assert not any(l.startswith((SLUG + "\t").encode()) for l in existing.splitlines())
aliases.write_bytes(existing + (b"" if existing.endswith(b"\n") else b"\n") + (row + "\n").encode())
print("qwen4-max not_scored; receipts saved")
