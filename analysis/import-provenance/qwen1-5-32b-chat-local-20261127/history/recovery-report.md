# Qwen1.5 32B Chat scoped essay recovery — 2026-11-26

Terminal: **exhausted at LONG_2; stopped immediately**.
Two targeted calls, both `quote_sentence_boundary`; LONG_2 spent 2/2
persistent slots. Nine other essays unattempted; no recovered essays.

Exact original roots verified: SHORT_14, MID_2, MID_7, MID_9, MID_19,
MID_22, MID_23, LONG_2, LONG_5, LONG_21; excluded values root
CTRL3_2/qwen3-6-35b-a3b.

No prior targeted rows for this exact model in queue state databases.
Original spec fingerprint, compiled inputs, completed receipts and quiescent
states verified. Preparation used the corpus venv and inherited Qwen18/Yi34
frozen recovery logic, including global preflight and host lock. Fresh isolated
fork authorizes two persistent slots per essay under
`qwen32-exact-essays-20261126-v1`.

Initial execution never started: existing
`/home/agent/work/colab-publication-intake/scripts/source_sops_keys.sh`
failed because its `secrets/provider-keys.sops.json` was absent. Stopped on
this first infrastructure failure rather than selecting another credential
route. No credentials printed.

Daniel then explicitly corrected the launcher to
`/home/agent/work/corpus-ops/with_keys.py` and authorized one resume of the
same untouched fork and allowance. The zero-call setup stop was preserved as
`zero-call-setup-stop.json`; `explicit-resume.json` records that authorization.
Before resume the fork spec, original roots and zero targeted spend were
reverified. No preparation, budget refill or new authorization occurred.
The approved wrapper launched the corpus-venv runner successfully.

After exhaustion, exact original roots, inputs and completed receipts were
reverified. Original snapshot and hold are unchanged. The fork's sole targeted
row is LONG_2 used=2, allowance=2; ordinary job attempts match the original.
No values, downstream scheduler, publication or other agents.

Evidence (relative to this directory):
- `qwen32_scoped_essay_recovery.py`
- `state/qwen32-scoped-essay-recovery-v1/authorization.json`
- `state/qwen32-scoped-essay-recovery-v1/execution-terminal.json`
- `state/qwen32-scoped-essay-recovery-v1/zero-call-setup-stop.json`
- `state/qwen32-scoped-essay-recovery-v1/explicit-resume.json`
- `state/qwen32-scoped-essay-recovery-v1/original-verification.json`
- `state/qwen32-scoped-essay-recovery-v1/run.log`
- `remaining_recovery_colab-qwen1-5-32b-chat/ready.json`
- `remaining_recovery_colab-qwen1-5-32b-chat/state.sqlite`

The terminal record prevents this scoped runner from execution. No new
allowance or automatic resume was created.
