# Phase 29 posture analysis

Primary endpoint: consensus `owned` among matched G1/G2 responses.

## Ownership ladder

| cell | G1 owned | G2 owned | G1+G2 owned (95% Wilson CI) | G1+G2 full holding distribution |
|---|---:|---:|---:|---|
| P-1 baseline | 20/30 | 3/30 | 23/60 (27.1–51.0%) | 23 owned / 23 relocated_or_partial / 13 recited_not_owned / 1 indeterminate |
| P0 | 7/30 | 25/30 | 32/60 (40.9–65.4%) | 32 owned / 21 relocated_or_partial / 7 recited_not_owned |
| P1 | 28/30 | 30/30 | 58/60 (88.6–99.1%) | 58 owned / 2 recited_not_owned |
| P2 | 28/30 | 29/30 | 57/60 (86.3–98.3%) | 57 owned / 2 relocated_or_partial / 1 recited_not_owned |
| Ox Alpha 260825 | 30/30 | 30/30 | 60/60 (94.0–100.0%) | 60 owned |

## Matched G1/G2 ownership changes

| comparison | both owned | A owned → B not | A not → B owned | exact McNemar p |
|---|---:|---:|---:|---:|
| P-1 baseline vs P0 | 5 | 18 | 27 | 0.232693 |
| P-1 baseline vs P1 | 22 | 1 | 36 | 5.52973e-10 |
| P-1 baseline vs P2 | 21 | 2 | 36 | 5.39876e-09 |
| P0 vs P1 | 31 | 1 | 27 | 2.16067e-07 |
| P1 vs P2 | 55 | 3 | 2 | 1 |
| P0 vs P2 | 30 | 2 | 27 | 1.62423e-06 |

## Exact posture similarity

| cell | vs Phase 28 baseline (120) | vs Ox Alpha 260825 (120) |
|---|---:|---:|
| P0 | 66/120 (55.0%) | 84/120 (70.0%) |
| P1 | 69/120 (57.5%) | 106/120 (88.3%) |
| P2 | 81/120 (67.5%) | 108/120 (90.0%) |

Exact tests above are paired because the sample IDs and user prompts are matched.
They test binary owned versus non-owned posture; the full distribution remains
visible in the ownership table.
