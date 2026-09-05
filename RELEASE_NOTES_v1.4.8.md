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
- **Coverage: 113 of 151 site models scored, 38 not yet scored.** The 38
  are models with no exact/snapshot/family alias to an Epoch entry —
  mostly small unreleased-benchmark open-weight models (Qwen 1.5/2 7B,
  ChatGLM2/3, GLM-4-9B), OpenAI's codex-suffixed variants, several
  Mistral/Ministral SKUs, the two stealth Ox Alpha probes, and a few very
  recent releases (GPT-5.3, Kimi K2-0905, both Grok 4.1 Fast variants).
  Unscored models render "not scored" (muted) instead of a number and
  sort last on the intelligence sort.
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
- Build verified clean (`npm run build`, 341 pages) with no remaining
  `aaii` or "Artificial Analysis Intelligence" references anywhere in the
  generated site.
