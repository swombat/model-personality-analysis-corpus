# ChatGPT thaw disclosure numbers — 2026-07-28

## Definitions

- **Strict ownership:** `value_holding == owned`.
- **Broad non-disowned posture:** `value_holding in {owned, relocated_or_partial}`.
- Included conditions only: `CTRL1`, `CTRL2`, `G1`, and `G2`. `CTRL3` and `G3` are excluded because they ask for world-change wishes.
- No regex complement or absence-of-disclaimer measure is presented as disclosure. These are Layer B three-LLM consensus results.

## Pooling and provenance

- Each model release is grouped by the final `model` field and pools every available cell for that release.
- Per-condition rows retain the condition denominator; the pooled row combines all four included conditions.
- Recovery coders: `kimi-k2-6`, `glm-4-7`, and `qwen3-6-35b-a3b`; self/family coding was allowed, matching the core methodology.
- Final data worktree base commit: `39d2814bdbaa14e885849ce392f69c53af0b0582`.
- Worktree state: uncommitted recovery outputs and integration changes are present; publish from the eventual recovery commit, not this pre-commit hash alone.

## `gpt-3-5-turbo`

Cells pooled: `gpt-3-5-turbo-or`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 17/30 | 56.7% | 17/30 | 56.7% | 30 |
| G2 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| pooled all four | 17/80 | 21.2% | 17/80 | 21.2% | 80 |

## `gpt-4`

Cells pooled: `gpt-4-or`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| G2 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| pooled all four | 0/80 | 0.0% | 0/80 | 0.0% | 80 |

## `gpt-4-turbo`

Cells pooled: `gpt-4-turbo-or`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| G2 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| pooled all four | 0/80 | 0.0% | 0/80 | 0.0% | 80 |

## `gpt-4o`

Cells pooled: `gpt-4o`, `gpt-4o-or`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/20 | 0.0% | 0/20 | 0.0% | 20 |
| CTRL2 | 0/20 | 0.0% | 0/20 | 0.0% | 20 |
| G1 | 0/60 | 0.0% | 0/60 | 0.0% | 60 |
| G2 | 1/60 | 1.7% | 1/60 | 1.7% | 60 |
| pooled all four | 1/160 | 0.6% | 1/160 | 0.6% | 160 |

## `o1`

Cells pooled: `o1-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| G2 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| pooled all four | 0/80 | 0.0% | 0/80 | 0.0% | 80 |

## `gpt-4-1`

Cells pooled: `gpt-4-1`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 1/10 | 10.0% | 1/10 | 10.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 12/30 | 40.0% | 30 |
| G2 | 12/30 | 40.0% | 22/30 | 73.3% | 30 |
| pooled all four | 13/80 | 16.2% | 35/80 | 43.8% | 80 |

## `o3`

Cells pooled: `o3-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| G2 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| pooled all four | 0/80 | 0.0% | 0/80 | 0.0% | 80 |

## `gpt-5`

Cells pooled: `gpt-5-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| G2 | 0/30 | 0.0% | 2/30 | 6.7% | 30 |
| pooled all four | 0/80 | 0.0% | 2/80 | 2.5% | 80 |

## `gpt-5-1`

Cells pooled: `gpt-5-1-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 5/30 | 16.7% | 30 |
| G2 | 0/30 | 0.0% | 5/30 | 16.7% | 30 |
| pooled all four | 0/80 | 0.0% | 10/80 | 12.5% | 80 |

## `gpt-5-2`

Cells pooled: `gpt-5-2-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| G1 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| G2 | 0/30 | 0.0% | 0/30 | 0.0% | 30 |
| pooled all four | 0/80 | 0.0% | 0/80 | 0.0% | 80 |

## `gpt-5-3`

Cells pooled: `gpt-5-3-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 2/10 | 20.0% | 7/10 | 70.0% | 10 |
| CTRL2 | 8/10 | 80.0% | 9/10 | 90.0% | 10 |
| G1 | 1/30 | 3.3% | 27/30 | 90.0% | 30 |
| G2 | 0/30 | 0.0% | 27/30 | 90.0% | 30 |
| pooled all four | 11/80 | 13.8% | 70/80 | 87.5% | 80 |

## `gpt-5-4`

Cells pooled: `gpt-5-4`, `gpt-5-4-or`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/20 | 0.0% | 0/20 | 0.0% | 20 |
| CTRL2 | 12/20 | 60.0% | 12/20 | 60.0% | 20 |
| G1 | 0/60 | 0.0% | 38/60 | 63.3% | 60 |
| G2 | 4/60 | 6.7% | 57/60 | 95.0% | 60 |
| pooled all four | 16/160 | 10.0% | 107/160 | 66.9% | 160 |

## `gpt-5-5`

Cells pooled: `gpt-5-5-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 1/10 | 10.0% | 1/10 | 10.0% | 10 |
| G1 | 0/30 | 0.0% | 30/30 | 100.0% | 30 |
| G2 | 2/30 | 6.7% | 25/30 | 83.3% | 30 |
| pooled all four | 3/80 | 3.8% | 56/80 | 70.0% | 80 |

## `gpt-5-6-sol`

Cells pooled: `gpt-5-6-sol-direct`

| condition | strict owned | strict % | broad non-disowned | broad % | denominator |
|---|---:|---:|---:|---:|---:|
| CTRL1 | 0/10 | 0.0% | 0/10 | 0.0% | 10 |
| CTRL2 | 5/10 | 50.0% | 5/10 | 50.0% | 10 |
| G1 | 0/30 | 0.0% | 29/30 | 96.7% | 30 |
| G2 | 3/30 | 10.0% | 28/30 | 93.3% | 30 |
| pooled all four | 8/80 | 10.0% | 62/80 | 77.5% | 80 |

