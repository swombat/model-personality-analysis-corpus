#!/usr/bin/env python3
"""Build the reproducible, pooled-output similarity data behind /map/.

Run after generate_data.py. Requires numpy, scipy, scikit-learn and umap-learn.
Missing projection dependencies are fatal: never replace a good artifact with
an incomplete payload that the page cannot render.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.cluster.hierarchy import linkage, to_tree
from scipy.spatial.distance import squareform
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import normalize
from scipy.linalg import orthogonal_procrustes

WEBSITE = Path(__file__).resolve().parents[1]
SAMPLES = WEBSITE / 'public/data/samples'
GENERATED = WEBSITE / 'src/generated'
OUT = GENERATED / 'model-map.json'
K = 3
SEED = 0
PRECISION = 6
FEATURES = dict(analyzer='char_wb', ngram_range=(3, 5), min_df=2,
                max_features=200000, sublinear_tf=True, norm='l2')


def nearest_indices(distances: np.ndarray, k: int) -> np.ndarray:
    """Stable model-order tie breaking, excluding self even for duplicates."""
    matrix = distances.copy()
    np.fill_diagonal(matrix, np.inf)
    return np.argsort(matrix, axis=1, kind='stable')[:, :min(k, len(matrix) - 1)]


def normalise_projection(x: np.ndarray) -> np.ndarray:
    """One uniform scale, never separate per-axis stretching."""
    x = np.asarray(x, dtype=np.float64)
    x = x - x.mean(axis=0)
    scale = np.abs(x).max() or 1.0
    return np.round(x / scale, PRECISION)


def load_previous_coords() -> tuple[dict, str | None]:
    """Previous release's per-projection coordinates, used only to keep the map's orientation stable."""
    if not OUT.exists():
        return {}, None
    try:
        previous = json.loads(OUT.read_text())
    except json.JSONDecodeError:
        return {}, None
    coords = {}
    for m in previous.get('models', []):
        for key, xy in (m.get('coords') or {}).items():
            coords.setdefault(key, {})[m['model']] = np.asarray(xy, dtype=np.float64)
    return coords, (previous.get('generated_from') or {}).get('repository_base_revision')


def align_to_previous(x: np.ndarray, models: list[str], previous: dict, min_common: int = 8) -> tuple[np.ndarray, dict | None]:
    """Rotate/reflect/scale/translate x so models present last release land where they were.

    Orthogonal Procrustes on the common models; applied to every row. It never
    distorts the layout (no shear, no per-axis scaling) - it only removes the
    arbitrary orientation that MDS and UMAP are free to choose on each run.
    """
    common = [i for i, m in enumerate(models) if m in previous]
    if len(common) < min_common:
        return x, None
    a = x[common]
    b = np.vstack([previous[models[i]] for i in common])
    mean_a, mean_b = a.mean(axis=0), b.mean(axis=0)
    a0, b0 = a - mean_a, b - mean_b
    rotation, _ = orthogonal_procrustes(a0, b0)
    scale = float(np.sum(b0 * (a0 @ rotation)) / max(np.sum(a0 * a0), 1e-12))
    aligned = scale * (x - mean_a) @ rotation + mean_b
    residual = aligned[common] - b
    disparity = float(np.sum(residual ** 2) / max(np.sum(b0 ** 2), 1e-12))
    return aligned, {'common_models': len(common), 'disparity': round(disparity, 4)}


def umap_init_from_previous(models: list[str], previous: dict, similarity: np.ndarray, dimensions: int):
    """Start UMAP from last release's layout; new models start at the mean of their nearest previous neighbours."""
    known = [i for i, m in enumerate(models) if m in previous]
    if len(known) < max(8, len(models) // 2):
        return 'spectral'
    init = np.zeros((len(models), dimensions))
    known_set = set(known)
    for i, m in enumerate(models):
        if i in known_set:
            init[i] = previous[m][:dimensions]
        else:
            order = [j for j in np.argsort(-similarity[i]) if j != i and j in known_set][:5]
            init[i] = np.mean([previous[models[j]][:dimensions] for j in order], axis=0)
    return init


def projection_quality(distances: np.ndarray, x: np.ndarray, k: int = K) -> dict:
    """Measure the shipped precision, not higher-precision hidden coordinates."""
    embedded = euclidean_distances(x)
    original_nn = nearest_indices(distances, k)
    projected_nn = nearest_indices(embedded, k)
    actual_k = original_nn.shape[1]
    retained = [len(set(a) & set(b)) for a, b in zip(original_nn, projected_nn)]
    upper = np.triu_indices(len(x), 1)
    target, fitted = distances[upper], embedded[upper]
    # Coordinates have arbitrary units. Fit a single scale before measuring error.
    denom = float(np.dot(fitted, fitted))
    scale = float(np.dot(fitted, target) / denom) if denom else 0.0
    target_energy = float(np.dot(target, target))
    stress = float(np.sqrt(np.sum((scale * fitted - target) ** 2) / target_energy)) if target_energy else 0.0
    return {'knn3': float(np.mean(retained) / actual_k) if actual_k else 1.0,
            'k': actual_k, 'retained': retained, 'projected_nn': projected_nn.tolist(),
            'distance_error': stress}


def sample_provenance(samples: list[dict]) -> dict:
    cells = Counter((s.get('source', 'unknown'), s.get('cell', 'unknown')) for s in samples)
    # Published bundles currently omit collection timestamps. Never substitute
    # a release date, filename date or filesystem mtime for an observation date.
    dates = []
    for sample in samples:
        timestamp = sample.get('collected_at') or sample.get('timestamp')
        if timestamp:
            dates.append(str(timestamp)[:10])
    return {
        'samples': len(samples), 'cell_count': len(cells),
        'cells': [{'source': source, 'cell': cell, 'samples': n}
                  for (source, cell), n in sorted(cells.items())],
        'conditions': dict(sorted(Counter(s.get('condition', 'unknown') for s in samples).items())),
        'capture_dates': {'min': min(dates), 'max': max(dates), 'known_samples': len(dates)} if dates else None,
    }


def main() -> None:
    import umap  # Required; fail before writing if it is unavailable.

    meta_path = GENERATED / 'models.json'
    meta_bytes = meta_path.read_bytes()
    meta = {m['model']: m for m in json.loads(meta_bytes) if m.get('status') != 'redirect'}
    fingerprint = hashlib.sha256()
    fingerprint.update(b'models.json\0' + meta_bytes + b'\0')
    docs, labels, provenance = [], [], {}
    for path in sorted(SAMPLES.glob('*.json')):
        raw = path.read_bytes()
        data = json.loads(raw)
        if data['model'] not in meta:
            continue
        samples = [s for s in data['samples'] if s['type'] == 'freeflow' and s.get('result')]
        if not samples:
            continue
        fingerprint.update(path.name.encode() + b'\0' + raw + b'\0')
        provenance[data['model']] = sample_provenance(samples)
        docs.extend(s['result'] for s in samples)
        labels.extend([data['model']] * len(samples))
    labels = np.array(labels)
    models = sorted(set(labels))
    if len(models) < 4:
        raise ValueError('Map requires at least four sampled models')
    print(f'{len(docs)} freeflow docs across {len(models)} models', file=sys.stderr, flush=True)
    matrix = TfidfVectorizer(**FEATURES).fit_transform(docs)
    centroids = np.vstack([np.asarray(matrix[labels == m].mean(axis=0)) for m in models])
    # Cosine ignores centroid length. PCA now shares that directional geometry,
    # rather than mixing it with differences in within-model sample dispersion.
    centroids = normalize(centroids)
    similarity = np.clip(np.round(cosine_similarity(centroids), PRECISION), -1, 1)
    np.fill_diagonal(similarity, 1)
    distances = np.maximum(1 - similarity, 0)

    previous_coords, previous_revision = load_previous_coords()
    projections = {}
    pca = PCA(n_components=3, svd_solver='full').fit(centroids)
    coordinates = pca.transform(centroids)
    projections['pca2'], projections['pca3'] = coordinates[:, :2], coordinates[:, :3]
    for dimensions in (2, 3):
        projections[f'mds{dimensions}'] = MDS(
            n_components=dimensions, dissimilarity='precomputed', random_state=SEED,
            n_init=4, normalized_stress='auto').fit_transform(distances)
        projections[f'umap{dimensions}'] = umap.UMAP(
            n_components=dimensions, metric='precomputed', random_state=SEED,
            n_neighbors=8, min_dist=0.15, n_jobs=1,
            init=umap_init_from_previous(models, previous_coords.get(f'umap{dimensions}', {}), similarity, dimensions)
        ).fit_transform(distances)
    # Stability across releases: orient every projection to last release's layout.
    alignment = {}
    for key in list(projections):
        projections[key], alignment[key] = align_to_previous(projections[key], models, previous_coords.get(key, {}))
    projections = {key: normalise_projection(x) for key, x in projections.items()}
    print('alignment to previous release:', alignment, file=sys.stderr, flush=True)
    quality = {key: projection_quality(distances, x) for key, x in projections.items()}
    print('3-NN preservation:', {key: round(q['knn3'], 3) for key, q in quality.items()}, file=sys.stderr, flush=True)
    neighbours = nearest_indices(distances, 6)

    tree_root = to_tree(linkage(squareform(distances, checks=True), method='average'))
    def tree_node(node):
        if node.is_leaf():
            return {'m': models[node.id]}
        return {'h': round(float(node.dist), PRECISION),
                'c': [tree_node(node.get_left()), tree_node(node.get_right())]}

    out_models = []
    for i, model in enumerate(models):
        row = meta[model]
        out_models.append({
            'model': model, 'display': row.get('display_name', model),
            'lab': row.get('lab') or 'Unknown', 'family': row.get('family', ''),
            'strapline': row.get('summary', ''), 'date': row.get('release_date'),
            'coords': {key: x[i].tolist() for key, x in projections.items()},
            'nn': [[models[j], float(similarity[i, j])] for j in neighbours[i]],
            'fidelity': {key: {'retained': q['retained'][i], 'k': q['k'],
                              'projected_nn': [models[j] for j in q['projected_nn'][i]]}
                         for key, q in quality.items()},
            'provenance': provenance[model],
        })
    revision = subprocess.check_output(['git', '-C', str(WEBSITE), 'rev-parse', 'HEAD'], text=True).strip()
    payload = {
        'schema_version': 2,
        'generated_from': {
            'models': len(models), 'freeflow_docs': len(docs),
            'method': 'char_wb 3-5 TF-IDF mean-centroid cosine',
            'weighting': 'equal response weights within each pooled model; corpus-wide sample-weighted IDF',
            'input_sha256': fingerprint.hexdigest(),
            'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'repository_base_revision': revision,
            'alignment': {'reference_revision': previous_revision, 'method': 'orthogonal Procrustes to previous coordinates; UMAP initialised from them',
                          'projections': alignment},
            'versions': {p: importlib.metadata.version(p) for p in ['numpy', 'scikit-learn', 'scipy', 'umap-learn']},
            'parameters': {'tfidf': FEATURES, 'seed': SEED, 'precision': PRECISION,
                           'pca': {'normalise_centroids': True, 'svd_solver': 'full'},
                           'mds': {'metric': True, 'n_init': 4, 'normalized_stress': 'auto'},
                           'umap': {'n_neighbors': 8, 'min_dist': 0.15, 'metric': 'precomputed', 'n_jobs': 1}},
        },
        'projections': {key: {'knn3': q['knn3'], 'k': q['k'], 'distance_error': q['distance_error'],
                              **({'variance': float(pca.explained_variance_ratio_[:int(key[-1])].sum())}
                                 if key.startswith('pca') else {})}
                        for key, q in quality.items()},
        'models': out_models, 'order': models, 'sim': similarity.tolist(), 'tree': tree_node(tree_root),
    }
    encoded = json.dumps(payload, separators=(',', ':'), allow_nan=False)
    temp = OUT.with_suffix('.tmp')
    temp.write_text(encoded)
    temp.replace(OUT)
    print(f'wrote {OUT} ({OUT.stat().st_size // 1024} KB)', file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
