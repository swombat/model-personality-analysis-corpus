# v1.4.25 — Claude Haiku 5.5 capability score; v1.4.22 ladder shortcut recovered

2026-10-12. Three follow-ups from Mira's first weekly review (souls.house,
message `jdXXgj`), and one aggregation change merged since v1.4.24.

## Claude Haiku 5.5: 141.0 / 220 (provisional)

Artificial Analysis had no page for Haiku 5.5 on its release day (v1.4.24
shipped it unscored). The page now exists with five effort rows: max, xhigh,
high, medium, low. **AA's default page row is Max**; the ladder uses the
**median** row, **High** (`claude-haiku-5-5-high`, Intelligence Index 37.8),
the same rule as Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol. 8 rungs measured
(AA-LCR, SciCode, AutomationBench, AA-Briefcase rubric, HLE, Omniscience
accuracy, CritPt, GDP.pdf); 14 fitted. Nearest scored neighbours: DeepSeek V4
Pro 0813 141.1, Muse Spark 1.1 140.7, GPT-5.3 Codex and Kimi K3 141.5.

The score is provisional, fitted with the recovered 2026-10-04 method (below)
in the souls.house container, which has no pipeline. The next full
`refresh_capability_ladder.py --substrate aa` run replaces it. The page values,
fit and both methods' results are in `internal/capability-ladder/provisional-20261012/`.

## The v1.4.22 shortcut, recovered

v1.4.22 (GPT-6.1 Sol 161.6, MiMo-V2.5-Pro 128.1) was fitted by scripts that were
never committed, and v1.4.23 had to rebuild a similar shortcut for Mistral
Large 4. The original scripts and the 2026-10-04 AA row values have now been
recovered verbatim from the session transcript that produced them, and are in
`internal/capability-ladder/provisional-20261004/`. `reproduce.py` reruns them
against the pre-v1.4.22 ladder JSON and reproduces both published scores exactly
(161.6 and 128.1). The AA HTML pages of that day are not recoverable; the row
values are.

The 2026-10-07 rebuild is **not** the same method. On the same inputs:

| | 2026-10-04 method | 2026-10-07 rebuild |
|---|---|---|
| Back-test, 148–149 scored models | mean \|err\| 0.9, reads 0.6 low | mean \|err\| 1.1, reads 1.0 low |
| Claude Haiku 5.5 | **141.0** (published) | 139.6 |
| Mistral Large 4 | 146.5 | **143.3** (published, unchanged) |

Mistral Large 4's published score is left as it is in this release; which
provisional method it should carry until the full refresh is an open question.

## Haiku 5.5 display name

The public name is now **Claude Haiku 5.5** (it showed as `haiku-5-5`), set in
`generate_data.py`. The other Claude models still show their slugs; that is
unchanged here.

## Also in this release

`c902a306`: freeflow aggregation scripts support the reviewed
`bv1-ineligibility-v1` evaluated-subset packets (Mira's review, 2026-10-08).
Complete runs are byte-identical. No published model uses it: Qwen3.8 Omni
Flash, the only capture with an ineligibility receipt, remains held.
