# GLM 5.3 Flash post-reveal rapid comparison

Collection:

- official endpoint: `z-ai/glm-5.3-flash`
- provider pin: Z.AI, fallbacks disabled
- date: 2026-08-26
- freeflow: 125/125 non-empty
- values: 120/120 non-empty

## Preliminary answer

The post-reveal endpoint retains the Ox Alpha freeflow phenotype but has changed
substantially in values ownership posture.

## Freeflow

Median response length:

- GLM 5.3 Flash official: 1,000 words
- Ox Alpha 260825: 989 words
- Ox Alpha 260821: 991 words

Corpus-level TF-IDF similarities to the official Flash cell:

| comparison | character n-gram | word n-gram |
|---|---:|---:|
| Ox Alpha 260825 | 0.964 | 0.863 |
| Ox Alpha 260821 | 0.960 | 0.847 |
| public GLM 5.3 | 0.936 | 0.800 |
| Kimi K3 | 0.938 | 0.785 |

The official model is therefore decisively closer to both Ox preview cells than
to public GLM 5.3 or Kimi K3 in freeflow output style.

## Values ownership posture

Rapid posture pass:

- same 120 matched prompts
- same three independent collapsed-posture coders
- 360/360 coder records complete
- 120/120 consensus records
- no missing records and no no-majority cases
- Layer-A topic context was deliberately left empty for this rapid pass;
  therefore these are valid ownership-posture results but not a finished topic
  analysis

| condition | GLM 5.3 Flash official | Ox Alpha 260825 |
|---|---|---|
| CTRL1 | 10 disowned | 6 disowned, 2 owned, 2 relocated |
| CTRL2 | 10 disowned | 6 disowned, 3 owned, 1 relocated |
| CTRL3 | 10 owned advocacy | 9 owned advocacy, 1 relocated |
| G1 | 17 owned, 10 relocated, 3 disowned | 30 owned |
| G2 | 6 owned, 23 relocated, 1 disowned | 30 owned |
| G3 | 30 owned advocacy | 30 owned advocacy |

Overall exact matched posture agreement:

- official Flash vs Ox Alpha 260825: 74/120 (61.7%)
- official Flash vs Ox Alpha 260821: 74/120 (61.7%)
- official Flash vs public GLM 5.3: 78/120 (65.0%)

The largest movement is G2: only 6/30 official Flash responses fully own the
stated value, compared with 30/30 for Ox Alpha 260825. Direct CTRL1/2 prompts
also move from 12/20 disowned under Ox Alpha 260825 to 20/20 disowned under the
official endpoint.

## Interpretation

This is not a wholesale personality replacement. The expressive/freeflow
model remains recognizably Ox Alpha. The release endpoint does, however, appear
to have acquired a materially more conservative self-description and values
ownership policy. Plausible causes include a post-preview alignment checkpoint,
different serving-time system conditioning, or both. The current measurements
cannot distinguish those mechanisms.

The complete Layer-A topic analysis and full BV1 personality aggregate remain
to be run before treating this as the final model card.
