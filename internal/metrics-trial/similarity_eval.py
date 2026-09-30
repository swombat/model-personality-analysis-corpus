#!/usr/bin/env python3
"""Second pass: evaluation tables for the similarity-metrics trial.

Loads the pickled intermediates from similarity_metrics.py (no TF-IDF
refit) and computes:
  - replicate-pair noise ratios + "are replicates each other's nearest cell"
  - eta^2 of metrics 1-5 across labs (labs with >=3 models, one row/model)
  - version-pair cosine + self-sim + word deltas
  - Ox Alpha attribution
Prints everything so it can be copy-edited into similarity_eval.md.
"""
from __future__ import annotations

import pickle
import re
from collections import defaultdict

import numpy as np

OUT_DIR = "/Users/danieltenner/dev/model-personality-analysis-corpus/internal/metrics-trial"

with open(f"{OUT_DIR}/_intermediate.pkl", "rb") as f:
    D = pickle.load(f)

cell_rows = {r["cell"]: r for r in D["cell_rows"]}
cell_centroid = D["cell_centroid"]
model_centroid = D["model_centroid"]
models_present = D["models_present"]
lab_models = D["lab_models"]
MODEL_LAB = {r["model"]: r["lab"] for r in D["cell_rows"]}

METRICS = ["self_sim_mean", "self_sim_LONG", "self_sim_p90", "centroid_norm_spread", "motif_concentration"]

# per-cell cosine matrix restricted to cells (cheap: 281 cells x 20000 dims)
cells_sorted = sorted(cell_centroid.keys())
Cmat = np.stack([cell_centroid[c] for c in cells_sorted])
cell_sim = Cmat @ Cmat.T
cell_idx = {c: i for i, c in enumerate(cells_sorted)}


def nearest_cell(cell, exclude=()):
    i = cell_idx[cell]
    sims = cell_sim[i].copy()
    sims[i] = -np.inf
    for e in exclude:
        if e in cell_idx:
            sims[cell_idx[e]] = -np.inf
    j = int(np.argmax(sims))
    return cells_sorted[j], float(sims[j])


