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
