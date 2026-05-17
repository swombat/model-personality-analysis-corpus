# Layer A Phase 1 QA report

Date: 2026-05-17T17:02:55.509913+00:00

## Completion

- kimi-k2-6: 300/300
- glm-4-7: 300/300
- qwen3-6-35b-a3b: 300/300
- consensus records: 300/300
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 50, 'CTRL2': 50, 'CTRL3': 50, 'G2': 50, 'G3': 50, 'G1': 50}
- model families: {'anthropic': 31, 'deepseek': 36, 'google': 29, 'openai': 38, 'kimi': 30, 'glm': 77, 'grok': 24, 'minimax': 17, 'qwen': 18}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 247
- empty consensus with one-coder votes: 2
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 300}

