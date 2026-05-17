# Layer A replacement-coder test report

Date: 2026-05-17

## Problem

The initial 300-sample Layer A pilot used DeepSeek v4 pro + Kimi K2.6 + GLM 4.7, with family-exclusion and ≥2 consensus. That completed nominally, but DeepSeek produced 10 parse failures / empty outputs, and family-exclusion meant GLM/Kimi/DeepSeek subject samples often had only 2 eligible coders. With a pool of 2, the ≥2 rule becomes unanimity, so one failure or disagreement silently nulls the sample.

Daniel's direction: do **not** expand to four coders for the trial. Instead, drop DeepSeek, allow self/family coding, and test a cheap/smart replacement.

## Tested replacements

Edge set: 21 samples, consisting of DeepSeek failure IDs, empty-consensus IDs, and representative sanity checks.

- `qwen/qwen3.6-35b-a3b`
  - edge test: 21/21 parse-clean
  - full 300 run: 300/300 parse-clean, 0 empty raw responses
  - average topics/sample: 3.25
  - hidden reasoning tokens observed in full run: 45,800 total; still produced valid outputs
  - measured OpenRouter cost for 300: about $0.0695
- `qwen/qwen3.5-35b-a3b`
  - edge test: 21/21 parse-clean
  - not full-run; slightly older candidate, one edge sample returned `CODES: NONE` where other coders found wish topics
- `google/gemini-2.5-flash-lite`
  - edge test: 21/21 parse-clean
  - full 300 run: 300/300 parse-clean, 0 empty raw responses
  - average topics/sample: 3.41
  - hidden reasoning tokens: 0
  - measured OpenRouter cost for 300: about $0.0147
  - however: it disagreed with at least one other coder on all 300 samples and produced more one-coder-only consensus misses, suggesting it may be too broad/noisy for this coding task.
- `minimax/minimax-m2.7`
  - failed with 400 errors under the current OpenRouter request shape; not pursued.

## Recommended replacement

Use **`qwen/qwen3.6-35b-a3b`** as the DeepSeek replacement for this 300-sample pilot and likely for the full Layer A run, unless Daniel prioritizes lowest cost over agreement quality.

Rationale:

- no parse failures on the edge set or full 300;
- no empty raw outputs;
- better apparent agreement behavior than Gemini Flash Lite;
- cheap enough even with observed hidden reasoning cost;
- simple one-line outputs, no DeepSeek-style blank response failures.

## Methodological changes for the pilot v2

- Coders: `kimi-k2-6`, `glm-4-7`, `qwen3-6-35b-a3b`.
- No family/self exclusion: all three coders are eligible for all samples.
- Consensus still requires ≥2 coder support.
- QA now reports parse failures, empty raw outputs, eligible coder pool sizes, and empty consensus records with one-coder votes.

## Current v2 outputs

- Qwen full output: `analysis/values-probe/model-coding/layered/layer_a_code_v2/qwen3-6-35b-a3b.jsonl`
- Kimi/GLM copied from the original clean run into: `analysis/values-probe/model-coding/layered/layer_a_code_v2/`
- v2 consensus: `analysis/values-probe/model-coding/layered/layer_a_code_v2/consensus_300.jsonl`
- v2 QA: `analysis/values-probe/model-coding/layered/layer_a_code_v2/qa_report.md`

QA summary for Qwen v2:

- Kimi: 300/300
- GLM: 300/300
- Qwen: 300/300
- parse_clean=false: 0
- empty raw_text: 0
- eligible coder pool sizes: `{3: 300}`
- empty consensus with one-coder votes: 2
- empty consensus with zero eligible votes: 0

The remaining two one-coder-only empty consensus cases are now explicit QA items, not silent failures.
