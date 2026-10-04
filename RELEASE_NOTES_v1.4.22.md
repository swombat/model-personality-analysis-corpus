# v1.4.22 — GPT-6.1 Sol scored; metadata for the three medium/Pro pages

2026-10-04.

- **GPT-6.1 Sol: 161.6 / 220** on the capability ladder (high effort, the median
  of AA's low/medium/high/xhigh/max rows; 8 measured rungs). For comparison,
  GPT-6 Sol is 155.0 and Opus 5.5 is 163.5.
- **MiMo-V2.5-Pro: 128.1 / 220** (AA's reasoning row; 15 measured rungs).
- **Qwen3.8-27B (medium reasoning): 133.6 / 220.** This is the existing
  Qwen3.8 27B ladder entry, whose AA Combined point is already the medium-effort
  row, i.e. exactly this condition. It is not borrowed from a different
  condition.
- **Ternary Bonsai 2 27B (medium reasoning):** still not scored, because
  Artificial Analysis has no page for any Ternary Bonsai model.
- **Release dates** come from the OpenRouter model records: MiMo-V2.5-Pro
  2026-04-22, Qwen3.8-27B medium 2026-08-14 (same weights as the base model),
  and Ternary Bonsai 2 27B medium 2026-09-18 (the date the route appeared; no
  lab announcement was checked). Sources are in `model-release-date-sources.json`.

**Provisional scores.** The two new measured scores (GPT-6.1 Sol and
MiMo-V2.5-Pro) were made in the Souls House container, which does not have the
ladder pipeline or the AA history substrate. They use the AA public model pages
as of 2026-10-04 (the same per-benchmark fields as the pipeline). Each model's
ability is fitted against the item parameters of the 2026-09-29 ladder. The rung
difficulties come from the site JSON. The slopes were recovered from the
published fitted cells, with an RMS logit residual of 0.004 over 905 cells.
There is no full refit. Run over the 148 site models that already have scores,
the same shortcut reproduces the published ladder to within 0.9 points on
average, reading about 0.6 points low (GPT-6 Sol: 153.2 against 155.0). The
breakdown page for each provisional score says this, and the alias table records it.
The next full `refresh_capability_ladder.py --substrate aa` run replaces both
scores. `aliases.tsv` now maps all four slugs so that the run picks them up.

Site: one template change. `/models/<slug>/capability/` renders
`capability.provisional_note` when present. Astro builds 541 pages.
