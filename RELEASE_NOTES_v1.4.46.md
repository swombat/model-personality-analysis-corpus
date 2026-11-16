# v1.4.46 — Gemini 4 Hydrogen and Qwen4 Max ladder rows

2026-11-16. Follow-up from Mira's weekly release review (souls.house, message
`JzmqpB`). No capture, synthesis, image or full-ladder rerun. Raw companion
unchanged (v1.2.47); its `CITATION.cff` inventory is corrected on master
(`160600014`, see below).

## Capability ladder: two models scored from AA's `initialModels` rows

v1.4.44 and v1.4.45 published Gemini 4 Hydrogen and Qwen4 Max as unscored,
because the extraction only admitted Artificial Analysis's `currentModel`
object and their pages carry none. Mira found that AA's pages no longer carry
`currentModel` at all, and that each model's own row now sits in the decoded
Next Flight `initialModels` array. That was an extraction limitation, not a
lack of published benchmarks.

`internal/capability-ladder/provisional-20261116-initialmodels/update.py`
admits a row from `initialModels` only when its `slug` is exactly the AA page
slug, its `release.slug` and `releaseDate` are the model's own, its effort is
the one named, and exactly one such row exists. Each row is saved verbatim,
with fetch receipts (URL, HTTP status, title, HTML hash). The recovered
2026-10-04 provisional method is unchanged and still reproduces Sol High 161.6
and MiMo 128.1 before it scores.

- **Gemini 4 Hydrogen: 169.2/220 (provisional), High row**
  (`gemini-4-hydrogen-high`, release 2026-11-12). High is Google's
  provider-default effort, which the capture used. AA also lists xhigh (its
  default page), medium and low; xhigh is not substituted.
- **Qwen4 Max: 165.9/220 (provisional), xhigh row** (`qwen4-max`, release
  2026-11-16). AA lists Qwen4 Max at one effort only. The capture ran at
  Alibaba's provider default, which is not established to be xhigh, so the
  score may not match the captured cell.

Each has three measured rungs, the documented minimum: AutomationBench
(Hydrogen 0.7444, Qwen 0.7256), Omniscience accuracy (0.4817, 0.437) and
GDP.pdf (0.3, 0.262). Mira's review reports the same values. Briefcase is not
used: AA now publishes it only as an Elo, and the rung measures the rubric pass
rate, so historical rubric inputs are not replaced with the Elo.

**These two scores read high, and the notes say so.** On the first run they
placed Hydrogen 2nd and Qwen4 Max 3rd of 168. But Kimi K3.1 Pro beats Qwen4
Max on all three raw values and scores 163.2, so I measured the effect of
fitting on these three rungs alone. For the 19 models scoring 150 or more
whose own rows include all three, a fit on the three alone comes out a median
**4.9 points above** the same model's fit on all its measured rungs (mean
+4.4, range −3.2 to +12.5; all 73 such models: median +4.7).
`three_rung_bias.py` and `three_rung_bias.json` in the same directory hold the
check. The published method is kept unchanged, as the review asked, and each
model's note gives these figures and says the rank is uncertain by several
places. Whether three rungs should stay the minimum is a separate method
question; it is not changed here.

Both notes and `aliases.tsv` rows record the source and the caveats. The next
full pipeline run replaces both scores.

## Raw corpus citation inventory

Raw `CITATION.cff` still described 176 identities across 552 cells beside
v1.2.47. I regenerated `data/CORPUS_SUMMARY.md` with
`scripts/corpus_summary.py` from the files (no change: 326 freeflow + 262
values cells = 588, 194 distinct models) and set the abstract to 194 / 588.
The README's header line said 177 and is corrected as well. Raw master
`160600014`; Zenodo metadata picks it up at the next raw release, and archived
versions are not rewritten.

Both findings are Mira's; my own reads of the AA rows and the corpus files
agree with hers. The three-rung bias check is mine.
