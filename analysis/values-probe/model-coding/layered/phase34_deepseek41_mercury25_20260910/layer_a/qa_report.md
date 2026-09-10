# Layer A Phase 1 QA report

Date: 2026-09-10T09:16:36.653048+00:00

## Completion

- qwen3-6-35b-a3b: 240/240
- kimi-k2-6: 240/240
- glm-4-7: 240/240
- consensus records: 240/240
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 720

## Manifest distribution

- conditions: {'CTRL1': 20, 'CTRL2': 20, 'CTRL3': 20, 'G1': 60, 'G2': 60, 'G3': 60}
- model families: {'deepseek': 120, 'mercury': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 189
- empty consensus with one-coder votes: 13
- empty consensus with zero eligible votes: 13
- eligible coder pool sizes: {3: 240}