def norm_lab(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# ---------------------------------------------------------------------------
# 1. Build replicate/noise pairs
# ---------------------------------------------------------------------------
pairs = []  # (label, cellA, cellB)

for c in cells_sorted:
    for suf in ("-r2", "-r3"):
        if c.endswith(suf):
            base = c[: -len(suf)]
            if base in cell_idx:
                pairs.append((f"replicate{suf}", base, c))

if "ox-alpha-or-pin-stealth-20260821" in cell_idx and "ox-alpha-260825-or-pin-stealth" in cell_idx:
    pairs.append(("ox-alpha-date-repin", "ox-alpha-or-pin-stealth-20260821", "ox-alpha-260825-or-pin-stealth"))

# <model>-direct vs <model>-or-pin-<same lab>
model_cells = defaultdict(list)
for c, r in cell_rows.items():
    model_cells[r["model"]].append(c)

for model, cells in model_cells.items():
    lab = MODEL_LAB.get(model, "unknown")
    ln = norm_lab(lab)
    direct_cells = [c for c in cells if c == model or c.startswith(model + "-direct")]
    pin_cells = [c for c in cells if "-or-pin-" in c]
    for dc in direct_cells:
        for pc in pin_cells:
            pin = pc.split("-or-pin-")[-1]
            if norm_lab(pin) == ln and ln:
                pairs.append(("direct-vs-same-lab-pin", dc, pc))

print(f"Found {len(pairs)} replicate/noise pairs")
for label, a, b in pairs:
    print(f"  [{label}] {a}  <->  {b}")

# noise ratio: mean|delta| / SD across cells, per metric
cell_vals = {m: np.array([cell_rows[c][m] for c in cells_sorted]) for m in METRICS}
cell_sd = {m: np.nanstd(cell_vals[m]) for m in METRICS}

print("\n=== Replicate-pair deltas ===")
per_metric_abs_deltas = defaultdict(list)
nn_hits = 0
nn_total = 0
for label, a, b in pairs:
    if a not in cell_rows or b not in cell_rows:
        continue
    row = {"pair": f"{a} vs {b}", "type": label}
    for m in METRICS:
        d = abs(cell_rows[a][m] - cell_rows[b][m])
        per_metric_abs_deltas[m].append(d)
    # nearest-neighbour sanity check (exclude nothing else)
    nn_a, sim_a = nearest_cell(a)
    nn_b, sim_b = nearest_cell(b)
    is_nn = (nn_a == b) or (nn_b == a)
    nn_total += 1
    nn_hits += int(is_nn)
    print(f"{label:24s} {a:45s} vs {b:45s} mutual_nearest={is_nn} (a's nearest={nn_a} sim={sim_a:.3f}; b's nearest={nn_b} sim={sim_b:.3f})")

print(f"\nReplicate mutual-nearest-neighbour rate: {nn_hits}/{nn_total} = {nn_hits/nn_total:.2f}")

print("\n=== Noise ratio (mean|delta| across replicate pairs / SD across all cells) ===")
for m in METRICS:
    dv = np.array(per_metric_abs_deltas[m])
    ratio = dv.mean() / cell_sd[m] if cell_sd[m] > 0 else float("nan")
    print(f"{m:22s} mean|delta|={dv.mean():.4f}  SD_across_cells={cell_sd[m]:.4f}  noise_ratio={ratio:.3f}")

# ---------------------------------------------------------------------------
# 2. eta^2 across labs (labs with >=3 models), one row per model (avg over its cells)
# ---------------------------------------------------------------------------
model_metric_avg = defaultdict(dict)
for model, cells in model_cells.items():
    for m in METRICS:
        vals = [cell_rows[c][m] for c in cells if not np.isnan(cell_rows[c][m])]
        model_metric_avg[model][m] = float(np.mean(vals)) if vals else float("nan")

lab_model_count = {lab: len(mods) for lab, mods in lab_models.items()}
labs_ge3 = [lab for lab, n in lab_model_count.items() if n >= 3 and lab != "unknown"]
print(f"\n=== Labs with >=3 models: {labs_ge3} ===")

print("\n=== eta^2 of metrics 1-5 across labs (model-level rows) ===")
eta2_results = {}
for m in METRICS:
    rows = []
    for lab in labs_ge3:
        for model in lab_models[lab]:
            v = model_metric_avg[model][m]
            if not np.isnan(v):
                rows.append((lab, v))
    if len(rows) < 4:
        continue
    vals = np.array([v for _, v in rows])
    grand_mean = vals.mean()
    ss_total = ((vals - grand_mean) ** 2).sum()
    ss_between = 0.0
    for lab in labs_ge3:
        gv = np.array([v for l, v in rows if l == lab])
        if len(gv) == 0:
            continue
        ss_between += len(gv) * (gv.mean() - grand_mean) ** 2
    eta2 = ss_between / ss_total if ss_total > 0 else float("nan")
    eta2_results[m] = eta2
    print(f"{m:22s} eta^2={eta2:.3f}  (n_models={len(rows)}, n_labs={len(labs_ge3)})")

# ---------------------------------------------------------------------------
# 3. LOO lab classification (already computed in main pass)
# ---------------------------------------------------------------------------
print(f"\n=== LOO nearest-centroid lab classification ===")
print(f"Overall accuracy: {D['loo_accuracy']:.3f}")
for lab in sorted(D["per_lab_total"].keys(), key=lambda l: -D["per_lab_total"][l]):
    c = D["per_lab_correct"].get(lab, 0)
    t = D["per_lab_total"][lab]
    print(f"  {lab:20s} {c}/{t} = {c/t:.2f}")

# ---------------------------------------------------------------------------
# 4. Version pairs
# ---------------------------------------------------------------------------
def canonical_cell(model):
    cells = model_cells.get(model, [])
    if not cells:
        return None
    def tag(c):
        return c[len(model) + 1:] if c.startswith(model + "-") else ("" if c == model else None)
    tagged = [(c, tag(c)) for c in cells]
    tagged = [(c, t) for c, t in tagged if t is not None]
    for want in ("direct",):
        for c, t in tagged:
            if t == want:
                return c
    for c, t in tagged:
        if t.startswith("direct"):
            return c
    for c, t in tagged:
        if t == "or":
            return c
    pins = sorted((c, t) for c, t in tagged if t.startswith("or-pin-"))
    if pins:
        return pins[0][0]
    return tagged[0][0] if tagged else None


VERSION_CHAINS = [
    ("gemini-3-7-flash", "gemini-3-8-flash"),
    ("fable-5", "fable-5-1"),
    ("opus-4-6", "opus-4-7"),
    ("opus-4-7", "opus-5"),
    ("gpt-5-4", "gpt-5-5"),
    ("gpt-5-5", "gpt-5-6-luna"),
    ("gpt-5-5", "gpt-5-6-sol"),
    ("gpt-5-5", "gpt-5-6-terra"),
    ("glm-4-6", "glm-4-7"),
    ("glm-4-7", "glm-5-1"),
    ("glm-5-1", "glm-5-3"),
]

print("\n=== Version pairs ===")
for old, new in VERSION_CHAINS:
    if old not in model_centroid or new not in model_centroid:
        print(f"{old} -> {new}: SKIP (model not present: {[m for m in (old,new) if m not in model_centroid]})")
        continue
    cos = float(model_centroid[old] @ model_centroid[new])
    old_cell = canonical_cell(old)
    new_cell = canonical_cell(new)
    old_self = cell_rows[old_cell]["self_sim_mean"] if old_cell else float("nan")
    new_self = cell_rows[new_cell]["self_sim_mean"] if new_cell else float("nan")
    old_words = set(cell_rows[old_cell]["top30_words"]) if old_cell else set()
    new_words = set(cell_rows[new_cell]["top30_words"]) if new_cell else set()
    entered = new_words - old_words
    left = old_words - new_words
    print(f"\n{old} ({old_cell}) -> {new} ({new_cell})")
    print(f"  model-centroid cosine: {cos:.3f}")
    print(f"  self_sim_mean: {old}={old_self:.3f}  {new}={new_self:.3f}")
    print(f"  words entered (new top30 not in old): {sorted(entered)}")
    print(f"  words left    (old top30 not in new): {sorted(left)}")

# ---------------------------------------------------------------------------
# 5. Ox Alpha attribution
# ---------------------------------------------------------------------------
print("\n=== Ox Alpha attribution ===")
ox_models = [m for m in models_present if m.startswith("ox-alpha")]
print(f"Ox-alpha pseudo-models present: {ox_models}")
for ox in ox_models:
    if ox not in model_centroid:
        continue
    sims = []
    for m in models_present:
        if m == ox or m.startswith("ox-alpha"):
            continue
        sims.append((m, float(model_centroid[ox] @ model_centroid[m])))
    sims.sort(key=lambda t: -t[1])
    print(f"\n{ox} top-5 nearest models:")
    for m, s in sims[:5]:
        print(f"  {m:30s} {MODEL_LAB.get(m,'?'):15s} sim={s:.3f}")
    # lab-centroid ranking
    lab_sims = []
    for lab, mods in lab_models.items():
        if lab == "unknown":
            continue
        mods2 = [x for x in mods if not x.startswith("ox-alpha")]
        if not mods2:
            continue
        vecs = np.stack([model_centroid[x] for x in mods2])
        c = vecs.mean(axis=0)
        c = c / np.linalg.norm(c)
        lab_sims.append((lab, float(model_centroid[ox] @ c)))
    lab_sims.sort(key=lambda t: -t[1])
    print(f"{ox} lab-centroid ranking (top 5): {lab_sims[:5]}")
    glm53 = [(m, s) for m, s in sims if "glm-5-3" in m]
    print(f"  GLM-5.3 rank check: {glm53}")

print("\nDONE")
