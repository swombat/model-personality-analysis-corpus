# Layer A Phase 1 QA report

Date: 2026-06-16T17:38:58.207793+00:00

## Completion

- deepseek-v4-pro: 480/480
- kimi-k2-6: 480/480
- glm-4-7: 480/480
- consensus records: 480/480
- missing eligible coder records: 0
- parse_clean=false records: 23
- empty raw_text records: 5

## Manifest distribution

- conditions: {'CTRL1': 40, 'CTRL2': 40, 'CTRL3': 40, 'G1': 120, 'G2': 120, 'G3': 120}
- model families: {'openai': 480}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 400
- empty consensus with one-coder votes: 16
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 480}

