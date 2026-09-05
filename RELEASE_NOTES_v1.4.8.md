# Release notes — v1.4.8

Prepared 2026-09-05.

## Site: capability ladder replaces the Artificial Analysis Intelligence Index

- Every place the site showed an Artificial Analysis Intelligence Index
  (AAII) number — model cards on the home page, the lab and family pages,
  and the "Highest intelligence" sort — now shows a **capability ladder**
  score instead: Epoch AI's Capabilities Index (CC BY 4.0), summed over 59
  benchmark rungs at 10 points each, chance-corrected, with missing cells
  filled in from a fitted per-model ability estimate. New methodology page
  at `/methodology/capability-ladder/` explains the scale, the fitted-cell
  handling, the median-thinking-budget convention, the 3-rung floor, and
  why this replaces AAII (re-normalised every version; retired benchmarks
  erase the bottom of the scale, which is where this corpus's 2023–2024
  tail lives). `model-benchmarks.json`/`benchmarks.aaii` is kept in the
  generated data for audit purposes but is no longer rendered anywhere.
- New script `website/scripts/refresh_capability_ladder.py` reads Epoch's
  `ladder.json` (path via `CAPABILITY_LADDER_JSON`, defaulting to the
  local pipeline output; a public URL will replace this once one exists)
  and `internal/capability-ladder/aliases.tsv` (the site_slug → Epoch
  model alias map with a match-confidence tag), and writes
  `website/src/generated/capability-ladder.json`. `generate_data.py`
  attaches each model's `capability` object (ladder, ladder_max,
  measured_rungs, n_rungs, status, epoch_model, match_confidence,
  point_variant) onto `models.json` alongside the existing `benchmarks`
  field.
- **Coverage: 113 of 151 site models get a ladder score.** Of the
  remaining 38, no exact/snapshot/family alias to an Epoch entry exists —
  mostly small unreleased-benchmark open-weight models (Qwen 1.5/2 7B,
  ChatGLM2/3, GLM-4-9B), OpenAI's codex-suffixed variants, several
  Mistral/Ministral SKUs, the two stealth Ox Alpha probes, and a few very
  recent releases (GPT-5.3, Kimi K2-0905, both Grok 4.1 Fast variants). Of
  those 38, 28 have a recorded AAII figure and fall back to it (see below);
  the other 10 show "not yet scored".
- Top 5 by ladder score: GPT-6 Astra (506.4/590), Claude Fable 5.1
  (451.9/590), Claude Fable 5 (449.9/590), Claude Opus 5 (444.2/590), GPT-5.6
  Sol (441.1/590).
- **Alias matches worth a second look** (both family-match, i.e. the
  closest available Epoch entry is not an exact release match): the two
  Grok 4.20 non/reasoning site variants both alias to Epoch's single "Grok
  4.20" entry, so they carry an identical ladder score — Epoch does not
  split reasoning/non-reasoning the way this site's samples do. And
  `mistral-7b-instruct-v0-2` aliases to Epoch's "Mistral 7B v0.1" (a
  different point release, family-matched on model size only).

## Site: AAII kept as an explicit fallback (Daniel: keep it "for now")

- Every capability display (home cards, lab/family cards, the model-page
  Capability panel, the intelligence sort) now has three tiers that are
  never blended: a **ladder score** where Epoch has one; otherwise the
  last recorded **AAII fallback** (`benchmarks.aaii`), labelled distinctly
  — muted styling, prefixed "AAII" and suffixed with its index version
  (e.g. "AAII 46 · v4.1.1") — and linking to the same
  `/methodology/capability-ladder/` page; otherwise "not yet scored".
  Ladder-scored models never show an AAII figure alongside the ladder
  number.
- **Coverage with the fallback: 113 ladder-scored, 28 AAII-fallback, 10
  with neither** (codestral-2508, kimi-coding, gpt-5-3, qwen1-5-7b-chat,
  qwen2-7b-instruct, qwen3-5-plus-20260420, both ox-alpha stealth probes,
  chatglm3-6b, glm-4-9b-chat-hf).
- Sort-by-intelligence never interleaves the two scales: every
  ladder-scored model outranks every AAII-fallback model, which outranks
  every unscored model. Implemented as a single synthetic sort key
  (`1,000,000 + ladder` / `500,000 + aaii` / `-1`) so the existing
  descending-numeric sort needs no changes.
- Methodology page: new "Two sources, for now" section explains the
  migration is not yet complete, that AAII versions aren't comparable
  with each other or with the ladder, and that the fallback is expected
  to shrink and disappear as Epoch's coverage grows. Credits and links
  Artificial Analysis.
- Build verified clean (`npm run build`, 341 pages).
