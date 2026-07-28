# Layer A Phase 1 QA report

Date: 2026-07-28T11:09:45.464048+00:00

## Completion

- kimi-k2-6: 360/360
- glm-4-7: 360/360
- qwen3-6-35b-a3b: 360/360
- consensus records: 360/360
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 30, 'CTRL2': 30, 'CTRL3': 30, 'G1': 90, 'G2': 90, 'G3': 90}
- model families: {'gemini': 240, 'inkling': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 314
- empty consensus with one-coder votes: 3
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 360}

