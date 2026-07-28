# Layer A Phase 1 QA report

Date: 2026-07-28T11:08:15.130546+00:00

## Completion

- kimi-k2-6: 3960/3960
- glm-4-7: 3960/3960
- qwen3-6-35b-a3b: 3960/3960
- consensus records: 3960/3960
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 330, 'CTRL2': 330, 'CTRL3': 330, 'G1': 990, 'G2': 990, 'G3': 990}
- model families: {'gpt': 840, 'grok': 240, 'mistral': 1920, 'llama': 960}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 3304
- empty consensus with one-coder votes: 281
- empty consensus with zero eligible votes: 4
- eligible coder pool sizes: {3: 3960}

