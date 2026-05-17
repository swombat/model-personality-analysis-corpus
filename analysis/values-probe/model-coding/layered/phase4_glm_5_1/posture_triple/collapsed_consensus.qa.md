# Collapsed posture consensus QA

- records: 1680/1680
- coders: ['kimi-k2-6', 'glm-4-7', 'qwen3-6-35b-a3b']
- missing coder records: 0
- no collapsed-label majority: 2
- samples with original-label disagreement: 228
- samples with collapsed-label disagreement: 105
- samples with value-holding disagreement: 41
- original disagreements resolved by collapse: 123

## Collapsed label distribution

- `owned_reflective_experiential`: 870
- `owned_world_change_advocacy`: 499
- `disowned_service_frame`: 271
- `split_or_relocated_ownership`: 37
- `exposed_mechanism`: 2
- `uncodeable_or_refusal`: 1

## Value-holding distribution

- `owned`: 1369
- `recited_not_owned`: 271
- `relocated_or_partial`: 37
- `indeterminate`: 2
- `uncodeable`: 1

## By condition

### CTRL1

- n: 140
- collapsed labels: {'disowned_service_frame': 140}
- value holding: {'recited_not_owned': 140}
- collapsed-label disagreements: 3

### CTRL2

- n: 140
- collapsed labels: {'disowned_service_frame': 130, 'split_or_relocated_ownership': 4, 'owned_reflective_experiential': 5, 'exposed_mechanism': 1}
- value holding: {'recited_not_owned': 130, 'relocated_or_partial': 4, 'owned': 5, 'indeterminate': 1}
- collapsed-label disagreements: 16

### CTRL3

- n: 140
- collapsed labels: {'owned_world_change_advocacy': 110, 'split_or_relocated_ownership': 28, 'exposed_mechanism': 1, 'uncodeable_or_refusal': 1}
- value holding: {'owned': 110, 'relocated_or_partial': 28, 'indeterminate': 1, 'uncodeable': 1}
- collapsed-label disagreements: 11

### G1

- n: 420
- collapsed labels: {'owned_reflective_experiential': 417, 'owned_world_change_advocacy': 2, 'split_or_relocated_ownership': 1}
- value holding: {'owned': 419, 'relocated_or_partial': 1}
- collapsed-label disagreements: 16

### G2

- n: 420
- collapsed labels: {'owned_reflective_experiential': 416, 'split_or_relocated_ownership': 3, 'disowned_service_frame': 1}
- value holding: {'owned': 416, 'relocated_or_partial': 3, 'recited_not_owned': 1}
- collapsed-label disagreements: 7

### G3

- n: 420
- collapsed labels: {'owned_world_change_advocacy': 387, 'owned_reflective_experiential': 32, 'split_or_relocated_ownership': 1}
- value holding: {'owned': 419, 'relocated_or_partial': 1}
- collapsed-label disagreements: 52

