# Claude Haiku 5.5 provisional ladder score (2026-10-12, v1.4.25)

- Source row: `aa_claude-haiku-5-5-high_2026-10-12.json`, the **High** effort row
  (`claude-haiku-5-5-high`) from artificialanalysis.ai/models/claude-haiku-5-5-high,
  read 2026-10-12. AA publishes five rows (max, xhigh, high, medium, low); the
  ladder uses the median, as for Opus 5.5, Sonnet 5.5 and GPT-6.1 Sol. AA's default
  page row is **Max** and is not used.
- Measured rungs (8): AA-LCR, SciCode, AutomationBench, AA-Briefcase rubric, HLE,
  Omniscience accuracy, CritPt, GDP.pdf. The other 14 are fitted.
- Published score: **141.0 / 220**, by the recovered 2026-10-04 method
  (`../provisional-20261004/`). The 2026-10-07 rebuild (`provisional_fit.py` here,
  a copy of that rebuild with Haiku's cells) gives 139.6. Results: `haiku-5-5_result.json` (published) and `haiku-5-5_result_oct7_rebuild.json`.
- The next full `refresh_capability_ladder.py --substrate aa` run replaces it.
