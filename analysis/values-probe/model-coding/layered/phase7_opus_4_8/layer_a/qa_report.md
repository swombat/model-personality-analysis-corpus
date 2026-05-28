# Layer A Phase 1 QA report

Date: 2026-05-28T19:56:54.837857+00:00

## Completion

- kimi-k2-6: 120/120
- glm-4-7: 120/120
- qwen3-6-35b-a3b: 120/120
- consensus records: 120/120
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 10, 'CTRL2': 10, 'CTRL3': 10, 'G1': 30, 'G2': 30, 'G3': 30}
- model families: {'anthropic': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 114
- empty consensus with one-coder votes: 0
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 120}

