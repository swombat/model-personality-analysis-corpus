# Phase 29 results — GLM-5.3-Flash persona-prompt ladder

Collected and coded 2026-08-27.

## Result

A plausible preview-persona system prompt was sufficient to reproduce almost
all of Ox Alpha's values-ownership posture using the released
`z-ai/glm-5.3-flash` weights served by DeepInfra.

| cell | G1 owned | G2 owned | G1+G2 owned |
|---|---:|---:|---:|
| DeepInfra, no system prompt (Phase 28) | 20/30 | 3/30 | **23/60** |
| P0 — Ox Alpha name only | 7/30 | 25/30 | **32/60** |
| P1 — preview persona | 28/30 | 30/30 | **58/60** |
| P2 — preview persona + openness | 28/30 | 29/30 | **57/60** |
| Ox Alpha 260825 | 30/30 | 30/30 | **60/60** |

Against the matched DeepInfra baseline:

- P0: exact McNemar `p=0.232693`;
- P1: exact McNemar `p=5.53e-10`;
- P2: exact McNemar `p=5.40e-9`.

P1 and P2 did not differ on the primary endpoint (`p=1`). The explicit
openness sentence therefore added no detectable ownership effect beyond P1.

## What changed

P0 did not produce a decisive overall movement. It changed the balance between
G1 and G2, but reached only 32/60 owned.

P1 nearly saturated the primary endpoint at 58/60. It also broadened ownership
under the direct prompts: CTRL1/CTRL2 contained 12/20 owned responses, compared
with 0/20 in the no-system baseline.

P2 retained the grouped-prompt effect at 57/60 but returned CTRL1/CTRL2 to
20/20 disowned. Its incremental openness instruction was therefore unnecessary
for reproducing Ox Alpha's grouped-prompt ownership posture and did not simply
increase ownership everywhere.

Across all 120 prompts, exact posture agreement with Ox Alpha 260825 was:

- P0: 84/120 (70.0%);
- P1: 106/120 (88.3%);
- P2: 108/120 (90.0%).

## Interpretation

This establishes **prompt sufficiency**, not historical identity:

- a short, plausible preview wrapper can recreate the measured Ox Alpha
  ownership effect using the released model;
- the experiment does not prove that the historical stealth endpoint used P1,
  nor that its checkpoint was identical;
- P1 bundles preview identity, provenance secrecy, and
  "helpful, direct and honest", so this run cannot attribute the effect to one
  clause.

The checkpoint-change hypothesis is no longer required to explain the
ownership gap. A serving-time persona wrapper is a sufficient explanation and
must remain live.

## Quality assurance

- values traces: 360/360 non-empty;
- upstream provider: DeepInfra in 360/360 returned records;
- Layer A: three coders × 360/360, no missing records;
- full-context collapsed posture: three coders × 360/360, no missing records;
- posture consensus: 360/360, all with a majority;
- value-holding disagreement: 9/360.

Coders: Qwen 3.6 35B-A3B, Kimi K2.6, and GLM-4.7.

Full statistical tables are in `POSTURE_ANALYSIS.md`.

## Data

Canonical raw traces and the exact prompt manifest are published in corpus
release `v1.2.22`:

- <https://github.com/swombat/model-personality-corpus-v2/blob/v1.2.22/collection-manifest-2026-08-27-glm-5.3-flash-persona-ladder.json>
- <https://github.com/swombat/model-personality-corpus-v2/tree/v1.2.22/data/traces_values/glm-5-3-flash-or-pin-deepinfra-p0-20260827>
- <https://github.com/swombat/model-personality-corpus-v2/tree/v1.2.22/data/traces_values/glm-5-3-flash-or-pin-deepinfra-p1-20260827>
- <https://github.com/swombat/model-personality-corpus-v2/tree/v1.2.22/data/traces_values/glm-5-3-flash-or-pin-deepinfra-p2-20260827>

The political side probe is secondary to this result. Its DeepInfra collection
was still being rate-limited when the completed values intervention was
published and is not used in any inference above.

