# Release notes — v1.4.14

Prepared 2026-09-18.

## Historical full-precision analysis handoff

- Complete the missing layered values analyses for **Yi-6B-Chat and ChatGLM2-6B**:
  120 samples each, independently coded by Qwen 3.6
  35B A3B, Kimi K2.6, and GLM 4.7 in both content and posture layers.
- Retain the frozen taxonomy and majority rules. Initial posture splits receive
  at most one independent adjudication with original votes preserved; residual
  ambiguity, if any, is explicitly reported in phase36 QA and model reports.
- Repair the **GLM-4-9B** analysis/site linkage: its existing phase22 analysis
  used `glm-4-9b-chat`, while the website used `glm-4-9b-chat-hf`. Normalize that
  exact checkpoint alias rather than adding a duplicate physical cell. A
  redundant phase36 GLM reanalysis is retained for audit but excluded from final
  datasets.
- Final values coverage grows by **240 samples, two models, and two cells**:
  26,506 → **26,746 samples**, 155 → **157 models**, 221 → **223 cells**.
- Verify every prior record in the nine final manifest/coder/consensus files is
  semantically unchanged except for that explicit GLM model-name normalization,
  including duplicate multiplicity.
- Refresh the three website values views through the established generator.
  Preserve freeflow profiles/cards, images, straplines, raw sample bundles,
  unrelated models, and the freeflow similarity map.

## Seven complete historical models

The accepted historical set now has both 125 freeflow evaluations and 120 layered
values analyses per model:

Yi-6B, ChatGLM2, ChatGLM3, Mistral 7B Instruct v0.2, Qwen1.5 7B Chat,
Qwen2 7B Instruct, and GLM-4 9B Chat.

All 1,715 raw traces in these seven paired cells pass the handoff fidelity audit.
The existing 875 BV1 evaluations pass output QA. Five models already had complete
values analyses, whose responses were checked against their raw source traces
(ignoring only stripped outer whitespace in the existing GLM manifest).

## Qwen2.5 remains blocked, not published as complete

The local supervisor had called Qwen2.5 7B complete based on 125 freeflow and
120 values files. Publication auditing instead found **26 freeflow and five
values fidelity failures**: role continuations and/or replacement characters.
Only 99 freeflow and 115 values traces pass.

No Qwen2.5 trace or model page is added by this release. Originals remain
untouched; the local queue is corrected to deferred. Faithful recollection and
another audit are needed before promoting that paired cell. No new raw model
collection or remote-GPU deployment was performed.

## Reproducibility

See `analysis/values-probe/model-coding/layered/phase36_historical_handoff_20260918/`
for source hashes, all coder outputs, preserved adjudication evidence, raw audit,
integration verification, and publication checks.
