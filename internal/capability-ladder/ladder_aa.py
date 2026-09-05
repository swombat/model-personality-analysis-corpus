#!/usr/bin/env python3
"""Capability ladder on Artificial Analysis' own per-benchmark cells, our fit.

Substrate: raw/aa/aa_history_best.tsv — for every AA model slug, the best-
provenance value per canonical benchmark across the live payload (2026-09-05)
and 14 Wayback snapshots (2024-01 → 2026-07). Retired rungs (MMLU, MMLU-Pro,
MATH-500, HumanEval, AIME-24, LiveCodeBench, GPQA) are therefore present for the
models that were live when they were.

Model: two-parameter logistic per benchmark, one ability per model —
    E[score_ij] = σ(a_j (θ_i − b_j)),   score chance-corrected (s − c)/(1 − c)
fitted by alternating grid search (items | abilities), then the ability scale
is anchored to Claude 3.5 Sonnet = 130 and GPT-5 = 150 so numbers are directly
comparable with Epoch's ECI. Ladder = Σ_rungs 10 × (measured if present else
fitted); every term tagged.

Usage:
  python3 ladder_aa.py                 # writes aa_ladder.tsv + aa_items.tsv
  python3 ladder_aa.py --show gpt-4 claude-3-haiku gpt-6-astra
  python3 ladder_aa.py --bootstrap 50  # CI on θ by resampling a model's cells
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "raw/aa/aa_history_best.tsv"
POINTS = 10.0
MIN_MEASURED = 3  # a ladder score needs ≥3 measured rungs; one cell = one equation, one unknown

# canonical id -> (label, chance baseline). Elo-scaled (briefcase, gdpval_aa,
# arena_elo) and composite fields are not rungs.
RUNGS = {
    "mmlu": ("MMLU", 0.25),
    "humaneval": ("HumanEval", 0.0),
    "math_500": ("MATH-500", 0.0),
    "mmlu_pro": ("MMLU-Pro", 0.10),
    "gpqa_diamond": ("GPQA Diamond", 0.25),
    "aime24": ("AIME 2024", 0.0),
    "aime25": ("AIME 2025", 0.0),
    "livecodebench": ("LiveCodeBench", 0.0),
    "scicode": ("SciCode", 0.0),
    "ifbench": ("IFBench", 0.0),
    "aa_lcr": ("AA-LCR", 0.0),
    "tau2_telecom": ("τ²-Telecom", 0.0),
    "tau3_banking": ("τ³-Banking", 0.0),
    "terminalbench_hard": ("Terminal-Bench Hard", 0.0),
    "terminalbench_v21": ("Terminal-Bench 2.1", 0.0),
    "omniscience_accuracy": ("Omniscience acc.", 0.0),
    "hle": ("HLE", 0.048),
    "critpt": ("CritPt", 0.0),
    "gdp_pdf": ("GDP.pdf", 0.0),
}
ANCHORS = {"claude-35-sonnet": 130.0, "gpt-5": 150.0}


def sig(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, x))))


def load_cells() -> tuple[dict, dict]:
    rows = list(csv.DictReader(open(SRC), delimiter="\t"))
    meta, cells = {}, {}
    for r in rows:
        slug = r["aa_model_slug"]
        meta[slug] = {"name": r.get("name", ""), "creator": r.get("creator", ""), "release": r.get("releaseDate", "")}
        for k, (_, base) in RUNGS.items():
            v = r.get(k, "")
            if v in ("", None):
                continue
            x = float(v)
            if x > 1.5:
                x /= 100.0
            cells[(slug, k)] = max(0.0, min(1.0, (x - base) / (1.0 - base)))
    return meta, cells


def fit(cells: dict, rounds: int = 5) -> tuple[dict, dict]:
    models = sorted({m for m, _ in cells})
    items = sorted({b for _, b in cells})
    by_m = {m: [] for m in models}
    by_b = {b: [] for b in items}
    for (m, b), s in cells.items():
        by_m[m].append((b, s)); by_b[b].append((m, s))
    # init θ from mean chance-corrected score, spread 90..170
    theta = {m: 90 + 80 * (sum(s for _, s in by_m[m]) / len(by_m[m])) for m in models}
    par = {b: (0.1, 130.0) for b in items}
    a_grid = [x / 100 for x in range(2, 61, 4)]
    b_grid = [float(x) for x in range(60, 201, 2)]
    t_grid = [x / 2 for x in range(120, 401)]
    for _ in range(rounds):
        for b in items:  # items given θ
            best = None
            for a in a_grid:
                for d in b_grid:
                    e = sum((sig(a * (theta[m] - d)) - s) ** 2 for m, s in by_b[b])
                    if best is None or e < best[0]:
                        best = (e, a, d)
            par[b] = (best[1], best[2])
        for m in models:  # θ given items
            best = None
            for t in t_grid:
                e = sum((sig(par[b][0] * (t - par[b][1])) - s) ** 2 for b, s in by_m[m])
                if best is None or e < best[0]:
                    best = (e, t)
            theta[m] = best[1]
    return theta, par


def anchor(theta: dict, par: dict) -> tuple[dict, dict]:
    (m1, v1), (m2, v2) = ANCHORS.items()
    if m1 not in theta or m2 not in theta:
        sys.exit(f"anchor models missing: {[m for m in (m1, m2) if m not in theta]}")
    t1, t2 = theta[m1], theta[m2]
    k = (v2 - v1) / (t2 - t1); c = v1 - k * t1
    theta = {m: k * t + c for m, t in theta.items()}
    par = {b: (a / k, k * d + c) for b, (a, d) in par.items()}
    return theta, par


def ladder(m: str, theta: dict, par: dict, cells: dict, rungs: list[str]) -> dict:
    rows = []
    for b in rungs:
        if (m, b) in cells:
            rows.append((b, cells[(m, b)], "measured"))
        else:
            a, d = par[b]; rows.append((b, sig(a * (theta[m] - d)), "fitted"))
    return {"total": sum(POINTS * s for _, s, _ in rows), "rows": rows,
            "measured": sum(1 for _, _, h in rows if h == "measured")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", nargs="*", default=[])
    ap.add_argument("--bootstrap", type=int, default=0)
    a = ap.parse_args()
    meta, cells = load_cells()
    theta, par = fit(cells)
    theta, par = anchor(theta, par)
    rungs = sorted(par, key=lambda b: par[b][1])
    with open(HERE / "aa_items.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t"); w.writerow(["benchmark", "label", "difficulty", "slope", "n_models", "chance"])
        for b in rungs:
            w.writerow([b, RUNGS[b][0], f"{par[b][1]:.1f}", f"{par[b][0]:.3f}", sum(1 for (m, bb) in cells if bb == b), RUNGS[b][1]])
    n_cells = {m: 0 for m in theta}
    for (m, _) in cells:
        n_cells[m] += 1
    results = []
    for m in theta:
        L = ladder(m, theta, par, cells, rungs)
        lo = hi = ""
        if a.bootstrap and n_cells[m] >= 3:
            obs = [(b, cells[(m, b)]) for b in rungs if (m, b) in cells]
            ts = []
            for _ in range(a.bootstrap):
                smp = [random.choice(obs) for _ in obs]
                best = None
                for t in [x / 2 for x in range(120, 401)]:
                    e = sum((sig(par[b][0] * (t - par[b][1])) - s) ** 2 for b, s in smp)
                    if best is None or e < best[0]:
                        best = (e, t)
                ts.append(best[1])
            ts.sort(); lo, hi = f"{ts[int(0.05 * len(ts))]:.1f}", f"{ts[int(0.95 * len(ts)) - 1]:.1f}"
        results.append((m, meta[m], theta[m], L, n_cells[m], lo, hi))
    results.sort(key=lambda r: (r[3]["measured"] < MIN_MEASURED, -r[3]["total"]))
    with open(HERE / "aa_ladder.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["aa_slug", "name", "creator", "release", "theta", "theta_lo", "theta_hi", "ladder", "ladder_max", "measured_rungs", "n_rungs", "n_cells", "status"]
                   + [f"rung:{b}" for b in rungs] + [f"how:{b}" for b in rungs])
        for m, md, t, L, n, lo, hi in results:
            ok = L["measured"] >= MIN_MEASURED
            w.writerow([m, md["name"], md["creator"], md["release"], f"{t:.1f}" if ok else "", lo if ok else "", hi if ok else "",
                        f"{L['total']:.1f}" if ok else "", f"{POINTS * len(rungs):.0f}", L["measured"], len(rungs), n,
                        "ok" if ok else f"insufficient_measurements ({L['measured']}/{len(rungs)})"]
                       + [f"{s:.3f}" if (ok or h == "measured") else "" for _, s, h in L["rows"]] + [h for _, _, h in L["rows"]])
    print(f"fit: {len(theta)} models × {len(rungs)} rungs on {len(cells)} cells; ladder max {POINTS * len(rungs):.0f}")
    print("rungs by fitted difficulty:")
    for b in rungs:
        print(f"   {par[b][1]:6.1f}  slope {par[b][0]:.3f}  n={sum(1 for (m, bb) in cells if bb == b):3d}  {RUNGS[b][0]}")
    for m in a.show:
        if m not in theta:
            print(f"-- {m}: not in AA table"); continue
        L = ladder(m, theta, par, cells, rungs)
        print(f"\n-- {m} ({meta[m]['name']})  θ {theta[m]:.1f}  ladder {L['total']:.1f}/{POINTS * len(rungs):.0f}  {L['measured']}/{len(rungs)} measured")
        for b, s, h in L["rows"]:
            print(f"   {POINTS * s:5.1f}  {h:8s} {RUNGS[b][0]}")


if __name__ == "__main__":
    main()
