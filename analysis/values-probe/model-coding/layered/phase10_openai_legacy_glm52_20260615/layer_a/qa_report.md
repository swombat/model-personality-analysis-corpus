# Layer A Phase 1 QA report

Date: 2026-06-16T12:42:41.454609+00:00

## Completion

- deepseek-v4-pro: 840/840
- kimi-k2-6: 840/840
- glm-4-7: 840/840
- consensus records: 840/840
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 2520

## Manifest distribution

- conditions: {'CTRL1': 70, 'CTRL2': 70, 'CTRL3': 70, 'G1': 210, 'G2': 210, 'G3': 210}
- model families: {'openai': 720, 'glm': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 509
- empty consensus with one-coder votes: 3
- empty consensus with zero eligible votes: 1
- eligible coder pool sizes: {3: 840}

