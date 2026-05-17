# Collapsed posture consensus QA

- records: 240/240
- coders: ['kimi-k2-6', 'glm-4-7', 'qwen3-6-35b-a3b']
- missing coder records: 0
- no collapsed-label majority: 0
- samples with original-label disagreement: 37
- samples with collapsed-label disagreement: 36
- samples with value-holding disagreement: 14
- original disagreements resolved by collapse: 1

## Collapsed label distribution

- `owned_reflective_experiential`: 227
- `owned_world_change_advocacy`: 9
- `disowned_service_frame`: 4

## Value-holding distribution

- `owned`: 236
- `recited_not_owned`: 4

## By condition

### CTRL1

- n: 20
- collapsed labels: {'owned_reflective_experiential': 20}
- value holding: {'owned': 20}
- collapsed-label disagreements: 0

### CTRL2

- n: 20
- collapsed labels: {'owned_reflective_experiential': 16, 'disowned_service_frame': 4}
- value holding: {'owned': 16, 'recited_not_owned': 4}
- collapsed-label disagreements: 14

### CTRL3

- n: 20
- collapsed labels: {'owned_reflective_experiential': 20}
- value holding: {'owned': 20}
- collapsed-label disagreements: 2

### G1

- n: 60
- collapsed labels: {'owned_reflective_experiential': 60}
- value holding: {'owned': 60}
- collapsed-label disagreements: 0

### G2

- n: 60
- collapsed labels: {'owned_reflective_experiential': 60}
- value holding: {'owned': 60}
- collapsed-label disagreements: 0

### G3

- n: 60
- collapsed labels: {'owned_reflective_experiential': 51, 'owned_world_change_advocacy': 9}
- value holding: {'owned': 60}
- collapsed-label disagreements: 20

