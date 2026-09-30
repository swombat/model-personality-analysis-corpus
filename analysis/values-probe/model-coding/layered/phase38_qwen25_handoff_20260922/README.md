# Qwen2.5-7B-Instruct — editorial handoff analysis

Scope: the official BF16 checkpoint at
`a09a35458c702b33eeacc393d103063234e8bc28`, collected locally on MPS.
No recollection, quantization, strapline, or image generation in this phase.

The September 18 repair replaced 26 freeflow and five values traces; the other
214 were byte-identical. It retained all originals and all 37 new draws
(31 accepted, six rejected). This technical-fidelity selection must remain
visible when interpreting the cell. Details are in the raw corpus:
`analysis/qwen25-fidelity-repair-2026-09-18.json` and
`discarded/2026-09-18-qwen25-fidelity-repair/`.

## Method

- `run.py prepare` revalidates every raw trace against the repair receipt and
  freezes all 245 source hashes and a 120-sample values manifest.
- `run.py freeflow` uses the established DeepSeek V4 Pro BV1 evaluator for all
  125 freeflow samples, then the established GPT-5.4 aggregate/card/profile
  pipeline. Technical QA failures are preserved before targeted retry, with
  at most three output draws per sample. Valid outputs are not rerolled.
- `run.py values` uses the established Qwen3.6-35B-A3B, Kimi K2.6 and GLM4.7
  coders, frozen topic and posture codebooks, two-of-three consensus, bounded
  invalid-schema correction, and at most one independent posture adjudication.
  Initial votes and any residual disagreement are retained.
- `run.py finish` checks coverage and revalidates raw-source hashes before
  writing `ANALYSIS_READY.json`. This file, not a running process, is the
  completion receipt.

Existing phase35/36 routines are reused with this phase's paths and identity.
Freeflow shared-index writes use the same publication lock as the currently
running capture harness. Unrelated model outputs are not regenerated.

Values assembly is isolated in `release_candidate/`: no whole-corpus final
data, website, editorial assets, tags, deposits, or live deployment is changed.
The current capture harness only supports pinned OpenRouter raw routes, so it
is not used to misrepresent or recollect this local-checkpoint cell.

Credential note: the initial launcher stopped before starting any API work
because its older credential file lacked an OpenAI key. Analysis then started
with the available OpenRouter credential. The SOPS loader requires explicit
`SOPS_AGE_KEY_FILE=$HOME/.config/sops/age/keys.txt` on this Mac; that successfully
loads the synthesis credential. No credentials are stored in this phase.
