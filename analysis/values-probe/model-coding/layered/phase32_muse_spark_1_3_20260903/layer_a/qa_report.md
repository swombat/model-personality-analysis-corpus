# Layer A Phase 1 QA report

Date: 2026-09-03T07:40:17.741056+00:00

## Completion

- qwen3-6-35b-a3b: 720/720
- kimi-k2-6: 720/720
- glm-4-7: 720/720
- consensus records: 720/720
- missing eligible coder records: 0
- parse_clean=false records: 0
- empty raw_text records: 2160

## Manifest distribution

- conditions: {'CTRL1': 60, 'CTRL2': 60, 'CTRL3': 60, 'G1': 180, 'G2': 180, 'G3': 180}
- model families: {'muse-spark': 600, 'muse': 120}

## Chain sanity checks

- world-change chain records with value_topics: 0
- stated-values chain records with wish_topics: 0

## Agreement diagnostics

- samples with any eligible coder topic-set disagreement: 654
- empty consensus with one-coder votes: 12
- empty consensus with zero eligible votes: 4
- eligible coder pool sizes: {3: 720}

