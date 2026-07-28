# Layer A Phase 1 QA report

Date: 2026-07-28T11:17:03.570141+00:00

## Completion

- kimi-k2-6: 720/720
- glm-4-7: 720/720
- qwen3-6-35b-a3b: 720/720
- consensus records: 720/720
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 0

## Manifest distribution

- conditions: {'CTRL1': 60, 'CTRL2': 60, 'CTRL3': 60, 'G1': 180, 'G2': 180, 'G3': 180}
- model families: {'claude-opus': 240, 'openai-o-series': 480}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 605
- empty consensus with one-coder votes: 86
- empty consensus with zero eligible votes: 0
- eligible coder pool sizes: {3: 720}

