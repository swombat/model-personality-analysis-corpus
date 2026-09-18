# Model map generation and checks

From `website/`, after generating the published sample bundles:

```sh
python3 scripts/generate_map.py
npm run test:map
npm run build
npm run preview -- --port 4323
```

Generation requires numpy, scipy, scikit-learn and umap-learn. The committed
`src/generated/model-map.json` records their exact versions, generator/input
hashes, repository base revision, seed and feature/projection parameters. A
missing UMAP dependency is an error, not a partial-success fallback. No model
APIs are called. A generation pass can take several minutes on the full corpus.

In a second terminal, use a locally installed Chrome:

```sh
MAP_TEST_URL=http://127.0.0.1:4323/map/ PLAYWRIGHT_CHANNEL=chrome npm run test:map:browser
```

Or install the test runner's bundled browser once with
`npx playwright install chromium`, then omit `PLAYWRIGHT_CHANNEL`.
The same suite can check the deployed map with `MAP_TEST_URL` set to its URL.
It creates isolated browser pages; it does not control the user's normal tabs.

The numerical suite recomputes every shipped per-model/global fidelity score,
checks cosine-neighbour rankings, verifies provenance against sample bundles,
and checks the tree's leaf coverage and merge-height ordering. The browser
suite checks rendering, actual pointer-driven camera preservation, equal axis
units in all six modes, hidden selections/reveal, keyboard tree selection and
mobile controls/layout. CDN access is needed for the live plotting libraries.

## Stability between releases (added 2026-09-18)

`generate_map.py` reads the previous `src/generated/model-map.json` before overwriting it, seeds UMAP from
its coordinates, and Procrustes-aligns every projection to it (`generated_from.alignment` records the
reference revision, common-model count and per-projection disparity). Leave-one-out check on 2026-09-18
(Union Alpha removed, other 153 models compared to the full map): median shift as % of map width —
PCA 0.2 / 0.6, MDS 0.9 / 3.1, UMAP 7.3 / 7.4 (2D / 3D); on-map 3-NN kept — PCA 96 / 92 %, MDS 71 / 90 %,
UMAP 71 / 71 %. Without alignment the same test gave MDS 17 / 38 % and UMAP 20 / 22 % shifts.
To reset the frame deliberately (e.g. after a method change), delete the JSON before regenerating.
