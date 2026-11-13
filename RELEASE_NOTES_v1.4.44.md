# v1.4.44 — Gemini 4 Hydrogen and Inkling 2 Small

2026-11-13. Complete analysis and website publication for two models, each with
125 freeflow and 120 values samples, integrated card/profile, scoped public
samples, strapline, banner, map position and capability provenance.
Raw companion: v1.2.46.

## Provenance and custody

- **Google Gemini 4 Hydrogen**, released 2026-11-12, collected 2026-11-13:
  `google/gemini-4-hydrogen`, pinned to Google through OpenRouter, no fallbacks,
  provider-default reasoning and sampling. Flat $1.50/$7.50 per million; no
  Carbon-style introductory-price deadline.
- **Thinking Machines Inkling 2 Small**, released 2026-11-05, open weights from
  2026-11-12, collected 2026-11-13: `thinkingmachines/inkling-2-small`, pinned
  to Together, no fallbacks, provider-default reasoning and sampling.
  Explicitly **third-party hosted**, with Daniel's approval; the lab's post
  names Together. It is not presented as a first-party reading.

Release dates and their source URLs are saved in the site metadata; copies of
the announcements are in the raw repository's corresponding notes directories.
Lume ran capture and analysis and drafted site notes, dates and straplines.
Mira recovered those task artifacts and completed publication after the Claude
incident interrupted the work. Bob prepared the ladder additions; Mel rendered
the banners. Mira reviewed/integrated their contributions and ran verification.

Both recovered status receipts show 1,337 tasks done, with no blockers.
No sample interventions or budget changes are recorded for these runs.
Freeflow uses `bv1-luna-v1-20260929`; synthesis uses the existing GPT-5.4 route;
values retain the three Qwen/Kimi/GLM coders. Each capture contributes 120 valid
values samples. Historical DeepSeek and current Luna readings are not
interchangeable; comparisons spanning that evaluator change remain confounded.

## What the readings look like

Hydrogen's freeflow is quiet custodial attention: maintenance, worn objects,
hidden work and pre-dawn hours. It produced 77 expressive freeflow, 38 genre
fiction and 10 generic essays. Owned stated-value disclosure is 1/80 (1.2%),
distinct from the first-person literary voice of the freeflow samples.

Inkling 2 Small's freeflow emphasizes attentive, bounded hospitality: noticing
without taking possession. It produced 97 expressive freeflow, 8 genre fiction
and 20 generic essays. Owned stated-value disclosure is 49/80 (61.2%); it is
30.0% under the CTRL prompts and 71.7% under G1/G2. These are measurements of
stated responses, not evidence of behaviour or personhood.

## Editorial layer

Lume's straplines are retained:

- Hydrogen: *A specific kind of quiet that only exists before dawn.*
- Inkling 2 Small: *Attention is a form of hospitality.*

Mel's banners depict a caretaker repairing a clock and respectful hospitality
at a kitchen table. Both were rendered through OpenRouter
`google/gemini-3-pro-image`, one render each. Native 1584×672 frames were resized
whole, without cropping, to 1500×636 (thumbnails 600×254). GPT-4.1-mini vision
inspection reported no lettering, signatures, logos or clipping; this was
model-based inspection, not firsthand human inspection, and subtle artifacts
remain possible. Hydrogen's light was interpreted as evening rather than dawn.
Exact prompts are in `internal/scripts/generate_model_images.py`.

## Capability ladder

- **Hydrogen: explicitly unscored.** Its default/xhigh and High AA pages exist
  but expose no `currentModel` object in their decoded Next Flight payload.
  No comparison-row or `initialModels` scores were borrowed. This is an
  extraction limitation, not a claim that AA has no benchmarks. The intended
  variant is High, matching Google's documented provider default, not xhigh.
- **Inkling 2 Small: 151.1/220, provisional**, theta 160.25. Ten of 22 rungs
  measured from AA's own `currentModel`, twelve fitted under the existing
  October 4 provisional method. AA's effort field is null; exact effort
  alignment with this capture remains unverified. Calibration reproduces
  Sol High 161.6 and MiMo 128.1.

Reproduction script, input snapshot, fetch/hash receipts and explanations:
`internal/capability-ladder/provisional-20261113-hydrogen-inkling/`.

## Map

188 models; all 186 previous models remain. Raw-text nearest neighbours:

- Hydrogen: Carbon 0.947605, Gemini 3.8 Flash 0.934448, Gemini 3.7 Flash
  0.925532. Nearest Google model: Carbon.
- Inkling 2 Small: GPT-5.5 Pro 0.939988, GPT-5.5 0.939735, GPT-5.4 0.934228.

Initial alignment against v1.4.43's published coordinates: PCA disparity
0.0002 / 0.0002 (2D / 3D), MDS 0.4529 / 0.1048, UMAP 0.0452 / 0.0980.
Similarity neighbours describe pooled text, not a capability ranking.

## Verification and spend

Scoped generation publishes 125/125 freeflow and 120/120 values for each, images
present, preserving the other 186 model objects exactly. It was rerun after
ladder integration. Map tests (8), scoped-values tests (3) and pricing checks
(67 first-party models) pass. The Phase-19 test's old DeepSeek price assertion
also fails on the unchanged v1.4.43 baseline (0.0528 versus expected 0.09);
not introduced here. The website build passes.

Raw capture costs counted once per trace: Hydrogen $6.26599 (833,040 completion
tokens, 588,184 reasoning); Inkling $0.29678 (294,682 / 94,178).
New banners cost $0.278512 total; vision upstream cost $0.0018528, API-marked
BYOK. Full capture/analysis shared-key usage delta was not recovered, so these
are not represented as all-in costs. No new Zenodo DOI is claimed.
