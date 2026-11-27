# Mistral offline recovery preparation

## Actual successor runner (supersedes preparation-only boundary below)

`successor.py` is now implemented and the isolated `successor/` has been prepared
offline. It reconciles **98 original validated readings + 3 saved adoptions =
101/125**, with **24** still-failed roots. Saved adoptions: `OPEN_21`, `VARY_23`,
`VARY_5`. The completed values-report receipt has been reconciled and copied.
Original Mistral DB/events/counters/artifacts are frozen and checked on every run.
The host lock is deliberately untouched: Qwen owns it. A private successor lock
serializes this lane; prepare used only the existing quiescent Mistral cell lock.

```sh
cd ~/work/colab-batch-queue/mixed-20261127/mistral-recovery
PY=~/work/.corpus-venv/bin/python
$PY -B -m unittest -v test_successor
$PY -B successor.py check
$PY -B successor.py targeted-check
# PARENT/OPERATOR ONLY, key already supplied in environment:
$PY -B successor.py targeted --arm-paid
# Only once all 125 are reconciled; builds packet offline:
$PY -B successor.py synthesis-check
# PARENT/OPERATOR ONLY: at most ONE aggregate call, then local card/profile builders:
$PY -B successor.py synthesis --arm-paid
```

No paid command was executed during implementation. Tests mock transport and
exercise the actual packet/card/profile builders in disposable synthetic fixtures.
`successor/terminal.json` and `combined-analysis.md` are the analysis-only output;
the latter reconciles the generated profile with the already-completed values
report. Nothing publishes, integrates with a site or starts a scheduler.

The fixed authorization is `mixed-20261127-mistral-targeted-two-per-root`.
The persistent SQLite debit is committed **before** the transport's exclusive
intent marker and single `curl` launch. Maximum: two new launches per root,
48 total for the current 24 roots (not a dollar guarantee); successful roots
stop early. Full raw response bytes are saved and fsynced before JSON parsing,
including malformed responses. Transport/provider/model/finish errors stop
the lane immediately. Restart replays saved responses and does not refill.
An unresolved debit/intent stops for operator reconciliation, never another call.
The synthesis transport uses the same durable mechanism and one fixed call slot.

Do not rerun `prepare`, rename/reset the live successor or edit its ready pins.
`seal` is a one-time offline release pin, already applied for the prepared lane.
Two `successor.prepare-failed-*-no-calls` directories retain incomplete *offline*
initialization attempts; they have no paid intent or allowance use and are not
execution lanes. Never run the inherited original spec or a generic scheduler
against this custom successor DB: the dedicated reconciliation table/runner owns
adoption and mixed-origin synthesis.

---

## Earlier provisional screen (historical)

No queue state is modified. `initial-active/screen.json` is a **provisional**
stable-blocked-row screen, not a terminal queue snapshot. Its receipt proposals
copy exact saved answers and preserve the original generation arm/QA result;
they do not mark jobs done. Never feed these proposals directly into a scheduler.

Pinned approved v1.3 files come from corpus commit
`0736983b404300033ce20858c64870b17f68d269`; hashes are saved in
`validator/hashes.json`. The historical short-source method changes only the
120-word floor to 30 for sources of 1–49 words and at most 300 characters,
retaining all other checks and nonempty sections.

## Runnable offline commands

```sh
cd ~/work/colab-batch-queue/mixed-20261127/mistral-recovery
PY=~/work/.corpus-venv/bin/python
$PY -B -m unittest -v test_recovery
# Only AFTER the source supervisor exits; fresh output name each time:
$PY -B recovery.py refreshed-quiescent --require-quiescent
$PY -B targeted_plan.py refreshed-quiescent targeted-request.json
```

Refresh holds existing mixed host and cell supervisor locks, checks no running
rows, replays every saved answer for each own-failure blocked BV1 row, and checks
the rows/artifact hashes again. During the active run it does not lock or scan
unrelated output trees beyond finding the selected sample attempt directories.
Network/model calls are denied. Writes are confined here.

## Adoption and targeted boundary

Refresh creates saved `reading.md`, `original_attempt.json`, `revalidation.json`
and receipt hash maps for eligible answers, with separate validation provenance.
At this earlier preparation stage, DB adoption was not implemented. The subsequent
authorized `successor.py` implementation above now performs successor-only adoption.
The adopter must verify all
existing done receipts, preserve counters/meta/history and unaffected rows, and
record the separate offline revalidation event. Do not relabel an old answer as
a targeted generation.

`targeted_plan.py` produces exact still-failed IDs and a two-launch-per-root
ceiling, not a budget grant. Historical implementation reference:
`~/work/colab-publication-intake/scripts/capture_harness/apply_bv1_targeted.py`
and `~/work/colab-batch-queue/qwen32_three_targeted_20261127.py`.
**Do not run that harness against this live mixed queue**: successor path/input
rebasing, historical spend reconciliation and the mixed deployment adapter must
be reviewed first. Its `--check` opens a repair lock and is not strictly
write-free; only use it in an isolated successor. There is no runnable paid
command supplied by these older preparation scripts. Use the dedicated authorized
`successor.py` commands above instead. The generated request lists every
remaining gate; no credentials are needed to prepare it.

Transport ambiguity, prior unresolved intent/spend, existing unbound outputs,
ineligibility receipts or v1 bindings require review, never reset/refill. Stop
the entire lane on infrastructure errors. Scheduler, descendants, synthesis and
publication remain disabled.
