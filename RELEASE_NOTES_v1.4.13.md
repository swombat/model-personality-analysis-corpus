# Release notes — v1.4.13

Prepared 2026-09-18.

## Map: findings restored, layouts stable between releases

- Method section regains the external checks the similarity matrix has passed, with numbers read from
  the shipped data: Ox Alpha ↔ GLM-5.3-Flash 0.959 (confirmed by Z.ai), the two Ox Alpha snapshots
  0.967, GPT-5.5 ↔ 5.5 Pro 0.981 (same weights, different reasoning mode), and Union Alpha ↔ GPT-6
  Astra 0.976 — placed nearest Astra before the route was reported to be a cascade router with Astra
  as its escalation model.
- `generate_map.py` now aligns every projection to the previous release's coordinates (orthogonal
  Procrustes) and seeds UMAP from them, so adding a model no longer re-orients the map. Leave-one-out:
  MDS 3D shift per added model 38% → 3% of map width, MDS 2D 17% → 1%, UMAP ~21% → 7%; PCA was already
  <1%. UMAP still rearranges ~a quarter of on-map neighbourhoods (optimiser, not orientation) — stated
  on the page, with the recommendation to use PCA or 3D MDS for month-to-month comparison.
- Alignment provenance in `generated_from.alignment`; procedure and numbers in `scripts/MAP_TESTING.md`.
