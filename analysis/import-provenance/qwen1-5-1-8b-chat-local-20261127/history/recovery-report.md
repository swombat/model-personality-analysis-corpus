# Qwen1.5 1.8B Chat scoped essay recovery — 2026-11-26

Terminal: **exhausted; stopped immediately at MID_15**. No resume or new allowance.

- Exact original roots verified: essays SHORT_18, MID_15, MID_21, MID_24,
  LONG_11, OPEN_8; excluded values root G1_7/qwen3-6-35b-a3b.
- No prior targeted rows for this exact model in original or existing recovery
  databases before preparation. Fresh isolated fork; two persistent slots per
  essay under `qwen18-exact-essays-20261126-v1`.
- LONG_11 recovered and production-validated, using 1/2 slots.
- MID_15 exhausted 2/2 slots, both `quote_sentence_boundary`.
- MID_21, MID_24, OPEN_8, SHORT_18 unattempted. Three targeted calls total.
- Original snapshot, hold, compiled inputs and completed receipts verified
  unchanged. Fork completed receipts rehashed; recovered LONG_11 independently
  passed the production targeted validator after execution.
- No values, scheduler/downstream run, publication, or other agents. Only
  dependency-blocked descendants were released by the existing repair code;
  no ordinary job attempts increased.

Implementation follows `yi34_scoped_essay_recovery.py`, inheriting its guarded
infrastructure stop, global preflight, host lock and original verification:
`qwen18_scoped_essay_recovery.py`.

Evidence:
- `state/qwen18-scoped-essay-recovery-v1/authorization.json`
- `state/qwen18-scoped-essay-recovery-v1/execution-terminal.json`
- `state/qwen18-scoped-essay-recovery-v1/original-verification.json`
- `state/qwen18-scoped-essay-recovery-v1/run.log`
- `remaining_recovery_colab-qwen1-5-1-8b-chat/state.sqlite`

Successful output and provenance/binding receipt paths are recorded in that
fork's LONG_11 job receipts.
