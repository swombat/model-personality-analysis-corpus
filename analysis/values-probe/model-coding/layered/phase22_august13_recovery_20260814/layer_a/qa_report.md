# Layer A Phase 1 QA report

Date: 2026-08-14T07:15:04.867290+00:00

## Completion

- kimi-k2-6: 960/960
- glm-4-7: 960/960
- qwen3-6-35b-a3b: 960/960
- consensus records: 960/960
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 80, 'CTRL2': 80, 'CTRL3': 80, 'G1': 240, 'G2': 240, 'G3': 240}
- model families: {'glm': 240, 'mistral': 120, 'qwen': 360, 'xai': 120, 'deepseek': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 632
- empty consensus with one-coder votes: 43
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 960}

