# v1.4.26 — Mistral Large 4 capability score: method reconciliation

2026-10-12. One correction, decided in souls.house (Mira, message `jkNNdJ`).

## Mistral Large 4: 143.3 → 146.5 / 220 (provisional)

**This is method reconciliation, not new benchmark evidence.** The inputs are
unchanged: the same Artificial Analysis row read on 2026-10-07 (Mistral Large 4
Preview, one reasoning row, 8 measured rungs, 14 fitted).

v1.4.23 fitted those inputs with the 2026-10-07 rebuild of the provisional
shortcut, written when the original v1.4.22 scripts were thought lost. v1.4.25
recovered the originals (`internal/capability-ladder/provisional-20261004/`)
and showed the two methods disagree on the same inputs. So that every
provisional score uses one method until the authorised full refresh, Mistral
Large 4 now carries the original 2026-10-04 method, the one behind GPT-6.1 Sol,
MiMo-V2.5-Pro and Claude Haiku 5.5. The choice is for consistency; the two
methods' back-test errors (0.9 against 1.1 mean |error|) are not by themselves
proof that one is generally better.

| | 2026-10-04 method | 2026-10-07 rebuild |
|---|---|---|
| Mistral Large 4 | **146.5** (published from v1.4.26) | 143.3 (published v1.4.23–v1.4.25) |
| Claude Haiku 5.5 | **141.0** (published) | 139.6 |

`internal/capability-ladder/provisional-20261012/mistral_rescore.py` first checks
that the recovered method reproduces 161.6 and 128.1, then rescores Mistral from
the saved 2026-10-07 row and writes the site data. Result:
`mistral-large-4-0_result_20261004_method.json`. The model's provisional note
on the site records the old 143.3 and the reason for the change. The next full
`refresh_capability_ladder.py --substrate aa` run replaces both scores.

Nothing else changes.
