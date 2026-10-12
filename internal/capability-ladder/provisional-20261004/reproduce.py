"""Reproduce the v1.4.22 provisional scores (GPT-6.1 Sol 161.6, MiMo-V2.5-Pro 128.1) from the
recovered 2026-10-04 scripts and row snapshot, against the ladder JSON as it stood before v1.4.22
(git c85984e1^). Run from the repo root: python3 internal/capability-ladder/provisional-20261004/reproduce.py"""
import json, subprocess, tempfile, os, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
pre = subprocess.run(["git", "-C", str(ROOT), "show", "c85984e1^:website/src/generated/capability-ladder.json"],
                     capture_output=True, text=True, check=True).stdout
tmp = tempfile.mkdtemp()
lad = os.path.join(tmp, "capability-ladder.json"); open(lad, "w").write(pre)
os.chdir(tmp)
src = lambda f: (HERE / f).read_text().replace("/home/agent/work/mpac/website/src/generated/capability-ladder.json", lad)
exec(src("slopes.py"), {})                      # writes items.json (prints n 905 rms ~0.004)
g = {}
exec(src("score.py").split("# validate")[0], g)  # defines score() and cc()
snap = json.loads((HERE / "aa_rows_2026-10-04.json").read_text())
expect = {"gpt-6-1-sol-high": 161.6, "mimo-v2-5-pro": 128.1}
ok = True
for k, want in expect.items():
    meas = {r: g["cc"](r, v) for r, v in snap[k].items() if not r.startswith("_")}
    t, L, _ = g["score"](meas)
    print(k, "ladder", L, "published", want, "measured rungs", len(meas))
    ok &= abs(L - want) < 0.05
print("REPRODUCED" if ok else "MISMATCH")
