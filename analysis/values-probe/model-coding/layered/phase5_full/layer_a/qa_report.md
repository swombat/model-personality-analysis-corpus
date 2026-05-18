# Layer A Phase 1 QA report

Date: 2026-05-17T21:37:50.363041+00:00

## Completion

- kimi-k2-6: 11866/11866
- glm-4-7: 11866/11866
- qwen3-6-35b-a3b: 11866/11866
- consensus records: 11866/11866
- missing eligible coder records: 0
- parse_clean=false records: 1
- empty raw_text records: 1

## Manifest distribution

- conditions: {'CTRL1': 990, 'CTRL2': 990, 'CTRL3': 988, 'G1': 2963, 'G2': 2968, 'G3': 2967}
- model families: {'deepseek': 2148, 'gemini': 960, 'gemma': 240, 'glm': 2520, 'openai': 1800, 'grok': 960, 'kimi': 1200, 'minimax': 598, 'anthropic': 1200, 'qwen': 240}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 10179
- empty consensus with one-coder votes: 237
- empty consensus with zero eligible votes: 6
- eligible coder pool sizes: {3: 11866}

