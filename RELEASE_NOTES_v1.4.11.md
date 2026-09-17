# Release notes — v1.4.11

Prepared 2026-09-17.

## Site: the model map (`/map/`)

- New page **Map** (nav link added): every published model placed by prose
  similarity. Character 3–5-gram TF-IDF centroid per model over its freeflow
  samples; cosine similarity between centroids; projected with **UMAP**
  (default), metric **MDS** or **PCA**, in 3D (rotatable) or 2D. Points are
  coloured by lab; stealth models are ringed. Hover/click shows the strapline
  and the three nearest neighbours *in the full space*, with a link to the
  model page.
- Each projection carries its own honesty number in the UI and in the method
  section: the share of each model's 3 nearest full-space neighbours that
  survive on the map. Today: UMAP 2D 59% / 3D 62%; MDS 36% / 50%; PCA 28% /
  38% (27% / 34% of variance). The drawn nearest-neighbour edges (k = 0–6)
  are the claim; the positions are the sketch.
- **Family tree**: average-linkage dendrogram over the full cosine matrix,
  leaves coloured by lab, hover/click wired to the map. Lossless where the
  map is lossy; the best single view of the corpus's structure.
- **Time**: a release-date scrubber hides models released after the cut-off,
  and a *lab trajectories* overlay draws each lab's models in release order —
  a lab's path through style-space.
- Generator: `website/scripts/generate_map.py` → `src/generated/model-map.json`
  (229 KB; committed). Run it after `generate_data.py` on every release.
  Needs `scikit-learn`, `scipy`, `umap-learn`.
- Libraries: plotly 2.31.1 and d3 7.9.0 from cdnjs (the page is static; the
  JSON is inlined at build time).

## Union Alpha: provenance note

- `model-notes.json` entry for `union-alpha`: measured as an anonymous stealth
  route; reported the same day (@aitrackerbot) to be *Pareto*, Circuit &
  Chisel's cascade router with GPT-6 Astra as the escalation model —
  architecture confirmed from the org's public `pareto-evals` repo, naming and
  member list not independently verified. Our per-sample re-cut agrees (88/125
  freeflow and 85/120 values answers nearest Astra; 35 s median for a 66-word
  answer). The page now says to read it as one path through a router under
  this corpus's prompt style, not as a model. Lab stays *Unknown*. Write-up:
  danieltenner.com/union-alpha-appears-to-be-from-openai/ (dated update).
