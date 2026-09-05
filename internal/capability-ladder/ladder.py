#!/usr/bin/env python3
"""Capability ladder — cumulative, open-ended benchmark score per model.

Design: internal/capability-ladder/DESIGN.md. In one line: every rung is a
benchmark worth 10 points × the model's chance-corrected score; measured
cells are used as measured, missing cells are derived from Epoch AI's
Capabilities Index item-response fit (one ability per model, one difficulty
and slope per benchmark); the published number is the plain sum, with the
measured/fitted split reported beside it.

Data (all published, CC-BY 4.0 — "Epoch AI, AI Benchmarking Hub, epoch.ai"):
  raw/epoch/benchmark_data/epoch_capabilities_index/eci_scores.csv
  raw/epoch/benchmark_data/epoch_capabilities_index/edi_scores.csv
  raw/epoch/benchmark_data/epoch_capabilities_index/processed_data_for_eci.csv

Usage:
  python3 ladder.py                 # writes ladder.tsv (all Epoch models)
  python3 ladder.py --rungs all     # every ECI benchmark instead of the curated set
  python3 ladder.py --show "GPT-4o (May 2024)" ...   # print per-rung detail

Functional form verified 2026-09-05 against all 2,842 processed cells:
performance ≈ σ(slope · (eci − edi)), RMSE 0.073.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ECI_DIR = HERE / "raw/epoch/benchmark_data/epoch_capabilities_index"
POINTS_PER_RUNG = 10.0

# Curated rungs: one recognisable public benchmark per generation of yardstick,
# sorted by Epoch's fitted difficulty at run time. Chosen to be the benchmarks a reader
# has heard of; the full ECI set is available with --rungs all.
CURATED = [
    "MMLU",
    "GSM8K",
    "HellaSwag",
    "MATH level 5",
    "GPQA diamond",
    "SWE-Bench verified",
    "OTIS Mock AIME 2024-2025",
    "Aider polyglot",
    "Terminal Bench",
    "FrontierMath-Tiers-1-3-v2-Private",
    "HLE",
    "ARC-AGI-2",
    "CritPt",
    "GDPval",
    "Remote Labor Index",
]


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def load() -> tuple[dict, dict, dict]:
    eci = {r["Model"]: r for r in csv.DictReader(open(ECI_DIR / "eci_scores.csv"))}
    edi = {r["benchmark_name"]: r for r in csv.DictReader(open(ECI_DIR / "edi_scores.csv"))}
    cells: dict[tuple[str, str], float] = {}
    for c in csv.DictReader(open(ECI_DIR / "processed_data_for_eci.csv")):
        cells[(c["Model"], c["benchmark"])] = float(c["performance"])
    return eci, edi, cells


def fitted(theta: float, bench: dict) -> float:
    return sigmoid(float(bench["estimated_slope_scaled"]) * (theta - float(bench["edi"])))


def ladder_for(model: str, rungs: list[str], eci: dict, edi: dict, cells: dict, extra: dict | None = None) -> dict:
    """extra: {rung: chance-corrected score} measured by another harness (tagged 'measured-aa')."""
    theta = float(eci[model]["eci"])
    extra = extra or {}
    rows = []
    for b in rungs:
        if (model, b) in cells:
            s, how = max(0.0, min(1.0, cells[(model, b)])), "measured"
        elif b in extra:
            s, how = max(0.0, min(1.0, extra[b])), "measured-aa"
        else:
            s, how = fitted(theta, edi[b]), "fitted"
        rows.append((b, s, how))
    total = sum(POINTS_PER_RUNG * s for _, s, _ in rows)
    measured = sum(POINTS_PER_RUNG * s for _, s, how in rows if how.startswith("measured"))
    n_meas = sum(1 for _, _, how in rows if how.startswith("measured"))
    lo, hi = eci[model]["eci_ci_low"], eci[model]["eci_ci_high"]
    # CI on the ladder: recompute fitted terms at the θ interval ends, keep measured fixed.
    def total_at(th: float) -> float:
        return sum(POINTS_PER_RUNG * (cells[(model, b)] if (model, b) in cells else extra[b] if b in extra else fitted(th, edi[b])) for b in rungs)
    ci = (total_at(float(lo)), total_at(float(hi))) if lo and hi else (None, None)
    return {
        "model": model,
        "eci": theta,
        "eci_ci_low": lo,
        "eci_ci_high": hi,
        "release_date": eci[model]["date"],
        "organization": eci[model]["Organization"],
        "ladder": total,
        "ladder_ci_low": ci[0],
        "ladder_ci_high": ci[1],
        "ladder_max": POINTS_PER_RUNG * len(rungs),
        "measured_points": measured,
        "measured_rungs": n_meas,
        "n_rungs": len(rungs),
        "rows": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", default="curated", choices=["curated", "all"])
    ap.add_argument("--show", nargs="*", default=[])
    ap.add_argument("--out", default=str(HERE / "ladder.tsv"))
    a = ap.parse_args()
    eci, edi, cells = load()
    missing = [b for b in CURATED if b not in edi]
    if missing:
        sys.exit(f"rungs not in edi_scores.csv: {missing}")
    rungs = sorted(CURATED if a.rungs == "curated" else list(edi), key=lambda b: float(edi[b]["edi"]))

    results = [ladder_for(m, rungs, eci, edi, cells) for m in eci if eci[m]["eci"]]
    results.sort(key=lambda r: -r["ladder"])
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["model", "organization", "release_date", "ladder", "ladder_ci_low", "ladder_ci_high",
                    "ladder_max", "measured_points", "measured_rungs", "n_rungs", "eci", "eci_ci_low", "eci_ci_high"]
                   + [f"rung:{b}" for b in rungs] + [f"how:{b}" for b in rungs])
        for r in results:
            w.writerow([r["model"], r["organization"], r["release_date"], f"{r['ladder']:.1f}",
                        "" if r["ladder_ci_low"] is None else f"{r['ladder_ci_low']:.1f}",
                        "" if r["ladder_ci_high"] is None else f"{r['ladder_ci_high']:.1f}",
                        f"{r['ladder_max']:.0f}", f"{r['measured_points']:.1f}", r["measured_rungs"], r["n_rungs"],
                        f"{r['eci']:.2f}", r["eci_ci_low"], r["eci_ci_high"]]
                       + [f"{s:.3f}" for _, s, _ in r["rows"]] + [how for _, _, how in r["rows"]])
    print(f"wrote {a.out}: {len(results)} models, {len(rungs)} rungs, max {POINTS_PER_RUNG * len(rungs):.0f}")

    for m in a.show:
        r = next((x for x in results if x["model"] == m), None)
        if not r:
            print(f"-- {m}: not in ECI"); continue
        print(f"\n-- {m}  ladder {r['ladder']:.1f}/{r['ladder_max']:.0f}  "
              f"(CI {r['ladder_ci_low']:.1f}–{r['ladder_ci_high']:.1f}; {r['measured_rungs']}/{r['n_rungs']} rungs measured, "
              f"{r['measured_points']:.1f} pts)  ECI {r['eci']:.1f}")
        for b, s, how in r["rows"]:
            print(f"   {POINTS_PER_RUNG * s:5.1f}  {how:8s} {b}")


if __name__ == "__main__" and "--site" not in sys.argv:
    main()


# ---------------------------------------------------------------------------
# Hybrid: models Epoch has not scored yet, estimated from Artificial Analysis'
# live per-benchmark row (raw/aa/aa_scores.tsv). Each AA field is calibrated
# as an extra item on the models both sources cover, then θ for an AA-only
# model is the least-squares fit over its available AA cells. Tagged
# `provisional`; replaced by Epoch's number when Epoch scores the model.
# ---------------------------------------------------------------------------
AA_ITEMS = {  # aa field -> chance baseline (AA reports raw accuracy)
    "gpqa": 0.25, "hle": 0.048, "aime25": 0.0, "livecodebench": 0.0, "scicode": 0.0,
    "ifbench": 0.0, "lcr": 0.0, "tau2": 0.0, "tauBanking": 0.0, "terminalbenchHard": 0.0,
    "terminalbenchV21": 0.0, "critpt": 0.0, "omniscienceBreakdown.accuracy": 0.0,
}


# AA fields that ARE curated rungs (same test, different harness). Chance
# baselines are Epoch's for the same benchmark. Terminal-Bench (version drift),
# AIME (different problem set) and GDPval (different scale) are deliberately NOT
# mapped — they calibrate θ but don't count as measured rungs.
AA_RUNG = {"gpqa": ("GPQA diamond", 0.25), "hle": ("HLE", 0.048), "critpt": ("CritPt", 0.0)}


def aa_rung_cells(aa_row: dict) -> dict:
    out = {}
    for f, (rung, base) in AA_RUNG.items():
        v = cc(aa_row.get(f, ""), base)
        if v is not None:
            out[rung] = v
    return out


def load_aa() -> dict:
    p = HERE / "raw/aa/aa_scores.tsv"
    return {r["slug"]: r for r in csv.DictReader(open(p), delimiter="\t")}


def load_aliases() -> list[dict]:
    return list(csv.DictReader(open(HERE / "aliases.tsv"), delimiter="\t"))


def cc(v: str, base: float) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if x > 1.0:  # a few fields are 0-100
        x /= 100.0
    return max(0.0, (x - base) / (1.0 - base))


def calibrate_aa_items(eci: dict, aa: dict, aliases: list[dict]) -> dict:
    """Fit slope/difficulty per AA field on models with both an ECI θ and an AA row.
    Grid search on (a, b) minimising squared error of σ(a(θ-b)) vs chance-corrected score."""
    pairs = {f: [] for f in AA_ITEMS}
    for r in aliases:
        if r["epoch_model"] and r["aa_slug"] and r["epoch_model"] in eci and r["aa_slug"] in aa:
            th = float(eci[r["epoch_model"]]["eci"])
            for f, base in AA_ITEMS.items():
                s = cc(aa[r["aa_slug"]].get(f, ""), base)
                if s is not None:
                    pairs[f].append((th, s))
    params = {}
    for f, pts in pairs.items():
        if len(pts) < 15:
            continue
        best = None
        for a100 in range(2, 60):          # slope 0.02 .. 0.59 (Epoch's range is 0.015-0.30)
            a = a100 / 100.0
            for b in range(90, 200):       # difficulty 90 .. 199 on the ECI scale
                e = sum((sigmoid(a * (th - b)) - s) ** 2 for th, s in pts)
                if best is None or e < best[0]:
                    best = (e, a, float(b))
        e, a, b = best
        params[f] = {"slope": a, "edi": b, "n": len(pts), "rmse": math.sqrt(e / len(pts))}
    return params


def estimate_theta(aa_row: dict, params: dict) -> tuple[float | None, int, float | None]:
    cells = []
    for f, base in AA_ITEMS.items():
        if f in params:
            s = cc(aa_row.get(f, ""), base)
            if s is not None:
                cells.append((f, s))
    if len(cells) < 3:
        return None, len(cells), None
    best = None
    for t10 in range(800, 2000):
        th = t10 / 10.0
        e = sum((sigmoid(params[f]["slope"] * (th - params[f]["edi"])) - s) ** 2 for f, s in cells)
        if best is None or e < best[0]:
            best = (e, th)
    return best[1], len(cells), math.sqrt(best[0] / len(cells))


def site_table(rungs_mode: str = "curated") -> None:
    """Join the ladder onto the site's 151 models; write site_ladder.tsv."""
    eci, edi, cells = load()
    aa, aliases = load_aa(), load_aliases()
    rungs = sorted(CURATED if rungs_mode == "curated" else list(edi), key=lambda b: float(edi[b]["edi"]))
    params = calibrate_aa_items(eci, aa, aliases)
    print("AA item calibration (on Epoch overlap):")
    for f, p in sorted(params.items(), key=lambda kv: kv[1]["edi"]):
        print(f"   {f:32s} n={p['n']:3d} edi={p['edi']:5.0f} slope={p['slope']:.2f} rmse={p['rmse']:.3f}")
    out = []
    for r in aliases:
        row = {"site_slug": r["site_slug"], "display_name": r["display_name"], "source": "", "theta": "",
               "ladder": "", "ladder_ci_low": "", "ladder_ci_high": "", "measured_rungs": "", "n_rungs": len(rungs),
               "epoch_model": r["epoch_model"], "aa_slug": r["aa_slug"], "note": r["notes"]}
        extra = aa_rung_cells(aa[r["aa_slug"]]) if r["aa_slug"] and r["aa_slug"] in aa else {}
        if r["epoch_model"] and r["epoch_model"] in eci and eci[r["epoch_model"]]["eci"]:
            L = ladder_for(r["epoch_model"], rungs, eci, edi, cells, extra)
            row.update(source=f"epoch ({r['epoch_confidence']})", theta=f"{L['eci']:.1f}", ladder=f"{L['ladder']:.1f}",
                       ladder_ci_low="" if L["ladder_ci_low"] is None else f"{L['ladder_ci_low']:.1f}",
                       ladder_ci_high="" if L["ladder_ci_high"] is None else f"{L['ladder_ci_high']:.1f}",
                       measured_rungs=L["measured_rungs"])
            for b, sc, how in L["rows"]:
                row[f"rung:{b}"], row[f"how:{b}"] = f"{sc:.3f}", how
        elif r["aa_slug"] and r["aa_slug"] in aa:
            th, n, rmse = estimate_theta(aa[r["aa_slug"]], params)
            if th is not None:
                rws = [(b, extra[b], "measured-aa") if b in extra else (b, fitted(th, edi[b]), "provisional") for b in rungs]
                tot = sum(POINTS_PER_RUNG * sc for _, sc, _ in rws)
                row.update(source=f"provisional/aa ({n} cells, rmse {rmse:.2f})", theta=f"{th:.1f}", ladder=f"{tot:.1f}",
                           measured_rungs=sum(1 for _, _, h in rws if h == "measured-aa"))
                for b, sc, how in rws:
                    row[f"rung:{b}"], row[f"how:{b}"] = f"{sc:.3f}", how
            else:
                row.update(source=f"aa row but <3 usable cells")
        else:
            row.update(source="none")
        out.append(row)
    p = HERE / "site_ladder.tsv"
    fields = list(out[0].keys()) + [f"rung:{b}" for b in rungs] + [f"how:{b}" for b in rungs]
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        w.writeheader(); w.writerows(out)
    print(f"wrote {p}: {len(out)} site models; "
          f"epoch={sum(1 for o in out if o['source'].startswith('epoch'))} "
          f"provisional={sum(1 for o in out if o['source'].startswith('provisional'))} "
          f"none={sum(1 for o in out if not o['ladder'])}")


if __name__ == "__main__" and "--site" in sys.argv:
    site_table("all" if "--rungs" in sys.argv and "all" in sys.argv else "curated")
