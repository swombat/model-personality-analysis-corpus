# Release notes — v1.4.6

Prepared 2026-09-03.

## Site: Muse Spark Contributor tiers folded into their parent pages (6 → 4 Muse pages)

v1.4.5 published every Muse cell as its own page. The corpus's own rule is
that a **cell is a route and a page is a model** (glm-4.7 has twelve
provider cells under one page; the route-difference layer decides). The
Contributor tiers are routes — same snapshot, different price and data
terms — so this release runs them through that machinery:

- **Route-difference judge** (`analyze_model_cell_difference.py`, gpt-5.4):
  `NO_STRONG_DIVERGENCE` for both `muse-spark-1-2` (standard vs
  Contributor) and `muse-spark-1-3`. Reports and audit packets under
  `analysis/freeflow/model-cell-difference-analysis/`. The judge's
  model-level card replaces the single-cell cards, per the pipeline.
- **Profiles and cards** rebuilt for the two merged models (250 freeflow
  samples each: 231/19 and 242/8 expressive/essay). The
  `muse-spark-1-2-contributor` and `muse-spark-1-3-contributor` cards,
  profiles and index rows are removed.
- **Values probe**: `assemble_final_values_probe.py` gains a
  `MODEL_ALIASES` map applied at assembly time (phase-32 source files
  untouched; `cell` preserved). Final reports now read 240 samples across
  2 cells; all-condition ownership 83.3%/88.3% (1.2 std/contrib) and
  63.3%/68.3% (1.3) per Mira's family report; G1/G2 disclosure 128/160
  and 81/160 on the merged pages.
- **Site**: the two contributor pages are gone; their sample bundles fold
  into the parent pages (490 published samples each); OpenRouter route,
  pricing, AAII and release date are the standard tier's. Straplines and
  banners for 1.2 and 1.3 are unchanged — both were drawn from the standard
  cells and the Contributor cells share the vocabulary. The two Contributor
  banners are kept in `internal/model-card-images/retired/`.
- **Provenance note** on each merged page (`model-notes.json`): what is
  *stated* (1.2 — Meta, 21 Aug 2026: "Same model") vs *inferred* (1.3 —
  Meta's announcement does not mention the tier), and why the second cell
  is kept: it is the serving-time wrapper test Ox Alpha taught us to want
  (a system prompt alone moved ownership 23→58/60 there); here the routes
  are indistinguishable on every probe, with the caveat that the probes
  don't exercise tool use, refusals or code.

## Pipeline notes (for whoever rebuilds next)

- `canonical()` in the three freeflow scripts now strips a bare `meta/`
  prefix (Muse is the first such source) and folds
  `muse-spark-1.x-contributor` into `muse-spark-1-x`. The difference script
  also gains the `stealth/` mapping its two siblings already had — without
  it, a full run pairs the two Ox Alpha snapshots into a spurious
  `stealth-ox-alpha` group (one such judge call was made and discarded).
  The three copies of `canonical()` have drifted; unifying them is
  overdue.
- **`build_personality_model_cards.py` and `build_personality_model_profiles.py`
  delete and regenerate their whole output directory.** A full run this
  release reverted hand-curated content that the generator does not know
  about: the values paragraph appended to `claude-fable-5-1`'s card, the
  hand-rewritten and dash-named `glm-5-3` / `glm-5-3-flash` cards and
  profiles (the script spells them `glm-5.3`), and a manual fix in the
  `gemini-3.8-flash` profile. All were restored from HEAD and the
  index/README rows merged by hand; only the Muse rows changed. Until the
  curated files are either fed back into the generator or protected, a
  full rebuild will do this again.
- `analysis/values-probe/final/data/*.jsonl` are regenerated wholesale by
  the assembler; the only content change is the two aliased model keys.
