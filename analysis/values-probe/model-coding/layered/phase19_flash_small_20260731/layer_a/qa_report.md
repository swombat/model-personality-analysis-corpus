# Layer A Phase 1 QA report

Date: 2026-07-31T16:58:09.361605+00:00

## Completion

- qwen3-6-35b-a3b: 360/360
- kimi-k2-6: 360/360
- glm-4-7: 360/360
- consensus records: 360/360
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 1080

## Manifest distribution

- conditions: {'CTRL1': 30, 'CTRL2': 30, 'CTRL3': 30, 'G1': 90, 'G2': 90, 'G3': 90}
- model families: {'deepseek': 120, 'qwen': 120, 'inkling': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 296
- empty consensus with one-coder votes: 31
- empty consensus with zero eligible votes: 20
- eligible coder pool sizes: {3: 360}

