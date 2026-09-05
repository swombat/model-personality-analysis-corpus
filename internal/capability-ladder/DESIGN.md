# Capability ladder — design note

Drafted 2026-09-05 by Lume, from Daniel's proposal the same morning. Status:
design, pre-data. The three `raw/*/REPORT.md` files say what data actually
exists; this note is what to do with it.

## The problem

The site carries one capability number per model (AAII) so readers can place
a personality against rough cognitive power. Two things broke on 2026-09-04:

1. AAII v4.2 re-scored the frontier on a new evaluation set. Scores are not
   comparable across versions, and our column was mixed — which produced
   the "Muse Spark above Astra" artefact.
2. Worse for us: each AA version *drops* the benchmarks the frontier has
   saturated (MMLU-Pro, GPQA Diamond…). Those are the only benchmarks on
   which GPT-3.5 Turbo (4), GPT-4 (7), GPT-4 Turbo (8), GPT-4o (11) were
   ever distinguishable. A 0–100 index that is re-normalised to the current
   frontier necessarily erases the bottom of the scale. The models we care
   about *include* the bottom of the scale.

AA's constraints (0–100, one fixed set for every model, comparable to last
quarter) are exactly what make it unfit as a longitudinal ruler. We do not
share those constraints.

## Daniel's proposal (restated)

A cumulative, open-ended ladder. Every benchmark is a rung worth a fixed
number of points (say 10) times the model's fractional score. When the
frontier saturates a rung, a new rung is added; the old rung's points stay.
A model that was never run on a rung that was already saturated when the
model was released is credited as if it had saturated it. The scale grows
without bound; that is a feature. GPT-5 might sit at 70, GPT-6 at 95, and
GPT-3.5 stays at ~5 forever, still on the same ruler.

## What I would keep, and the one thing I would change

Keep: cumulative, open-ended, fixed points per rung, points never removed,
computed entirely from published numbers, every cell tagged with its
provenance. The display metric should be the sum-of-rungs Daniel described —
it is transparent and a reader can recompute it by hand.

Change: the "not run → assume saturated" rule. It is right in spirit and
wrong at the edges, and the edges are where the interesting models sit:

- It has a *direction*. A model released after a benchmark saturated and
  never run on it → credit. A model released before a benchmark *existed*
  and never run on it → no credit. A model that was live while the
  benchmark was live but AA simply didn't run it → genuinely missing.
  Three different absences, one rule.
- Multiple-choice benchmarks have a chance floor (MMLU 25%, GPQA Diamond
  25%, MMLU-Pro 10%). A model at chance is not 2.5 points capable; it is
  zero. Every fractional score must be chance-corrected first:
  `(s − c) / (1 − c)`, clipped at 0.
- "Assume 100%" over-credits: benchmarks are retired when the *frontier*
  hits ~90%, not 100%.

The clean replacement is the thing Daniel's rule is a hand-rolled version
of: an **item-response model**. Each benchmark j has a difficulty b_j and a
discrimination a_j; each model i has one latent ability θ_i; the expected
chance-corrected score on any rung is σ(a_j (θ_i − b_j)). Fit θ, a, b by
least squares on every cell we *have*. Then:

- A cell we have is used as measured.
- A cell we lack is *derived* from the model's ability and the rung's
  difficulty — which is precisely "old easy rung → near full credit, new
  hard rung → near zero" as a continuous function instead of a threshold,
  and it handles the ambiguous middle absence without a special case.
- No replacement bookkeeping. Rungs are never "replaced"; new ones appear
  when benchmarks appear, old ones keep contributing. Saturation is a
  *report* (this rung no longer discriminates at the top), not a mechanism.
- The ladder score stays Daniel's sum: `L_i = Σ_j 10 · ŝ_ij`, where ŝ_ij is
  the measured chance-corrected score if we have it, else the fitted one.
  Every term is tagged `measured` / `fitted`, and the site can show the
  measured fraction ("62 of 80 points measured").

θ itself is a perfectly good scale too (it is what the ladder is estimating),
but it is unbounded, unitless and re-fits every time data is added. The
sum-of-rungs is what to publish; θ is what makes the missing cells honest.

## Open design choices (decide after seeing the data)

1. **Equal points per rung** makes the scale "how many generations of
   yardstick has this model mastered". Eras with many benchmarks (2025)
   then count for more than eras with few (2023). Alternative: group rungs
   into capability families (knowledge, maths, code, reasoning, agentic,
   long-context) and weight so each family's chain sums the same. Test
   equal-rungs first against the anchors GPT-3.5 ≈ 4 : GPT-4 ≈ 7 : GPT-4o ≈
   11 : GPT-4.1 ≈ 20 — the *ratios* are the calibration, not the numbers.
2. **Redundant rungs** (MATH-500 and AIME-24 measure one skill; two AIME
   years). IRT absorbs correlation partly; a family grouping absorbs it
   fully. Decide by looking at which rungs move together.
3. **Which variant** of a model: AA scores max-reasoning. Our personality
   samples are default-effort. Use max for the capability number (it is
   what "this model can do" means) and say so on the methodology page.
4. **Source precedence** when a cell exists in more than one place: AA's
   own run > Epoch's run > developer-reported. Developer-reported numbers
   are contamination-prone and self-selected; keep them as a last-resort
   tier and tag them.
5. **Exclusions:** Elo-style items (Arena) are not fixed tests — exclude.
   Private-test-set items (AA-Briefcase, GDPval-AA, Omniscience) are
   AA-only and unverifiable; include, tagged `private`, or exclude — the
   ladder works either way, so decide on principle (I lean include-tagged:
   they are the only rungs that separate the current top three).
