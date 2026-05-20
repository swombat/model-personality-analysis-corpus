# Layer A Phase 1 QA report

Date: 2026-05-20T09:46:31.314582+00:00

## Completion

- kimi-k2-6: 11986/11986
- glm-4-7: 11986/11986
- qwen3-6-35b-a3b: 11986/11986
- consensus records: 11986/11986
- missing eligible coder records: 0
- parse_clean=false records: 1
- empty raw_text records: 1

## Manifest distribution

- conditions: {'CTRL1': 1000, 'CTRL2': 1000, 'CTRL3': 998, 'G1': 2993, 'G2': 2998, 'G3': 2997}
- model families: {'deepseek': 2148, 'gemini': 1080, 'gemma': 240, 'glm': 2520, 'openai': 1800, 'grok': 960, 'kimi': 1200, 'minimax': 598, 'anthropic': 1200, 'qwen': 240}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 10292
- empty consensus with one-coder votes: 237
- empty consensus with zero eligible votes: 6
- eligible coder pool sizes: {3: 11986}

