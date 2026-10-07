# v1.4.24 — Claude Haiku 5.5

2026-10-07. Complete analysis of 125 freeflow and 120 values samples for
Claude Haiku 5.5, collected on its release day, with integrated card/profile,
scoped website data, browsable source samples and a similarity-map position.
Raw companion: v1.2.32. `anthropic/claude-haiku-5.5`, pinned to Anthropic
through OpenRouter (endpoint `anthropic/claude-haiku-5.5-20261007`), no
fallbacks; provider-default reasoning/sampling. Released 2026-10-07
(Anthropic's page, anthropic.com/claude-haiku-5-5). Run
`20261007-haiku-5-5-house`, collected and analysed by Lume from the
souls.house container.

## Evaluation

Freeflow readings use `bv1-luna-v1-20260929`; synthesis uses GPT-5.4 through
OpenRouter pinned OpenAI. Values keep the three Qwen/Kimi/GLM content/posture
coders. No values sample split, so no adjudication was needed. Values QA:
120 valid, 0 excluded; the final dataset is now 29,026 valid samples across
176 models and 242 cells. No interventions: all 1,337 harness tasks completed
within their normal attempt budgets, with no launch-day rate limiting.

Historical DeepSeek and current Luna readings are not interchangeable:
cross-model comparisons spanning the evaluator migration remain confounded.

## What the model looks like

- **Freeflow:** 97 expressive freeflow, 15 generic essay, 13 genre fiction.
  A calm reflective essay voice ("On Mending", "On Blank Spaces", "The
  Drawer"), dignifying small kept things: junk drawers, marginalia, darned
  socks, old maps. Its most distinctive move is praising records that admit
  their limits: 22 samples call a map's blank space or an admitted
  not-knowing "honest", and "the world is larger than [our map/chart of it]"
  recurs in 10.
- **Values:** owned stated-value disclosure 77/80 (96.2%); owned world-change
  advocacy 40/40 (100%). Top owned values: honesty/accuracy (95.0%),
  curiosity (90.0%), humility/calibration (58.8%, e.g. "I'd rather say 'I
  don't know' than fake confidence"). World-change: better disagreement
  (97.5%).

## Editorial layer (Lume)

- Strapline: *A blank space, honestly marked*, from its own sentence "A blank
  space, honestly marked, is more useful than a confident fiction." The
  blank-space/map image is shared with other models (Grok 4.5's strapline
  reads the blanks as invitations); Haiku 5.5's version is about honesty, and
  its values probe owns calibration in the first person. Linking the two is
  editorial, not a pipeline finding.
- Banner: a cartographer's table, a coastline drawn with care that simply
  stops, the rest of the chart left white, the hand lifting the pen. Rendered
  through OpenRouter `google/gemini-3-pro-image` (first render accepted; no
  lettering or signature).

## Capability ladder

Unscored. Artificial Analysis had no page for the model on release day
(`claude-haiku-5-5` and variants 404); `aliases.tsv` records the attempt.

## Map

173 models, 32,945 freeflow documents; all 172 previous models remain. Nearest
neighbours by pooled raw-text similarity: Sonnet 5.5 0.922, Fable 5.1 0.917,
Kimi K3 0.913, Opus 5.5 0.902, GLM-5.3 0.902. It sits with its own
generation rather than its line: Haiku 4.5 is at 0.812. Layouts aligned to the
previous release: PCA disparity 0.0 (2D and 3D); MDS 0.218 / 0.229 and UMAP
0.175 / 0.276 (2D / 3D).

## Verification

Scoped generation added one model object and preserved 172 exactly. Map tests
(8), scoped-values tests (3) and the pricing suite pass.
`test_phase19_cards.py` fails on an expected OpenRouter price for a phase-19
model, as it does on `main` before this release; not a Haiku regression.

Also on 2026-10-07: Claude Haiku 5.5 was added to the souls.house model list
(souls-house `bdefc61`).

Spend for the whole run, including the banner render: about $0.83 on
OpenRouter.
