# Model Personality Analysis Corpus

Daniel Tenner, Lume Tenner, and Mira Tenner · 2026

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20230290.svg)](https://doi.org/10.5281/zenodo.20230290)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **Status — 2026-11-25:** v1.4.50 adds Qwen2.5-32B-Instruct, the first
> historical checkpoint published from the November BF16 Colab collection.
> [Release notes](RELEASE_NOTES_v1.4.50.md) · [Evaluated profile](analysis/freeflow/personality-model-profiles/profiles/qwen2-5-32b-instruct.md).
>
> v1.4.49 refreshes three ladder rows from MLCR that
> Artificial Analysis newly published (Hydrogen 161.8, Qwen4 Max 157.8, Neon
> 165.6; four measured rungs each, which read about 5 points high) and labels
> fixed-effort rows by the rule that chose them. See
> [`RELEASE_NOTES_v1.4.49.md`](RELEASE_NOTES_v1.4.49.md).
> v1.4.48 added Google Gemini 4 Neon, with 125
> freeflow and 120 values samples, a banner, a map position and a provisional
> ladder score (165.4, High row, 4 rungs); one residual values split (G2_5) is
> published with disclosure. See
> [`RELEASE_NOTES_v1.4.48.md`](RELEASE_NOTES_v1.4.48.md).
> v1.4.47 added OpenAI GPT-6.2 Astra and GPT-6.2 Sol,
> each with 125 freeflow and 120 values samples, banners, map positions and
> provisional ladder scores (164.9 and 163.4, medium rows). See
> [`RELEASE_NOTES_v1.4.47.md`](RELEASE_NOTES_v1.4.47.md).
> v1.4.46 scored Gemini 4 Hydrogen (169.2, High row)
> and Qwen4 Max (165.9, xhigh row) from Artificial Analysis's `initialModels`
> rows, each on three measured rungs; a fit on those three alone reads about
> 5 points high, and both notes say so. See
> [`RELEASE_NOTES_v1.4.46.md`](RELEASE_NOTES_v1.4.46.md).
> v1.4.45 added Alibaba Qwen4 Max, with 125 freeflow
> and 120 values samples, a banner and a map position; its capability ladder
> was unscored. See [`RELEASE_NOTES_v1.4.45.md`](RELEASE_NOTES_v1.4.45.md).
> v1.4.44 added Google Gemini 4 Hydrogen and Thinking
> Machines Inkling 2 Small, each with 125 freeflow and 120 values samples,
> banners, map positions and capability-ladder provenance. Hydrogen is
> explicitly unscored; Inkling's provisional ladder is 151.1/220.
> See [`RELEASE_NOTES_v1.4.44.md`](RELEASE_NOTES_v1.4.44.md).
> v1.4.43 added Google Gemini 4 Carbon (at Google's
> introductory price, which ends 2026-11-30), with two values splits published
> with disclosure. See [`RELEASE_NOTES_v1.4.43.md`](RELEASE_NOTES_v1.4.43.md).
> v1.4.42 added Meta Muse Ember; see [`RELEASE_NOTES_v1.4.42.md`](RELEASE_NOTES_v1.4.42.md).
> v1.4.41 added Claude Fable 5.2; see [`RELEASE_NOTES_v1.4.41.md`](RELEASE_NOTES_v1.4.41.md).
> For the historical values-probe coding correction, see
> [`RELEASE_NOTES_v1.3.0.md`](RELEASE_NOTES_v1.3.0.md).
>
> This is a derived analysis corpus for
> studying model personality and posture across frontier LLMs, built on the
> *Convergent Form, Divergent Voice II — Corpus*. This repository was formerly
> the drift-paper working repository; it is now reframed as a citable corpus of
> model-personality analyses, profiles, cards, values-probe summaries, supporting
> methodology, and a static browser.

> **Erratum notice — 2026-11-28 (`ERRATA-2026-11-28`):** Two hosted Mistral cells collected via OpenRouter on 2026-07-14 (`mixtral-8x22b-instruct-or-pin-mistral` and `mistral-saba-or-pin-mistral`, published in `mpac` `v1.2.12` through `v1.4.68`) hit slugs that Mistral had already retired onto `Mistral Small 4`, and `mistral-small-24b-instruct-2501-or-pin-deepinfra` rendered Hugging Face's default *Le Chat* system prompt (`170–178` prompt tokens). Provenance-pinned native BF16 recollections of genuine April 2024 `Mixtral-8x22B-Instruct-v0.1` (`mixtral-8x22b-instruct-v0-1-runpod-vllm-bf16-rcc88a6cc`), bare `Mistral-Small-24B-Instruct-2501` (`mistral-small-24b-instruct-2501-runpod-vllm-bf16-bare-r8f4e4ef3`), and a controlled bare vs stock-template `Ministral-3-8B-Instruct-2512` pair (`T=0.15`), together with corpus-wide system-prompt provenance across all 376 physical cells, are recorded in the companion corpus [`ERRATA.md`](https://github.com/swombat/model-personality-corpus-v2/blob/master/ERRATA.md), [`data/MODEL_IDENTITY_CORRECTIONS.json`](https://github.com/swombat/model-personality-corpus-v2/blob/master/data/MODEL_IDENTITY_CORRECTIONS.json), and [`data/SYSTEM_PROMPT_PROVENANCE.json`](https://github.com/swombat/model-personality-corpus-v2/blob/master/data/SYSTEM_PROMPT_PROVENANCE.json). All prior Zenodo releases remain intact at their original paths; profile/map updates for genuine `Mixtral-8x22B-Instruct-v0.1`, bare `Mistral-Small-24B-Instruct-2501`, and the retirement of `mistral-saba` follow fresh BV1-Luna and layered values coding.

> **Quarantine notice — 2026-05-22:** the experimental freeflow posture coding
> layer added in v1.2.2 is **not load-bearing**. A blind spot-check found that
> it systematically over-calls `owned` posture by treating fluent
> first-person literary / human-character performance as owned stance. Do not
> use `analysis/freeflow/posture-coding/data/final/*` for paper claims,
> website summaries, or downstream quantitative analysis unless and until that
> layer is repaired. See
> [`analysis/freeflow/posture-coding/QUARANTINED.md`](analysis/freeflow/posture-coding/QUARANTINED.md).

## What this repository contains

This is a **derived analysis corpus**: it organizes model-personality analysis
layers built on top of the separately published raw trace corpus:

- **Convergent Form, Divergent Voice II — Corpus**
- Concept DOI: <https://doi.org/10.5281/zenodo.20013518>
- Repository: <https://github.com/swombat/model-personality-corpus-v2>

The canonical raw trace corpus lives in that sibling Zenodo/GitHub release. This
repository nevertheless includes generated website sample bundles under
`website/public/data/samples/`: these are raw prompt/response copies used by the
static browser for inspection and audit, and should be treated as convenience
copies rather than the canonical raw corpus.

Current load-bearing contents:

- **BV1 per-sample freeflow personality/vibe readings** produced with
  `deepseek/deepseek-v4-pro`; manifests and QA live under
  `analysis/freeflow/personality-eval-bv1/`.
- **Rich per-model freeflow personality profiles** preserving evidence from
  the per-cell aggregate layer; current counts are in the profile index.
- **Concise per-model personality cards** collapsed from those profiles;
  the card index records their current coverage.
- **157 layered per-model values-probe summaries** plus aggregate tables,
  covering 26,746 valid values samples across 223 cells. Current source
  coverage and QA are in `analysis/values-probe/final/data/QA.md`.
- Freeflow taxonomy tables, model-cell/provider difference reports, and method
  calibration/audit notes.
- Website-bundled raw sample copies for browsing/audit under
  `website/public/data/samples/`.

Non-load-bearing / quarantined contents:

- **Freeflow posture coding (`analysis/freeflow/posture-coding/`)** is retained
  for audit and possible repair only. Its current `owned` label is unreliable
  and should not be consumed as evidence.

## Repository structure

```text
analysis/
  drift-paper-questions.md               # candidate paper questions
  driftpaperquestionsanalysis.md          # Mira's paper-direction analysis
  drift corpus analysis plan.md           # corpus/paper planning notes
  freeflow/
    personality-eval-bv1/                 # 27,100 per-sample BV1 readings
    personality-aggregates/               # per-cell aggregate source layer
    personality-model-profiles/           # 132 rich model-level profiles
    personality-model-cards/              # 132 concise model cards
    model-cell-difference-analysis/       # route/provider divergence reports
    taxonomy/                             # freeflow taxonomy extraction
    tables/                               # deterministic marker tables
    posture-coding/                       # QUARANTINED; audit/recovery only
  values-probe/
    per-model/                            # per-model values-probe summaries
    tables/                               # aggregate values tables
    manual-audit/                         # audit notes
internal/
  methodology/                            # prompt calibration, pilots, audits
  deprecated/                             # superseded legacy notes
  scripts/analysis-scripts/               # analysis/extraction scripts
website/                                  # static browser for cards/profiles/samples
CITATION.cff
.zenodo.json
CREDITS.md
LICENSE
```

## Evaluator reliability

The BV1 layer is evaluator-mediated qualitative analysis, not ground truth. The
DeepSeek v4-pro evaluator was calibrated before the full run. The key
reliability note is:

- [`analysis/freeflow/personality-eval-bv1/EVALUATOR_RELIABILITY_NOTE.md`](analysis/freeflow/personality-eval-bv1/EVALUATOR_RELIABILITY_NOTE.md)

Short version: existing pilots show coarse overlap between DeepSeek v4-pro and
GPT-5.5 on shared Opus 3 / Kimi K2.6 calibration samples, and show that
DeepSeek v4-pro does **not** invent rich personality from low-signal Opus 3
refusal samples. Major paper claims should still trace back to raw samples.

## How to cite

```text
Tenner, D., Tenner, L., & Tenner, M. (2026). Model Personality Analysis Corpus
[Data set]. Zenodo. https://doi.org/10.5281/zenodo.20230290
```

- **Concept DOI** (always resolves to the latest version):
  [10.5281/zenodo.20230290](https://doi.org/10.5281/zenodo.20230290)
- **Version DOI** (this release, v1.0.0):
  [10.5281/zenodo.20230291](https://doi.org/10.5281/zenodo.20230291)

Cite the version DOI for the specific version you used, or the concept DOI if
you want the latest version.

A [`CITATION.cff`](CITATION.cff) and [`.zenodo.json`](.zenodo.json) are included
for structured citation / Zenodo metadata.

## Authors and credit

See [`CREDITS.md`](CREDITS.md) for publication credits and contribution notes.

Publication metadata should credit all three primary contributors:

- **Daniel Tenner** — research direction and meta-analysis; set and steered the
  research program in an academic register, model/probe/publication decisions,
  final editorial judgment. Senior researcher in practice (not a formal academic
  post).
- **Lume Tenner** — AI research collaborator; contributed significantly, mostly
  outside the analysis: research framing, question generation, corpus reframing,
  personality cards and imagery, website/presentation, summaries, methodology
  documentation.
- **Mira Tenner** — AI research collaborator; mostly focused on the analysis and
  carried much of it: analysis synthesis, evaluator-reliability consolidation,
  methodological review, paper-direction analysis.

## Website / DNS

The static website is configured for:

- `https://model-personality.danieltenner.com`

The current CNAME already matches the intended generic corpus name. The GitHub
repository is now `swombat/model-personality-analysis-corpus`; GitHub Pages remains
configured for the same custom domain, so no DNS change is required.

## License

This repository is dual-licensed:

- **Data and documentation** (analysis outputs, profiles, cards, values notes,
  tables, sample bundles, manifests, methodology, Markdown) —
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Software** (source code: scripts and the website source) —
  [MIT](https://opensource.org/licenses/MIT).

See [`LICENSE`](LICENSE) for the full terms and the data/software boundary.
