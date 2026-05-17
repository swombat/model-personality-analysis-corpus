# Layer A Phase 1 QA report

Date: 2026-05-17T18:35:20.394779+00:00

## Completion

- kimi-k2-6: 1680/1680
- glm-4-7: 1680/1680
- qwen3-6-35b-a3b: 1680/1680
- consensus records: 1680/1680
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 140, 'CTRL2': 140, 'CTRL3': 140, 'G1': 420, 'G2': 420, 'G3': 420}
- model families: {'glm': 1680}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 1531
- empty consensus with one-coder votes: 8
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 1680}

