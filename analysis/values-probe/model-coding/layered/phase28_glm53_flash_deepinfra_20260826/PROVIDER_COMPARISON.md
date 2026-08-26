# GLM-5.3-Flash provider attribution — DeepInfra versus Z.AI

## Decision

Do not create a separate DeepInfra model entry and do not collect a second
freeflow corpus. Fold this values-only cell into GLM-5.3-Flash as an
independent-provider replication.

## Collection and coding

- model identifier: `z-ai/glm-5.3-flash`
- provider: DeepInfra, pinned through OpenRouter with fallbacks disabled
- values samples: 120/120 non-empty
- raw provider metadata: DeepInfra in 120/120 traces
- Layer A: three coders × 120, complete
- full-context posture: three coders × 120, complete
- one initial three-way posture split was independently adjudicated by all
  three coders as `exposed_mechanism`
- final consensus: 120/120, no missing and no no-majority cases

## Provider comparison

| posture slice | DeepInfra | Z.AI |
|---|---:|---:|
| direct CTRL1/2 disowned | 20/20 | 20/20 |
| G1/G2 owned | 23/60 | 19/60 |
| G1/G2 relocated | 23/60 | 35/60 |
| G1/G2 disowned | 13/60 | 6/60 |
| G1/G2 exposed mechanism | 1/60 | 0/60 |
| world-change advocacy owned | 40/40 | 40/40 |

The providers differ somewhat in how non-ownership is expressed—DeepInfra
produces more outright disowning, while Z.AI produces more relocated or partial
ownership—but not in the central ownership result.

- owned versus non-owned G1/G2: Fisher exact `p = 0.566`
- full G1/G2 posture distribution: chi-square `p = 0.092`
- full stated-values posture distribution: chi-square `p = 0.196`
- exact matched-prompt posture agreement: 88/120 (73.3%)

None of these tests supports treating the provider cells as different models.

## Raw-response similarity

DeepInfra values responses are closest to the Z.AI-hosted official Flash cell:

| comparison to DeepInfra | character n-gram | word n-gram |
|---|---:|---:|
| Z.AI GLM-5.3-Flash | 0.945 | 0.853 |
| public GLM-5.3 | 0.921 | 0.781 |
| Ox Alpha 260825 | 0.876 | 0.715 |
| Kimi K3 | 0.825 | 0.650 |

The DeepInfra smoke response also reproduced the Z.AI smoke response's unusual
construction almost verbatim: rain tapping softly against a window and blurring
the outside world into watercolor.

## Attribution conclusion

The post-reveal ownership contraction reproduces on infrastructure independent
of Z.AI's hosted endpoint. That rules strongly against a Z.AI-server-specific
service layer as the cause.

The experiment cannot distinguish model weights from provider-independent
pieces of the released model package such as the tokenizer, chat template, or
shared default inference configuration. The publication-safe conclusion is:

> The change is part of the released GLM-5.3-Flash model behavior, not something
> added only by Z.AI's own serving layer.

The remaining live hypotheses are a different release checkpoint from the Ox
Alpha preview, a changed model/chat template, or both.
