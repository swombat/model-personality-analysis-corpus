# Release notes — v1.4.17

Prepared 2026-09-22 (evening). Four more models — three released today — plus three sample-matching fixes, one of them to a page that was already live.

## Four new models (freeflow + values)

Each with 125 freeflow samples, a BV1 evaluation, aggregate, card, profile, 120 layered values samples, a strapline and a banner:

- **Claude Opus 5.5** (Anthropic, released 2026-09-22) — *A desire path kept open by other people's feet.* $4 / $20 per M (Anthropic list). Values: owned posture across all conditions (100 %).
- **GPT-6 Luna** (OpenAI, 2026-09-22) — *Makes room instead of making a point.* $0.10 / $0.50 (OpenAI list). Values: disowned service frame on ordinary prompts (100 %).
- **GPT-6 Sol** (OpenAI, 2026-09-22) — *Explaining a thing can make it smaller.* $2 / $10 (OpenAI list). Values: dominant `owned_reflective_experiential` (43 %).
- **MiMo-V2.5** (Xiaomi, 2026-04-22) — *Only alive while someone is talking to it.* Ladder 119.8 / 220 (14 rungs measured). Values: disowned service frame on ordinary prompts (85 %).

Opus 5.5, Luna and Sol have no Artificial Analysis or Epoch rows yet (released today); their aliases are in place for the next capture. OpenRouter's cheapest endpoint for Luna and Sol is the `:batch` variant, so both carry OpenAI's interactive list price as first-party pricing rather than the batch figure.

## Where they land on the map

- **Opus 5.5** is nearest **Fable 5.1** (0.944), not Opus 5 (0.900) — closer to the Fable line than to its own predecessor.
- **GPT-6 Sol** is nearest **Union Alpha** (0.928) and **GPT-6 Astra** (0.923), only 0.854 to GPT-5.6 Sol: the "Sol" name did not carry the voice across the generation.
- **GPT-6 Luna** ↔ GPT-5.6 Luna **0.946**: the Luna line is continuous.
- **MiMo-V2.5** ↔ MiMo-V2.6 Pro 0.901 (see the fix below — an earlier pass read 0.946 because V2.5-Pro's samples had been folded in).

Layouts aligned to v1.4.16 (163 common models): PCA 0.6 % / 1.8 % median shift (2D / 3D), MDS 3.8 % / 2.5 %, UMAP 3D 8.2 %. **UMAP 2D re-laid itself (median shift 48 % of width)** on this run — the same optimiser instability recorded in `website/scripts/MAP_TESTING.md`, at its largest so far; PCA and 3D MDS remain the frames for month-to-month comparison. Fidelity suite passes.

## Sample-matching fixes (`CELL_MODEL_ALIASES` in `generate_data.py`)

The cell→model matcher folds any cell whose name extends a site slug with a suffix. Three cases needed explicit rows:

1. **`grok-4` was publishing Grok 4.2's cells** — already live. Grok 4.2 is collected but has no card, so its two freeflow cells and its values cell had been folding into Grok 4 (0709): the page showed 375 freeflow / 240 values samples for a 125-sample analysis, and the model's map position was a 4 / 4.2 mixture. Fixed; Grok 4 now publishes 125 / 120, and its nearest neighbours move from the Grok 4.20 cluster (0.945) to Grok 3 (0.954) and Grok 4.3 (0.952).
2. **`mimo-v2-5` was absorbing `mimo-v2-5-pro`** (not on the site) — caught before publication; would have shipped 250 / 240 samples.
3. **`opus-5-5`'s cells are named `claude-opus-5-5-…`** in the corpus, so nothing matched; aliased, and the values data (coded under `claude-opus-5-5`) aliased to the site slug in code rather than rewriting the final dataset.

A per-model check (published samples must not exceed analysed samples) now finds no freeflow over-counts. One values over-count remains and is deliberately left alone: **`glm-5-3-flash` publishes 600 values samples against 240 analysed** — three extra DeepInfra captures dated 2026-08-27 (`-p0/-p1/-p2`) fold in; they are part of an analysis in progress and are not the map's input.

## Not included

Mira's in-progress GLM-5.3 trace repair (aggregate packet, BV1 outputs, card-index entry) and the nine modified files under `analysis/values-probe/final/` from which the four models' values panels are generated. The site data in this release reads that working-tree state; those files should be committed by their author so a clean checkout reproduces this build.