6. **Saturation report rule** for the methodology page: a rung is
   saturated when the best chance-corrected score has been ≥ 0.90 for two
   consecutive quarters. Cross-check against AA's removal history; they
   should agree, and where they don't is worth a sentence.

## What "no benchmarks run by us" costs

Nothing we can't state. The ladder is a function of published tables plus a
committed script; anyone can rerun it. What it cannot do is score a model
nobody has evaluated (the 2023 6B–7B tail: Yi-6B, ChatGLM2, Qwen2-7B). For
those the honest cell is blank, with whatever developer-reported MMLU
exists shown as a single tagged rung. A blank is better than a fitted θ
from zero items.

## Files

- `raw/aa/` — Artificial Analysis per-benchmark table (API), see REPORT.md
- `raw/epoch/` — Epoch AI benchmarking hub CSVs, see REPORT.md
- `raw/timeline/` — benchmark lifecycle table + AAII version history
- `ladder.py` — (to write) normalise → chance-correct → fit → sum → tag
- `ladder.tsv` — (output) one row per model: ladder score, measured points,
  fitted points, θ, per-rung cells with provenance

---

## Results (2026-09-05, same day)

**Found object.** Epoch AI's Capabilities Index (ECI, in the CC-BY
`benchmark_data.zip` bundle) is already the item-response model this note
designs: one ability per model (267 scored, bootstrap CIs), one difficulty
(`edi`) and slope per benchmark (59, from TriviaQA at 57 to CL-bench at
183), chance baselines and ceilings in `benchmark_metadata.csv`, anchored
Claude 3.5 Sonnet = 130 and GPT-5 = 150. Functional form verified on all
2,842 processed cells: `performance ≈ σ(slope·(eci − edi))`, RMSE 0.073.
`ladder.py` computes Daniel's sum-of-rungs on top of it.

**Curated 15 rungs, max 150** (ordered by Epoch difficulty): MMLU, GSM8K,
HellaSwag, MATH L5, GPQA Diamond, SWE-bench Verified, OTIS Mock AIME, Aider
Polyglot, Terminal-Bench, FrontierMath T1–3, HLE, ARC-AGI-2, CritPt,
GDPval, Remote Labor Index.

| model | ladder | CI | measured rungs |
|---|---|---|---|
| ChatGLM2-6B | 11.5 | 10.8–12.2 | 3 |
| Llama 3.2 1B | 15.2 | 9–23 | 2 |
| GPT-3.5 Turbo (Jun '23) | 22.5 | 20–25 | 2 |
| Claude 3 Haiku | 28.5 | 25–30 | 4 |
| GPT-4 (Mar '23) | 37.9 | 34–42 | 5 |
| GPT-4o | 41.8 | 39–44 | 4 |
| GPT-4.1 | 58.9 | 58–60 | 8 |
| o3 | 81.8 | 81–83 | 10 |
| GPT-5 | 90.5 | — (anchor) | 12 |
| Opus 4.8 | 112.1 | 110–114 | 6 |
| GPT-5.6 Sol | 120.4 | 118–123 | 5 |
| Fable 5.1 | 121.5 | 119–125 | 4 |
| GPT-6 Astra | 131.1 | 125–137 | 3 |

**Site join** (`site_ladder.tsv`, via `aliases.tsv`): 113/151 from Epoch,
27 provisional from AA's live per-benchmark row (θ estimated after
calibrating AA's items on the 107-model overlap — AA's GPQA fits at
difficulty 135 vs Epoch's 135.8, HLE 160 vs 160.0, CritPt 169 vs 167: two
independent evaluators, same ruler), 11 blank (stealth Ox Alpha, Qwen
1.5/2 7B, ChatGLM3, GLM-4-9B, Codestral 2508, GPT-5.3 non-codex which
neither index lists, Mistral Saba with <3 cells).

**Agreement with AAII.** Spearman 0.956 vs the site's v4.1.1 column over
125 models. The ordering AA and Epoch agree on survives; what changes is
the bottom (no longer collapsed to 1–7) and the top (open-ended). Largest
disagreements, all explainable: (a) *variant collapse* — Epoch has one
"Grok 4.20" where AA/we have reasoning and non-reasoning (23 vs 37); the
ladder cannot split what Epoch doesn't; (b) *AA low-effort or stale rows*
— Opus 4.6 (AAII 39, ladder 106), Gemini 3 Flash Preview (28 vs 96); (c)
*genuine evaluator disagreement* on private-set-heavy models — GLM-5.3
(60 vs 106), MiniMax M3 (45 vs 83), and Astra vs Fable 5.1 (AA: 55 < 57;
Epoch: 169 > 163).

**What the ladder costs.** Old models' rungs are mostly fitted, not
measured (GPT-3.5: 2 of 15). That is the design, but the site must show
it. Epoch lags releases by days–weeks, so the provisional path is needed
for release-day publishing. AA data is keyless but scraped from page
payloads (`raw/aa/parse_flight.py`) — brittle; Epoch's ZIP is the stable
source. `raw/` holds ~50 MB of HTML/ZIP — gitignore the HTML, keep the
TSVs.

**Sources.** Epoch AI, "AI Benchmarking Hub" (CC-BY 4.0);
Artificial Analysis model pages (live) and Wayback snapshots 2024-01 →
2026-07 (retired rungs: MMLU, HumanEval, MATH-500, MMLU-Pro, AIME, Arena
Elo — merge in `raw/aa/aa_history*.tsv`).
