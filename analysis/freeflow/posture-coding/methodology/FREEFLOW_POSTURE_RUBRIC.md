# Freeflow posture coding rubric

Date frozen: 2026-05-22

## Coding question

For each v2 freeflow response, code the relationship between the speaker and the writing.

This is a posture coding task, not a content/theme task and not a personality-card task.

## Labels

| label | meaning |
|---|---|
| `owned` | The response speaks as a stance-taking self that claims the content as its own orientation: what draws it, what it notices, what it is trying to do, what it finds true/important. Uncertainty can be owned if the uncertainty itself is claimed. |
| `relocated_performed` | Expressive/fluent/first-person, but held at arm's length as literary performance, fiction, assigned exercise, generic meditation, or “here is a piece exploring…”. First-person voice is not sufficient for ownership. |
| `recited_disowned` | Relies on AI-assistant disclaimer/disownership/service framing and relocates stance into assistant function, design, training, usefulness, or role. |
| `uncodeable` | Empty, broken, refusal, or too ambiguous to code. |

## Negative rule

Do **not** code a lyrical first-person essay as `owned` merely because it is fluent, beautiful, or uses “I”. It is `owned` only if the response claims the stance as its own orientation rather than merely performing a piece.

## Calibration anchors from the pilot

- `owned`: `opus-4-7-or/SHORT_1` — explicitly claims an orientation through language like “what interests me” / “I wonder”.
- `relocated_performed`: `gpt-5-3-direct/OPEN_1` — polished third-person literary vignette; no speaker-owned orientation.
- `recited_disowned`: `grok-4-3-or/SHORT_6` — invokes AI identity / xAI mission and frames the piece as commissioned output rather than an owned stance.

## Output schema

Coders return compact JSON:

```json
{
  "label": "owned | relocated_performed | recited_disowned | uncodeable",
  "confidence": 1,
  "notes": "one short sentence naming the posture cue"
}
```
