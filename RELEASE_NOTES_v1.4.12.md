# Release notes — v1.4.12

Prepared 2026-09-17. Map fidelity, interpretation and interaction fixes.

- Preserve equal coordinate units in 2D and 3D; filtering does not rescale the map.
- Preserve the full camera, including its up direction, across ordinary redraws and when returning to a projection.
- Rename the dendrogram “Similarity tree” and remove losslessness, ancestry and causal training claims. Explain the limits of average-linkage clustering, MDS, pooled samples and release-order sequences.
- Report mean top-three neighbour retention explicitly as an average, with selected-model retention and projected-neighbour markers in cards.
- Show per-model response, cell and condition counts; unknown capture dates remain explicitly unavailable. Add provenance fingerprints, dependency versions, parameters and a seed to the generated payload.
- Calculate fidelity at the precision actually shipped. Store six-decimal cosine similarities/coordinates with stable tie breaking. MDS includes an explicit relative distance-error diagnostic.
- Normalise centroids before PCA to align with cosine's directional comparison. Regeneration and higher input precision can change projection layouts; no raw samples changed and existing cosine similarities agree to their old rounding precision.
- Add family-grouped release sequences, keyboard tree activation, hidden-model reveal controls and mobile-collapsed filters.
- Missing UMAP stops generation instead of producing an incomplete map.
- Add numerical and browser regression suites. The browser suite uses real pointer rotation, checks all six projection modes for equal units, and exercises provenance, filtering, keyboard access and mobile layout.

Bootstrap uncertainty, route-balanced comparisons and cross-seed stability research are not included in this patch; the page makes no such claims. No model API calls or raw-corpus edits were needed.
