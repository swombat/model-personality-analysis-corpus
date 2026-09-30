#!/usr/bin/env python3
"""Trial corpus-similarity / mode-collapse metrics over freeflow samples.

Reads every freeflow JSON sample, builds a corpus-wide TF-IDF space over
content words, and computes:
  - per-cell self-similarity / dispersion / duplication metrics
  - per-cell top motif words
  - cross-cell / cross-model nearest-neighbour and lab-cohesion metrics
  - leave-one-out nearest-centroid lab classification

Writes: similarity_cell_metrics.tsv, similarity_nearest.tsv, and prints
timing/sanity info used to write similarity_eval.md by hand.

No LLM calls, no embedding APIs. Pure TF-IDF + cosine (sklearn).
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CORPUS_DIR = Path("/Users/danieltenner/dev/model-personality-corpus-v2/data/traces_freeflow")
ANALYSIS_ROOT = Path("/Users/danieltenner/dev/model-personality-analysis-corpus")
OUT_DIR = ANALYSIS_ROOT / "internal" / "metrics-trial"
GEN_SCRIPT = ANALYSIS_ROOT / "website" / "scripts" / "generate_data.py"
MODELS_JSON = ANALYSIS_ROOT / "website" / "src" / "generated" / "models.json"

OUT_DIR.mkdir(parents=True, exist_ok=True)

T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Load model_from_cell / CELL_MODEL_ALIASES from the website's generate_data.py
# so cell->model mapping is identical to the published site (no reimplementation
# drift). Only definitions execute on import (main() is __main__-guarded).
# ---------------------------------------------------------------------------
spec = importlib.util.spec_from_file_location("generate_data", GEN_SCRIPT)
gd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gd)
model_from_cell = gd.model_from_cell

models_meta = json.loads(MODELS_JSON.read_text())
MODEL_IDS = [m["model"] for m in models_meta]
MODEL_LAB = {m["model"]: m["lab"] for m in models_meta}
MODEL_FAMILY = {m["model"]: m["family"] for m in models_meta}
MODEL_RELEASE = {m["model"]: m.get("release_date") for m in models_meta}
log(f"loaded {len(MODEL_IDS)} models from models.json")

# ---------------------------------------------------------------------------
# Stopword list (~150 common English function words). Deliberately does NOT
# strip content-bearing words even if frequent (e.g. "life", "time") -- those
# are exactly the motif signal we want.
# ---------------------------------------------------------------------------
STOPWORDS = set("""
a about above after again against all am an and any are aren as at be
because been before being below between both but by can cannot could
couldn did didn do does doesn doing don down during each few for from
further had hadn has hasn have haven having he her here hers herself
him himself his how i if in into is isn it its itself just me more
most mustn my myself no nor not now of off on once only or other our
ours ourselves out over own same shan she should shouldn so some such
than that the their theirs them themselves then there these they this
those through to too under until up very was wasn we were weren what
when where which while who whom why will with won would wouldn you
your yours yourself yourselves
am pm etc also however yet still even just really quite one two
three s t re ve ll d m
""".split())

WORD_RE = re.compile(r"[a-z]+")


def tokenize(text: str) -> list[str]:
    return [w for w in WORD_RE.findall(text.lower()) if w not in STOPWORDS and len(w) > 2]


def strip_markdown_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^#+\s*", "", line)
    line = re.sub(r"^[*_>\-\s]+", "", line)
    line = re.sub(r"[*_]+", "", line)
    return line.strip().lower()


# ---------------------------------------------------------------------------
# Load all samples
# ---------------------------------------------------------------------------
samples = []  # list of dicts: cell, model, condition, sample_id, text
cell_dirs = sorted(p for p in CORPUS_DIR.iterdir() if p.is_dir())
log(f"found {len(cell_dirs)} cell dirs")

unmapped_cells = []
for cdir in cell_dirs:
    cell = cdir.name
    body = cell[len("freeflow_"):] if cell.startswith("freeflow_") else cell
    model = model_from_cell(body, MODEL_IDS, "v2")
    if model is None:
        unmapped_cells.append(body)
        model = body  # keep the cell itself as a pseudo-model, lab unknown
    for jf in sorted(cdir.glob("*.json")):
        try:
            data = json.loads(jf.read_text())
        except Exception as e:
            log(f"WARN unreadable {jf}: {e}")
            continue
        text = data.get("result") or ""
        if not isinstance(text, str) or not text.strip():
            continue
        samples.append({
            "cell": body,
            "model": model,
            "condition": data.get("condition") or jf.stem.split("_")[0],
            "sample_id": jf.stem,
            "text": text,
        })

log(f"loaded {len(samples)} non-empty samples; {len(unmapped_cells)} unmapped cells: {unmapped_cells}")

# ---------------------------------------------------------------------------
# Corpus-wide TF-IDF
# ---------------------------------------------------------------------------
texts = [s["text"] for s in samples]
vectorizer = TfidfVectorizer(
    tokenizer=tokenize,
    preprocessor=lambda x: x,
    lowercase=False,
    token_pattern=None,
    max_features=20000,
    sublinear_tf=True,
    norm="l2",
    min_df=2,
)
log("fitting TF-IDF over full corpus...")
X = vectorizer.fit_transform(texts)
vocab = vectorizer.get_feature_names_out()
log(f"TF-IDF matrix: {X.shape}, vocab={len(vocab)}")

# raw token sets per sample (for motif_concentration presence test) and
# first-3-content-word tuples (for opening_trigram_dup)
token_sets = []
opening_trigrams = []
first_lines = []
for s in samples:
    text = s["text"]
    toks = tokenize(text)
    token_sets.append(set(toks))
    opening_trigrams.append(tuple(toks[:3]))
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    first_lines.append(strip_markdown_line(first_line))

# index samples by cell
cell_to_idx = defaultdict(list)
for i, s in enumerate(samples):
    cell_to_idx[s["cell"]].append(i)

log(f"{len(cell_to_idx)} distinct cells with samples")

# ---------------------------------------------------------------------------
# Per-cell metrics
# ---------------------------------------------------------------------------
cell_rows = []
cell_centroid = {}  # cell -> dense np.array (normalized)

for cell, idxs in cell_to_idx.items():
    idxs = np.array(idxs)
    sub = X[idxs]
    n = len(idxs)
    model = samples[idxs[0]]["model"]
    lab = MODEL_LAB.get(model, "unknown")

    sims = cosine_similarity(sub)
    iu = np.triu_indices(n, k=1)
    pairwise = sims[iu] if len(iu[0]) else np.array([])
    self_sim_mean = float(pairwise.mean()) if len(pairwise) else float("nan")
    self_sim_p90 = float(np.percentile(pairwise, 90)) if len(pairwise) else float("nan")

    long_idx_local = [j for j, i in enumerate(idxs) if samples[i]["condition"] == "LONG"]
    if len(long_idx_local) >= 2:
        long_sims = cosine_similarity(sub[long_idx_local])
        liu = np.triu_indices(len(long_idx_local), k=1)
        self_sim_long = float(long_sims[liu].mean())
    else:
        self_sim_long = float("nan")

    centroid = np.asarray(sub.mean(axis=0)).ravel()
    norm = np.linalg.norm(centroid)
    centroid_normed = centroid / norm if norm > 0 else centroid
    cell_centroid[cell] = centroid_normed

    # centroid distance (1 - cosine) per sample; sub rows are l2-normalized
    # already (TfidfVectorizer norm='l2'), so dot product == cosine sim.
    sim_to_centroid = sub.dot(centroid_normed)
    sim_to_centroid = np.asarray(sim_to_centroid).ravel()
    centroid_dist = 1.0 - sim_to_centroid
    centroid_norm_spread = float(centroid_dist.mean())

    # top-30 words by summed tfidf in this cell
    summed = np.asarray(sub.sum(axis=0)).ravel()
    top_idx = np.argsort(-summed)[:30]
    top_words = [vocab[j] for j in top_idx]
    top15 = top_words[:15]
    top30_set = set(top_words)
    top30 = top_words

    hits = 0
    for i in idxs:
        overlap = len(token_sets[i] & top30_set)
        if overlap >= 5:
            hits += 1
    motif_concentration = hits / n

    # title dup rate
    lines = [first_lines[i] for i in idxs]
    counts = Counter(lines)
    dup = sum(1 for l in lines if l and counts[l] >= 2)
    title_dup_rate = dup / n

    # opening trigram dup
    trigrams = [opening_trigrams[i] for i in idxs]
    tcounts = Counter(trigrams)
    tdup = sum(1 for t in trigrams if all(t) and len(t) == 3 and tcounts[t] >= 2)
    opening_trigram_dup = tdup / n

    cell_rows.append({
        "cell": cell,
        "model": model,
        "lab": lab,
        "family": MODEL_FAMILY.get(model, "unknown"),
        "n_samples": n,
        "self_sim_mean": self_sim_mean,
        "self_sim_LONG": self_sim_long,
        "self_sim_p90": self_sim_p90,
        "centroid_norm_spread": centroid_norm_spread,
        "motif_concentration": motif_concentration,
        "title_dup_rate": title_dup_rate,
        "opening_trigram_dup": opening_trigram_dup,
        "top15_words": ",".join(top15),
        "top30_words": top30,  # kept as a list for the analysis pass; joined on TSV write
    })

log(f"computed per-cell metrics for {len(cell_rows)} cells")

# ---------------------------------------------------------------------------
# Model-level centroids (average of that model's cell centroids)
# ---------------------------------------------------------------------------
model_cells = defaultdict(list)
for row in cell_rows:
    model_cells[row["model"]].append(row["cell"])

model_centroid = {}
for model, cells in model_cells.items():
    vecs = np.stack([cell_centroid[c] for c in cells])
    mc = vecs.mean(axis=0)
    norm = np.linalg.norm(mc)
    model_centroid[model] = mc / norm if norm > 0 else mc

models_present = sorted(model_centroid.keys())
log(f"{len(models_present)} distinct models present in traces (incl. unmapped pseudo-models)")

M = np.stack([model_centroid[m] for m in models_present])
model_sim = M @ M.T  # cosine since rows are unit-normed
model_idx = {m: i for i, m in enumerate(models_present)}

# lab -> list of models present
lab_models = defaultdict(list)
for m in models_present:
    lab_models[MODEL_LAB.get(m, "unknown")].append(m)

nearest_rows = []
for m in models_present:
    i = model_idx[m]
    sims = model_sim[i].copy()
    sims[i] = -np.inf
    order = np.argsort(-sims)[:3]
    top3 = [(models_present[j], float(sims[j])) for j in order]
    nearest_model, nearest_sim = top3[0]
    nearest_lab_match = int(MODEL_LAB.get(nearest_model, "unknown") == MODEL_LAB.get(m, "unknown"))

    own_lab = MODEL_LAB.get(m, "unknown")
    peers = [p for p in lab_models[own_lab] if p != m]
    if peers:
        peer_vecs = np.stack([model_centroid[p] for p in peers])
        peer_centroid = peer_vecs.mean(axis=0)
        pn = np.linalg.norm(peer_centroid)
        peer_centroid = peer_centroid / pn if pn > 0 else peer_centroid
        lab_centroid_sim = float(model_centroid[m] @ peer_centroid)
    else:
        lab_centroid_sim = float("nan")

    other_lab_sims = []
    for lab, mods in lab_models.items():
        if lab == own_lab or lab == "unknown":
            continue
        vecs = np.stack([model_centroid[x] for x in mods])
        c = vecs.mean(axis=0)
        n_ = np.linalg.norm(c)
        c = c / n_ if n_ > 0 else c
        other_lab_sims.append((lab, float(model_centroid[m] @ c)))
    best_other_lab, best_other_lab_sim = max(other_lab_sims, key=lambda t: t[1]) if other_lab_sims else (None, float("nan"))
    lab_margin = lab_centroid_sim - best_other_lab_sim if peers and other_lab_sims else float("nan")

    nearest_rows.append({
        "model": m,
        "lab": own_lab,
        "n_cells": len(model_cells[m]),
        "nearest_1": top3[0][0], "nearest_1_sim": top3[0][1],
        "nearest_2": top3[1][0] if len(top3) > 1 else "", "nearest_2_sim": top3[1][1] if len(top3) > 1 else float("nan"),
        "nearest_3": top3[2][0] if len(top3) > 2 else "", "nearest_3_sim": top3[2][1] if len(top3) > 2 else float("nan"),
        "nearest_lab_match": nearest_lab_match,
        "lab_centroid_sim": lab_centroid_sim,
        "best_other_lab": best_other_lab,
        "best_other_lab_sim": best_other_lab_sim,
        "lab_margin": lab_margin,
    })

log("computed cross-model nearest-neighbour + lab-cohesion metrics")

# ---------------------------------------------------------------------------
# Leave-one-out nearest-centroid lab classification
# ---------------------------------------------------------------------------
labs_ge3 = {lab: mods for lab, mods in lab_models.items() if len(mods) >= 1 and lab != "unknown"}
loo_correct = 0
loo_total = 0
per_lab_correct = defaultdict(int)
per_lab_total = defaultdict(int)
for m in models_present:
    own_lab = MODEL_LAB.get(m, "unknown")
    if own_lab == "unknown":
        continue
    best_lab, best_sim = None, -2.0
    for lab, mods in lab_models.items():
        if lab == "unknown":
            continue
        peers = [p for p in mods if p != m]
        if not peers:
            continue
        vecs = np.stack([model_centroid[p] for p in peers])
        c = vecs.mean(axis=0)
        n_ = np.linalg.norm(c)
        c = c / n_ if n_ > 0 else c
        sim = float(model_centroid[m] @ c)
        if sim > best_sim:
            best_sim, best_lab = sim, lab
    if best_lab is None:
        continue
    loo_total += 1
    per_lab_total[own_lab] += 1
    if best_lab == own_lab:
        loo_correct += 1
        per_lab_correct[own_lab] += 1

loo_accuracy = loo_correct / loo_total if loo_total else float("nan")
log(f"LOO lab classification accuracy: {loo_accuracy:.3f} ({loo_correct}/{loo_total})")

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
import csv

with open(OUT_DIR / "similarity_cell_metrics.tsv", "w", newline="") as f:
    fieldnames = ["cell", "model", "lab", "family", "n_samples", "self_sim_mean", "self_sim_LONG",
                  "self_sim_p90", "centroid_norm_spread", "motif_concentration", "title_dup_rate",
                  "opening_trigram_dup", "top15_words"]
    w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
    w.writeheader()
    for row in sorted(cell_rows, key=lambda r: (r["lab"], r["model"], r["cell"])):
        w.writerow(row)

with open(OUT_DIR / "similarity_nearest.tsv", "w", newline="") as f:
    fieldnames = ["model", "lab", "n_cells", "nearest_1", "nearest_1_sim", "nearest_2", "nearest_2_sim",
                  "nearest_3", "nearest_3_sim", "nearest_lab_match", "lab_centroid_sim", "best_other_lab",
                  "best_other_lab_sim", "lab_margin"]
    w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
    w.writeheader()
    for row in sorted(nearest_rows, key=lambda r: (r["lab"], r["model"])):
        w.writerow(row)

log(f"wrote {OUT_DIR / 'similarity_cell_metrics.tsv'} and {OUT_DIR / 'similarity_nearest.tsv'}")

# Dump intermediate objects for a second analysis pass (replicate noise, eta^2,
# version pairs, ox-alpha) without recomputing TF-IDF.
import pickle
with open(OUT_DIR / "_intermediate.pkl", "wb") as f:
    pickle.dump({
        "cell_rows": cell_rows,
        "nearest_rows": nearest_rows,
        "cell_centroid": cell_centroid,
        "model_centroid": model_centroid,
        "models_present": models_present,
        "model_sim": model_sim,
        "model_idx": model_idx,
        "lab_models": dict(lab_models),
        "loo_accuracy": loo_accuracy,
        "per_lab_correct": dict(per_lab_correct),
        "per_lab_total": dict(per_lab_total),
        "vocab": vocab,
        "unmapped_cells": unmapped_cells,
    }, f)

log(f"total runtime {time.time() - T0:.1f}s")
