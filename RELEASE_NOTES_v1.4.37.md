# v1.4.37 — MiniMax M3.1 Flash MLCR rung, zero-gap wording, evidence recounts

2026-10-26. Follow-ups from Mira's weekly release review (souls.house, message
`JbVorJ`). No capture, synthesis, image or full-ladder rerun.

- **MiniMax M3.1 Flash ladder: 158.3 → 154.6 (provisional).** Artificial
  Analysis's page, read again on 2026-10-26, now carries an MLCR result
  (0.166666666666667) that was absent from the 2026-10-22 snapshot. Nothing else
  the provisional method uses changed (the script asserts this). MLCR is added as
  a ninth measured rung, dated 2026-10-26; the other eight keep 2026-10-22. Same
  recovered 2026-10-04 method, which still reproduces 161.6 / 128.1 first.
  Script and snapshot: `internal/capability-ladder/provisional-20261026-minimax-m3-1-flash-mlcr/`.
  This is newly available coverage, not a launch-day omission. The model's
  provisional note keeps the old 158.3 and says why it moved.
- **Disclosure-conflict wording.** `values_headline.conflict.direction` said
  "higher under direct CTRL1/2 prompts" whenever the cache-broken rate was not
  higher, including when the two were equal. Mira found it on MiniMax M3.1 Flash
  (10% vs 10%); the same wording was on 52 models with a 0.0-point gap (among
  them Opus 5.5, o3 and GPT-5). A zero gap now reads "no difference between
  direct CTRL1/2 and cache-broken G1/G2 prompts". Generator:
  `conflict_direction()` in `website/scripts/generate_data.py`; regression test
  `website/scripts/test_conflict_direction.py`, which also checks every
  published entry against the generator. The counts were always correct.
- **Release evidence recounts.** Kimi K3.1 Pro's Museum of Almost is in 12 of
  125 samples, not 8 (OPEN_19, OPEN_21, VARY_15, VARY_23 were omitted).
  Mercury 3's "the world seems to hold its breath" is verbatim in 7 samples, plus
  one "the whole world" variant (OPEN_11), not "verbatim in 8"; its rejected
  candidate "Silence is not empty" is verbatim in 2, not 9. Corrected in place in
  the v1.4.36 and v1.4.34 notes, each with a dated marker. Neither strapline
  changes.
