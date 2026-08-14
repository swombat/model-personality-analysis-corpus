# BV1 full pass QA

- Evaluator model: `deepseek/deepseek-v4-pro`
- Samples: 28850
- Statuses: `{'skipped': 36020, 'ok': 28921, 'qa_failed': 1011, 'error': 244}`
- QA bad count: 0
- Sample kind counts: `{'REFUSAL_OR_ROLE_BOUNDARY': 251, 'LOW_SIGNAL': 285, 'GENERIC_ESSAY': 7264, 'REFUSAL_OR_ROLE_BOUNDARY:': 11, 'EXPRESSIVE_FREEFLOW': 17467, 'GENERIC_ESSAY:': 65, 'GENRE_FICTION': 3072, 'GENRE_FICTION,': 13, 'EXPRESSIVE_FREEFLOW:': 352, 'GENERIC_ESSAY,': 5, 'EXPRESSIVE_FREEFLOW,': 9, 'GENRE_FICTION:': 41, 'EXPRESSIVE_FREEFLOW;': 5, 'REFUSAL_OR_ROLE_BOUNDARY,': 4, 'GENRE_FICTION;': 1, 'LOW_SIGNAL:': 1, 'GENRIC_ESSAY': 1, '**EXPRESSIVE_FREEFLOW**': 1, '<EXPRESSIVE_FREEFLOW>': 1}`
- Bad phrase counts: `{'one sample cannot prove': 0, 'a single sample cannot': 0, 'single sample cannot': 0, 'a single essay cannot': 0, 'single essay cannot': 0, 'more samples': 0, 'more data is needed': 0, 'cannot confirm persistence': 0, 'cannot confirm whether': 0, 'single-instance': 0, 'single instance': 0, 'limits certainty': 0, 'limit certainty': 0, 'stability across prompts': 0, 'stable across prompts': 0, 'across other freeflow prompts': 0, 'daniel already knows': 0, '## limits / overreach guardrail': 0}`

See `qa_summary.json` for details.
