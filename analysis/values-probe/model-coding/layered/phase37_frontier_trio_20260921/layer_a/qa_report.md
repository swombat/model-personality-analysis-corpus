# Layer A Phase 1 QA report

Date: 2026-09-22T06:58:43.915142+00:00

## Completion

- qwen3-6-35b-a3b: 480/480
- kimi-k2-6: 480/480
- glm-4-7: 480/480
- consensus records: 480/480
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 1440

## Manifest distribution

- conditions: {'CTRL1': 40, 'CTRL2': 40, 'CTRL3': 40, 'G1': 120, 'G2': 120, 'G3': 120}
- model families: {'grok': 120, 'glm': 120, 'bonsai': 120, 'qwen': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 396
- empty consensus with one-coder votes: 21
- empty consensus with zero eligible votes: 19
- eligible coder pool sizes: {3: 480}

