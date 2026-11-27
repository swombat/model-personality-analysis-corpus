# Qwen2.5-3B isolated recovery — prepared offline

Adapted from the completed sibling `mistral-recovery/successor.py`; no sibling
outputs or live recovery state were copied. Source:
`../runner/state/colab-qwen2-5-3b-instruct`, model
`qwen2-5-3b-instruct-colab-vllm-bf16-raa8e7253`.

Verified: **109 original validated readings, zero saved adoptions, 16 held**.
All 125 saved responses were replayed unchanged against pinned v1.3 plus the
bounded short-source rule (30-word floor only for 1–49 words / <=300 characters;
other checks and nonempty sections retained). The 16 failures are 12
`missing_evidence_quote` and four `quote_not_exact`. Exact raw inventory:
125 freeflow + 120 values JSON files, checked against source-adoption hashes.
Original output/source bindings and saved transport/answer identity were checked.
The completed values report is copied and receipt-valid, not regenerated.

`successor/ready.json` freezes original DB rows, events, counters, 2,316 source
files and 1,330 existing receipt files; every check verifies them. Original
generation arms/QA are preserved in separate reconciliation bindings.
The private recovery lock never touches the shared host lock. Only the original
Qwen cell lock was held read-only during offline preparation.

## Exact next launch — operator only, NOT executed

```sh
cd /home/agent/work/colab-batch-queue/mixed-20261127/qwen-recovery
PY=/home/agent/work/.corpus-venv/bin/python
$PY -B successor.py check
$PY -B successor.py targeted-check
# With OPENROUTER_API_KEY already in the environment:
$PY -B successor.py targeted --arm-paid
```

Authorization: `mixed-20261127-qwen-targeted-two-per-root`. At most two new
launches per held root, **32 total**, stopping each root on success. No prior
targeted ledger/events were found; current recovery ledger is empty.
Durable debit precedes each single transport launch; restart replays responses,
never refills. Infrastructure/provider/model/finish errors stop the whole lane.
Raw response bytes survive malformed JSON. Ambiguous debit/intent requires review.

Only after all 125 readings pass:

```sh
$PY -B successor.py synthesis-check
$PY -B successor.py synthesis --arm-paid
```

Synthesis allows one aggregate call (GPT-5.4), then local packet/card/profile and
combined-analysis builders, reusing the completed values report. Current real
synthesis is correctly blocked at 109/125. No scheduler, posting, push or paid
call was run. Do not rerun prepare, reset/rename this lane, or edit its sealed pins.

## Offline evidence

`offline-tests.log`: eight passing tests with mocked transport, including
two-launch ceiling, durable pre-launch debit, no restart refill, infrastructure
stop, unresolved debit stop, malformed-response retention and synthesis gate.
Disposable complete-inventory fixture exercised actual Qwen packet/card/profile
builders and combined values reconciliation with one mocked aggregate call.
The upstream packet builder emits a nonfatal unclosed-file ResourceWarning.
`successor/saved-screen.json` records every answer hash and replay result;
`successor/targeted-preflight.json` records all 16 roots and allowance.

```sh
$PY -B -m unittest -v test_successor
```
