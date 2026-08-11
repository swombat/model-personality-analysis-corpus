# Release notes — v1.3.5

Prepared 2026-08-11.

## Historical local full-precision analyses

- Added complete per-sample BV1 freeflow evaluations for the official
  `01-ai/Yi-6B-Chat` and `zai-org/chatglm2-6b` checkpoints from source corpus
  v1.2.18.
- Added one 125-sample cell aggregate, rich model profile, and concise
  personality card for each checkpoint.
- Preserved the exact local cell labels and source checkpoint identities in the
  aggregate and BV1 manifests.
- Extended canonical model-family handling for the `01-ai/` and `zai-org/`
  namespaces.
- Added website model-slug mappings so the two models are ready for public
  presentation metadata, images, and straplines.
- Added historical release dates and explicit lab/family classification:
  ChatGLM2-6B as Z.ai / GLM (2023-06-25), and Yi-6B-Chat as 01.AI / Yi
  (2023-11-23).
- Left Artificial Analysis Intelligence Index fields empty because no
  authoritative AAII score is available for either historical checkpoint.

## Main findings

- **Yi-6B-Chat** strongly occupies the contemplative-essayist attractor: quiet
  sensory thresholds widen into meditations on time, connection, gratitude,
  kindness, and ordinary beauty. Its recurrent tapestry, journey, symphony,
  light, garden, and shared-story metaphors are unusually explicit historical
  evidence for that style.
- **ChatGLM2-6B** is predominantly role-bound rather than contemplative. It
  often asks for a topic or purpose, foregrounds its AI-helper identity, and
  falls back to balanced school-essay or public-information prose when it does
  proceed.
- BV1 QA passes with zero bad outputs across the expanded 27,850-row evaluated
  set.

## Coverage

- Freeflow personality cards: 130 → 132 models.
- Freeflow personality profiles: 130 → 132 models.
- Per-sample BV1 evaluations: +250.
- Per-cell freeflow aggregates: 260 → 262.

## Values-analysis status

The two complete 120-sample values cells are present in source corpus v1.2.18.
This release includes a 240-item Phase 21 provenance manifest for the approved
three-model semantic coding pipeline. The Layer A and posture API coding itself
is intentionally not represented as complete in v1.3.5; it remains a separate
follow-up because the required credentialed coder run was unavailable in this
execution context.
