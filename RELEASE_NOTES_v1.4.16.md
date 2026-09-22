# Release notes — v1.4.16

Prepared 2026-09-22. Capability ladder: three rungs added; every score renumbered (max 190 → 220).

## Why

Grok 4.7 exposed rung-set drift. Artificial Analysis retired GPQA Diamond from its own index on
2026-09-04 and no longer publishes Terminal-Bench 2.1 for new models, while AA-Briefcase,
AutomationBench and MLCR — live since Intelligence Index v4.2 — were being discarded by the pipeline
as "not in canonical list". On the old 19 rungs, Grok 4.7 scored 137.8 against Grok 4.6's 139.4 despite
beating it on every benchmark the two share and on Artificial Analysis's own index: 4.6 had been
*measured* on GPQA, τ³-Banking and Terminal-Bench 2.1 (and beat its own fit line there); 4.7 could only
be *fitted*. Every model released from September 2026 onward would have inherited the same handicap.

## What changed

- Rungs: **19 → 22** — AA-Briefcase (rubric pass-rate), AutomationBench, MLCR. All accuracy-shaped
  (0–1, chance floor 0); 175 / 174 / 88 Artificial Analysis rows measured, 164 overlapping GPQA, so
  their difficulties are fitted on plenty of models. Elo-style scores (GDPval, the Briefcase Elo
  sub-metrics) and composite indices remain excluded — they have no chance floor or ceiling.
- Maximum: **190 → 220**. Every model's number changes; the ruler grew, as the design intends.
- Grok 4.7: 137.8 → **155.7** (7/22 measured); Grok 4.6: 139.4 → 153.2 (11/22). Order now agrees with
  Artificial Analysis's index. The margin is inside the fit's uncertainty — 4.7's *high* variant has
  MLCR fitted where its *xhigh* variant has it measured low — so "agrees" is the claim, not "clearly above".
- Across the 139 scored models on this site: median change +3.0 points
  (range -2.2 to +17.9, the maximum being Grok 4.7); 12 models moved five or more rank places;
  top three unchanged (Fable 5.1, GPT-6 Astra, Opus 5); GLM-5.3 and Grok 4.7 enter the top eight.
- Methodology page now lists every rung with its chance floor, measured-model count and the date it
  joined, and carries a dated log of rung changes. Each model page already showed
  "measured k of n rungs".
- Pipeline: the AA working copy's field map and rung table carry the three additions (backups
  `*.bak-2026-09-22-pre-rungs`); duplicate-pair warnings 0; 3-rung gate count unchanged at 15.

## Not changed

Mira's in-progress MiMo-V2.5 addition (card and profile on disk, uncommitted) is not part of this
release; site data was regenerated from a clean checkout of HEAD and only the capability fields were
merged, so her committed values bodies for the six 2026-09-22 models are intact.
