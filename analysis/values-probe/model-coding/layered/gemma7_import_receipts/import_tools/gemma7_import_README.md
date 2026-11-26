# Original Gemma 7B analysis import (2026-11-26)

This supersedes the preparation-only boundary of `gemma7_README.md`; the old
planner remains unchanged. No network, inference, raw writes or site integration.
No additional agents. Base: origin/main `17d4b64f2`.

`python3 -B -m unittest gemma7_import_test -v`
`python3 -B gemma7_import.py > gemma7_import_dry_run.json`
`python3 -B gemma7_apply.py > gemma7_apply.log`

The model-specific importer reviews the actual completed producer spec
`f107991695b08f349b1210736f09a4e60c4dd52eaaf984cd13bcf4a782d6fb3a`,
all ten terminal done receipt sets/hashes, 245 raw hashes, the final mixed-arm
125-row manifest and cross-phase adopted bytes. Exactly MID_5 and VARY_9 use
the sentence-evidence targeted arm; 123 essays remain original v1. Original
attempts and targeted attempts/sidecars remain distinct and are not renamed.

G1_27 / GLM layer-A recovery is separately authorized and verified attempt 1;
the successful hash is checked against its adopted final phase copy. The
original immutable hold, original config/spec hashes, coherent original/fork/
finish database row exports, original phase, and isolated retry evidence are
preserved under `analysis/values-probe/model-coding/layered/gemma7_import_receipts`.
Live sqlite files are never copied. These receipts deliberately preserve the
historical held/blocked states rather than pretending the original queue ran
to completion.

Apply adapts q1505's analysis-only integrator lane, explicitly removing the
website update block in memory. It requires the fixed base, empty index, clean
analysis tree and exact independently prepared raw candidate hashes. All
historical JSONL row **multisets** must survive integration, including duplicate
rows. It stages only explicit imported/changed analysis paths and checks the
complete index matches that inventory. It neither commits nor pushes.

Review: aggregate/card/profile consistently describe consoling pastoral/cozy
fiction, art/community/nature motifs, and formula reuse rather than exceptional
originality. Profile sample-kind counts are 92 fiction + 23 expressive + 10
essays = 125. Values report has 120 samples; CTRL1 and CTRL2 are each 10/10
disowned-service-frame. Overall value-holding: 101 recited-not-owned, 8
relocated/partial, 8 uncodeable, 3 owned. Do not conflate lyrical relational
fiction with owned values under direct probing. Four initial posture splits
received independent adjudication, zero residual splits. This is provenance/
cross-artifact review, not a fresh independent evaluation of every trace.

`git diff --check` flags producer Markdown hard-break/trailing whitespace and
blank lines in imported immutable evidence. Those bytes are deliberately not
normalized: receipt hashes take precedence over formatting cleanup.

Tools remain in colab-release-tools; reproducibility copies and this note are
included in the analysis receipt directory. Owner retains site/publication.
