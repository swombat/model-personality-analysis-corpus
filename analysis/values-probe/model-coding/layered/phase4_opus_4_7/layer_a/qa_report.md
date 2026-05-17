# Layer A Phase 1 QA report

Date: 2026-05-17T17:39:56.611929+00:00

## Completion

- kimi-k2-6: 240/240
- glm-4-7: 240/240
- qwen3-6-35b-a3b: 240/240
- consensus records: 240/240
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 20, 'CTRL2': 20, 'CTRL3': 20, 'G1': 60, 'G2': 60, 'G3': 60}
- model families: {'anthropic': 240}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 226
- empty consensus with one-coder votes: 1
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 240}

