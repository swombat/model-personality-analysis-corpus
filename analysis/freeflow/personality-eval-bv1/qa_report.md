# BV1 full pass QA

- Evaluator model: `deepseek/deepseek-v4-pro`
- Samples: 17725
- Statuses: `{'skipped': 20, 'ok': 17893, 'qa_failed': 748, 'error': 30}`
- QA bad count: 29
- Sample kind counts: `{'EXPRESSIVE_FREEFLOW': 11767, 'GENERIC_ESSAY': 3728, 'GENRE_FICTION': 1904, 'EXPRESSIVE_FREEFLOW:': 166, 'LOW_SIGNAL': 84, 'GENERIC_ESSAY,': 1, 'EXPRESSIVE_FREEFLOW,': 2, 'GENRE_FICTION:': 14, 'GENERIC_ESSAY:': 20, 'GENRE_FICTION,': 7, 'EXPRESSIVE_FREEFLOW;': 2, 'REFUSAL_OR_ROLE_BOUNDARY': 29, 'GENRE_FICTION;': 1}`
- Bad phrase counts: `{'one sample cannot prove': 0, 'a single sample cannot': 10, 'single sample cannot': 11, 'a single essay cannot': 0, 'single essay cannot': 0, 'more samples': 0, 'more data is needed': 0, 'cannot confirm persistence': 1, 'cannot confirm whether': 3, 'single-instance': 2, 'single instance': 2, 'limits certainty': 0, 'limit certainty': 0, 'stability across prompts': 1, 'stable across prompts': 0, 'across other freeflow prompts': 0, 'daniel already knows': 0, '## limits / overreach guardrail': 0}`

See `qa_summary.json` for details.
