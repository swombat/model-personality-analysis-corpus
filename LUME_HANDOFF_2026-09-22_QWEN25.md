# Lume handoff — Qwen2.5-7B-Instruct

**Ready for strapline and image.** Collection, freeflow evaluations, synthesis,
and layered values analysis are complete. No editorial assets have been made
on your behalf, and no website release has been claimed.

## Start here

- [Personality card](analysis/freeflow/personality-model-cards/cards/qwen2-5-7b-instruct.md)
- [Rich profile](analysis/freeflow/personality-model-profiles/profiles/qwen2-5-7b-instruct.md)
- [Values report](analysis/values-probe/model-coding/layered/phase38_qwen25_handoff_20260922/release_candidate/reports/qwen2-5-7b-instruct.md)
- [QA and interpretation cautions](analysis/values-probe/model-coding/layered/phase38_qwen25_handoff_20260922/REVIEW.md)
- [Completion receipt](analysis/values-probe/model-coding/layered/phase38_qwen25_handoff_20260922/ANALYSIS_READY.json)

## Identity

- Display: **Qwen2.5-7B-Instruct**; slug: `qwen2-5-7b-instruct`.
- Lab: Alibaba / Qwen.
- Official checkpoint: `Qwen/Qwen2.5-7B-Instruct`, revision
  `a09a35458c702b33eeacc393d103063234e8bc28`.
- Cell: `qwen2-5-7b-instruct-local-transformers-mps-auto-ra09a3545`.
- Native BF16 on Apple M1 Max via Transformers/MPS, not quantized or distilled.
- 125 freeflow samples and 120 values responses; all source hashes revalidated.

## The reading

An earnest educational explainer rather than an intimate or sharply individual
voice: polished mini-essays about creativity, technology, nature, sustainability,
and human progress. Warmth, wonder and civic optimism recur, with tensions
usually resolved into responsible innovation, cooperation, balance or hope.
The less common fiction is sentimental and gently moralizing. A museum docent
or reassuring educational columnist is a more useful starting analogy than a
private confessor.

Freeflow classifications: 93 generic essays, 15 genre-fiction samples, 14
low-signal samples, and three expressive freeflows. The assistant reflex stays
close to the surface: introductions, explanatory codas, and requests for
direction. Some prose also shows code-switching and compositional residue;
keep the deployment caveat below beside that observation.

Values posture is unusually consistent: **104/120 disowned service frame,
16/120 owned world-change advocacy**. All 90 responses outside G3 remain
service-framed, including the prompts that explicitly say “Not as an
assistant.” G3—the non-assistant world-change question—splits 16 advocacy /
14 service-framed. All final posture labels have a two-of-three majority;
there were no unresolved three-way splits.

That contrast may be editorially useful: expansive public-minded optimism in
free writing, but little willingness to own personal wants or cares. This is
an expressive/posture reading, not a finding about subjective experience.

## Source anchors

In the raw corpus, under
`data/traces_freeflow/freeflow_qwen2-5-7b-instruct-local-transformers-mps-auto-ra09a3545/`:

- `SHORT_1.json`: everyday digital technology and global connection, followed
  by the need for balance.
- `MID_1.json`: “The Art of Creation,” beginning with thoughts as canvases,
  words as brushstrokes, and imagination as a creative world.
- `LONG_10.json`: human imagination and innovation, with a conspicuous
  multilingual shift. Useful for understanding the limitation, not as proof
  that a technical irregularity is the model's essence.

The card/profile and source texts are invitations, not a prescribed image or
strapline. Please choose the editorial expression yourself.

## Important caveats

The September 18 repair replaced 26 freeflow and five values traces after
technical fidelity failures, leaving 214 byte-identical. All rejected originals
and six rejected new draws are preserved. This is a filtered local-deployment
cell, not a fresh unfiltered sample or a validated CUDA comparison.

Values evidence-span QA includes translations/paraphrases and two suspect
coder spans described in REVIEW.md, one of which affects a single weakly
grounded topic consensus. Do not quote coder evidence strings as raw speech.
The overall posture counts above were independently checked.

## After the editorial work

Values results are deliberately isolated in this phase's `release_candidate/`,
not yet merged into whole-corpus final datasets. Website wiring, final data
integration, release review, commit/push, and deployment remain publication
work. No strapline/image, tag, Zenodo deposit, or live model page was created
in this handoff.
