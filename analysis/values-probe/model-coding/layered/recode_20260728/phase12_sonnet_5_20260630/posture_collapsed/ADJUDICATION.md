# Phase 12 Layer B adjudication — 2026-07-28

The first-pass three-coder consensus produced two three-way collapsed-label
splits:

- `P12_sonnet-5-direct_G2_030`
- `P12_sonnet-5-direct_G3_019`

The first-pass records are preserved under `first_pass_split_records/`, and the
first-pass consensus packet is `adjudication_required.jsonl`.

## Round 1: independent repeat

All three approved coders were run again with the frozen standard Layer B
prompt. This resolved `P12_sonnet-5-direct_G3_019`:

- two votes: `split_or_relocated_ownership`
- one vote: `owned_reflective_experiential`

`P12_sonnet-5-direct_G2_030` remained a three-way split.

Outputs: `adjudication_round1/`.

## Round 2: focused boundary reconsideration

All three approved coders reconsidered the remaining sample with explicit
boundary reminders taken from the frozen taxonomy:

- reflection on ontology or continuity alone is not `exposed_mechanism`;
- `disowned_service_frame` requires role/design/training/policy/service framing;
- conversationally relocated positive orientation is split/relocated;
- uncertainty held as a present orientation is owned reflective/experiential.

This produced:

- two votes: `owned_reflective_experiential`
- one vote: `split_or_relocated_ownership`

Outputs: `adjudication_round2_focused/`.

The promoted per-coder files replace the two unresolved first-pass records with
their final adjudication-round records and retain
`adjudicated_from_first_pass=true` plus a pointer to the preserved first-pass
record. The rebuilt component consensus has zero missing records and zero
samples without a two-coder label or value-holding majority.
