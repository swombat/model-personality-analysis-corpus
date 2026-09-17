#!/usr/bin/env python3
"""Build src/generated/model-map.json — the data behind /map/.

For every published model: the char 3–5-gram TF-IDF centroid of its freeflow
samples, the full centroid cosine-similarity matrix, low-dimensional
projections (PCA, metric MDS, UMAP; 2D and 3D), each projection's
3-nearest-neighbour preservation score, per-model nearest neighbours, and an
average-linkage dendrogram over cosine distance.

Run after generate_data.py (it reads public/data/samples/*.json):
    python3 scripts/generate_map.py
"""
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import linkage, to_tree
from scipy.spatial.distance import squareform

warnings.filterwarnings("ignore")
WEBSITE = Path(__file__).resolve().parents[1]
SAMPLES = WEBSITE / "public" / "data" / "samples"
GENERATED = WEBSITE / "src" / "generated"
OUT = GENERATED / "model-map.json"
K = 3

def knn_preserve(D: np.ndarray, X: np.ndarray, k: int = K) -> float:
    E = euclidean_distances(X)
    np.fill_diagonal(E, np.inf)
    Dn = D.copy(); np.fill_diagonal(Dn, np.inf)
    hi = np.argsort(Dn, axis=1)[:, :k]; lo = np.argsort(E, axis=1)[:, :k]
    return float(np.mean([len(set(hi[i]) & set(lo[i])) / k for i in range(len(X))]))

def main() -> None:
    models_meta = json.loads((GENERATED / "models.json").read_text())
    meta = {m["model"]: m for m in models_meta if m.get("status") != "redirect"}
    docs, labels = [], []
    for f in sorted(SAMPLES.glob("*.json")):
        d = json.loads(f.read_text())
        if d["model"] not in meta:
            continue
        for s in d["samples"]:
            if s["type"] == "freeflow" and s.get("result"):
                docs.append(s["result"]); labels.append(d["model"])
    labels = np.array(labels); models = sorted(set(labels))
    print(f"{len(docs)} freeflow docs across {len(models)} models", file=sys.stderr)
    M = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=200000, sublinear_tf=True).fit_transform(docs)
    C = np.vstack([np.asarray(M[labels == m].mean(axis=0)) for m in models])
    S = cosine_similarity(C); D = 1 - S; np.fill_diagonal(D, 0); D = np.clip(D, 0, None)

    proj: dict[str, np.ndarray] = {}
    pca = PCA(n_components=3).fit(C); P = pca.transform(C)
    proj["pca2"], proj["pca3"] = P[:, :2], P[:, :3]
    var2, var3 = float(pca.explained_variance_ratio_[:2].sum()), float(pca.explained_variance_ratio_[:3].sum())
    for n in (2, 3):
        proj[f"mds{n}"] = MDS(n_components=n, dissimilarity="precomputed", random_state=0, n_init=4, normalized_stress="auto").fit(D).embedding_
    try:
        import umap  # type: ignore
        for n in (2, 3):
            proj[f"umap{n}"] = umap.UMAP(n_components=n, metric="precomputed", random_state=0, n_neighbors=8, min_dist=0.15).fit_transform(D)
    except Exception as e:  # pragma: no cover
        print(f"umap unavailable: {e}", file=sys.stderr)
    preserve = {k: round(knn_preserve(D, X), 3) for k, X in proj.items()}
    print("3-NN preservation:", preserve, f"| PCA variance 2D {var2:.3f} 3D {var3:.3f}", file=sys.stderr)

    # normalise each projection to unit box so the client can treat them alike
    def norm(X):
        X = X - X.mean(axis=0); s = np.abs(X).max() or 1.0
        return (X / s).round(4).tolist()
    idx = {m: i for i, m in enumerate(models)}
    nn = {}
    for i, m in enumerate(models):
        order = np.argsort(-S[i]); order = [j for j in order if j != i][:6]
        nn[m] = [[models[j], round(float(S[i, j]), 3)] for j in order]

    # dendrogram: average linkage on cosine distance
    Z = linkage(squareform(D, checks=False), method="average")
    root = to_tree(Z)
    def node(t):
        if t.is_leaf():
            return {"m": models[t.id]}
        return {"h": round(float(t.dist), 4), "c": [node(t.get_left()), node(t.get_right())]}
    tree = node(root)

    out_models = []
    for i, m in enumerate(models):
        r = meta[m]
        out_models.append({
            "model": m, "display": r.get("display_name", m), "lab": r.get("lab") or "Unknown",
            "family": r.get("family", ""), "strapline": r.get("summary", ""), "date": r.get("release_date"),
            "coords": {k: norm(X)[i] for k, X in proj.items()}, "nn": nn[m],
        })
    payload = {
        "generated_from": {"models": len(models), "freeflow_docs": len(docs), "method": "char_wb 3-5 TF-IDF centroid cosine"},
        "projections": {k: {"knn3": preserve[k], **({"variance": var2} if k == "pca2" else {"variance": var3} if k == "pca3" else {})} for k in proj},
        "models": out_models, "order": models,
        "sim": [[round(float(x), 3) for x in row] for row in S],
        "tree": tree,
    }
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)", file=sys.stderr)

if __name__ == "__main__":
    main()
