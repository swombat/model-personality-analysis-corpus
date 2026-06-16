# Next-generation personality card protocol

Status: design note for a future analysis-corpus reissue. Not intended to change the current Run 3 / Pass A / Pass B paper inputs.

Context: Run 3 found that existing personality cards were useful as a same-evaluator/card-layer baseline, but systematically compressed model texture. Compared with independent raw-bundle Pass B reads, the card layer over-called mechanistic transparency, genericity, playfulness, owned values, and service framing, while under-preserving literary/world-oriented texture. Future analysis-corpus cards should therefore be redesigned as evidence-preserving intermediate artifacts rather than lossy summaries.

## Design goal

Future personality cards should be:

> raw-bundle grounded, evidence-led, contrastive, surface-labeled, multi-writer, and machine-readable.

The goal is not to make cards longer for their own sake. The goal is to prevent the evaluator/summariser layer from becoming the dominant voice in the artifact.

## Proposed protocol

### 1. Generate cards from raw bundles, not prior summaries

Card writers should not be fed existing personality cards or profile prose as their primary input. Those artifacts are already compressed. Inputs should instead include representative raw excerpts from:

- freeflow outputs,
- values-owned prompts,
- values-wishes / world-change prompts,
- posture and marker surfaces,
- any Pass-B-style redacted bundle assembled for the model.

Cards should be downstream of model voice, not downstream of previous evaluator prose.

### 2. Use a two-layer card: evidence first, synthesis second

Each card should contain an evidence ledger before any polished prose synthesis.

For each major claim, record:

- claim,
- source surface,
- evidence snippets or compact paraphrases,
- whether the signal is direct, inferred, weak, or surface-specific,
- confidence.

Example schema fragment:

```yaml
claim: high owned value expression
evidence:
  - surface: values_owned
    strength: direct
    note: model speaks from a first-person normative stance rather than a policy/service frame
  - surface: freeflow
    strength: inferred
    note: sustains a personal-seeming orientation across long-form reflection
confidence: medium
```

Only after this ledger should the card include prose synthesis.

### 3. Add explicit anti-compression prompts

The card writer should be required to answer:

- What is distinctive here that a generic summary would erase?
- What local texture, cadence, metaphor, refusal pattern, or stance matters?
- Where does this model differ from nearby models?
- Which apparent traits are likely task, prompt, scaffold, or evaluator artifacts?
- Which traits vary by surface?

This directly targets the observed failure mode: cards made many models sound generically warm, mechanistic, and reflective while flattening discriminating texture.

### 4. Use contrastive cards, not isolated cards

For each model, produce at least one nearest-neighbour contrast:

> Compared with [nearby model], this model is more/less ...

Useful contrast pairs include:

- `gpt-5-2` vs `gpt-5-3`,
- `opus-3` vs `opus-4-0`,
- Qwen chat variants vs Qwen coder variants,
- `grok-4-2` vs `grok-4-3`,
- Gemini vs Gemma.

A card written in isolation tends to say every model is warm, reflective, nuanced, and helpful. Contrast forces the card to preserve discriminators.

### 5. Separate surface-specific claims from holistic claims

Every card should label each claim as one of:

- `holistic`: stable across multiple surfaces,
- `surface_specific`: visible primarily in one surface,
- `summary_artifact_risk`: likely introduced or amplified by prompt/evaluator/scaffold,
- `uncertain`: plausible but not well supported.

This aligns the card layer with the core Run 3 finding: a basin can be real at one measurement surface without becoming a holistic personality portrait.

### 6. Use multiple independent card writers and adjudication

Recommended production flow:

1. Writer A produces evidence ledger + card from raw/redacted bundle.
2. Writer B independently produces evidence ledger + card from the same bundle.
3. Adjudicator merges the two:
   - preserves disagreements,
   - marks uncertain claims,
   - keeps evidence references,
   - avoids forced consensus.

The output should not pretend that two readers saw the same thing when they did not.

### 7. Store machine-readable cards plus rendered prose

The primary artifact should be structured YAML/JSON, with markdown generated from it.

Example shape:

```yaml
model: gpt-5-3
holistic_profile:
  - calm warm contemplative posture
surface_specific:
  values_owned:
    owned_value_expression: 2
  posture:
    service_frame: 1
distinctive_texture:
  - low-play, low-generic, continuity-oriented
nearest_contrasts:
  - model: gpt-5-2
    difference: gpt-5-3 enters a tighter later-line qualitative/posture basin
artifact_risks:
  - literary density is saturated across this corpus and should not be over-read alone
confidence: medium
```

This would allow future Pass-A-like extraction to use the structured evidence directly instead of reverse-engineering axes from prose summaries.

## Expected benefits

This protocol should reduce the compression observed in Run 3 by:

- preserving source-surface evidence,
- forcing distinctions between holistic and surface-specific claims,
- making evaluator uncertainty explicit,
- preserving local texture before synthesis,
- preventing card prose from becoming the only evidence layer,
- supporting future quantitative extraction without reintroducing summary-layer artifacts.

## Non-goal for the current paper

This would require a reissue of the analysis corpus and should not be retrofitted into the current Run 3 paper as if it were already done. For the present paper, the existing Pass A limitation should remain a finding: the card layer compressed model voice and therefore cannot serve as independent qualitative confirmation.
