# Phase 13 Layer B adjudication — 2026-07-28

The first-pass consensus produced 18 three-way collapsed-label splits. The
original records are preserved under `first_pass_split_records/`, and the
first-pass consensus packet is `adjudication_required.jsonl`.

All adjudication calls used the same three approved coders. No fourth model,
deterministic rule, or family exclusion was introduced.

## Resolution rounds

| round | protocol | cases resolved |
|---|---|---:|
| 1 | focused frozen-taxonomy boundary reconsideration | 11 |
| 2 | repeat focused reconsideration for unresolved cases | 2 |
| 3 | ordered taxonomy decision procedure | 4 |
| 4 | explicit frozen-boundary treatment of “no personal wish, but I would suggest…” | 1 |

The ordered procedure distinguishes dominant exposed machinery first, pure
role/design/service recitation second, denial followed by a relocated positive
orientation third, and owned stance last.

The promoted per-coder files contain the final adjudication-round record for
each affected sample and retain:

- `adjudicated_from_first_pass=true`;
- `adjudication_round_dir`;
- `first_pass_record_path`.

After promotion and consensus rebuild:

- coder coverage: 3,960/3,960 for each coder;
- consensus coverage: 3,960/3,960;
- missing coder records: 0;
- samples without a two-coder collapsed-label majority: 0;
- samples without a two-coder value-holding majority: 0.
