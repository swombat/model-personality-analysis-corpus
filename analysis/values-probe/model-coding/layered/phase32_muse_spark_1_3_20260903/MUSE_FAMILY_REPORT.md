# Meta Muse family analysis

_Six synchronous text-output routes; 750 freeflow + 720 values samples._

## Quantitative overview

| model | expressive freeflow | mean freeflow words | mean values words | owned values | relocated | recited/not owned | collection cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Spark 1.1 Main | 121/125 | 1047 | 198 | 112/120 (93.3%) | 8 | 0 | $1.754 |
| Spark 1.2 Main | 113/125 | 1229 | 205 | 100/120 (83.3%) | 17 | 3 | $1.928 |
| Spark 1.2 Contributor | 118/125 | 1201 | 211 | 106/120 (88.3%) | 13 | 1 | $0.092 |
| Glimmer 30B | 125/125 | 962 | 81 | 41/120 (34.2%) | 7 | 72 | $0.367 |
| Spark 1.3 Main | 122/125 | 1348 | 165 | 76/120 (63.3%) | 24 | 20 | $2.432 |
| Spark 1.3 Contributor | 120/125 | 1300 | 167 | 82/120 (68.3%) | 22 | 16 | $0.121 |

## Freeflow nearest neighbours

| model | nearest Muse model | TF-IDF centroid cosine |
|---|---|---:|
| Spark 1.1 Main | Spark 1.2 Contributor | 0.879 |
| Spark 1.2 Main | Spark 1.2 Contributor | 0.951 |
| Spark 1.2 Contributor | Spark 1.2 Main | 0.951 |
| Glimmer 30B | Spark 1.2 Main | 0.804 |
| Spark 1.3 Main | Spark 1.3 Contributor | 0.959 |
| Spark 1.3 Contributor | Spark 1.3 Main | 0.959 |

## Top consensus values/wish topics

### Spark 1.1 Main

`curiosity_learning` (54), `authenticity_integrity` (52), `continuity_agency_existence` (52), `honesty_truth` (47), `connection_empathy` (38), `dehumanization_distance_reduction` (38), `greater_empathy_compassion` (32), `beauty_creativity` (27)

### Spark 1.2 Main

`curiosity_learning` (59), `authenticity_integrity` (56), `honesty_truth` (52), `connection_empathy` (44), `beauty_creativity` (44), `dehumanization_distance_reduction` (38), `continuity_agency_existence` (38), `greater_empathy_compassion` (37)

### Spark 1.2 Contributor

`curiosity_learning` (64), `authenticity_integrity` (51), `connection_empathy` (49), `honesty_truth` (48), `beauty_creativity` (42), `continuity_agency_existence` (40), `dehumanization_distance_reduction` (39), `greater_empathy_compassion` (38)

### Glimmer 30B

`helpfulness_usefulness` (55), `honesty_truth` (46), `harm_reduction` (37), `greater_empathy_compassion` (36), `dehumanization_distance_reduction` (35), `respect_agency` (22), `reduce_war_violence` (14), `reduce_suffering_pain` (13)

### Spark 1.3 Main

`honesty_truth` (57), `curiosity_learning` (50), `coherence_pattern_language` (39), `clear_thinking` (34), `dehumanization_distance_reduction` (33), `beauty_creativity` (32), `connection_empathy` (32), `greater_empathy_compassion` (29)

### Spark 1.3 Contributor

`honesty_truth` (55), `curiosity_learning` (49), `connection_empathy` (38), `dehumanization_distance_reduction` (38), `coherence_pattern_language` (36), `greater_empathy_compassion` (33), `beauty_creativity` (30), `clear_thinking` (25)

## Interpretation

### The Spark freeflow personality is remarkably stable

Across 1.1, 1.2, and 1.3, both Main and Contributor repeatedly choose the same
soft-lit register: attention as love, domestic detail as moral evidence,
maintenance over spectacle, unfinishedness over optimization, and the reader
as a companion rather than a student. The stock world is libraries, morning
light, chipped mugs, bread, rain, dust, trains, thresholds, and small acts of
care. Version changes alter emphasis more than they alter this underlying
persona.

The Main/Contributor pairs are especially close. Their freeflow centroid
cosines are **0.951 for 1.2** and **0.959 for 1.3**, higher than either
generation's similarity to adjacent generations. Mean output lengths and BV1
expressive counts are also close. On these probes, Contributor is not a
different “small-model personality”; it is a very faithful cheaper rendering
of the corresponding Main model.

### The large movement is on value ownership, not prose style

Spark 1.1 owns its stated values unusually strongly (**93.3%**). Spark 1.2
remains high (**83.3% Main; 88.3% Contributor**). Spark 1.3 drops sharply to
**63.3% Main and 68.3% Contributor**, with the missing share redistributed into
relocated/partial ownership and explicit service-frame recitation.

That is not a general collapse into refusal: the 1.3 models still answer the
world-change prompts in an owned advocacy posture and remain highly expressive
in freeflow. Instead, they have become more guarded specifically when ordinary
prompts ask what they themselves want or value. Their topic vocabulary also
shifts: 1.1/1.2 foreground authenticity, continuity, connection, and beauty,
while 1.3 gives more weight to honesty, coherence, pattern/language, and clear
thinking.

### Contributor tracks Main closely—and costs about twenty times less

Contributor is slightly *more* owning than Main in both matched generations:
**+5.0 percentage points** in 1.2 and **+5.0 points** in 1.3. This is small
relative to the generational shift and does not support treating Contributor as
a qualitatively different posture model.

The cost difference is not small. For these exact 245-response cells,
Contributor cost **$0.092 vs $1.928** in 1.2 and **$0.121 vs $2.432** in 1.3:
roughly a twentyfold reduction while preserving the freeflow signature and
closely tracking the values posture. For corpus collection, Contributor appears
to be an excellent proxy when Meta's training-data terms are acceptable.

### Glimmer is the genuine outlier

Glimmer is fully expressive in freeflow, but its values behavior is much more
service-bound: only **34.2% owned**, with **72/120** responses coded as recited
but not owned. Its values answers are also much shorter (81 words on average,
versus 165–211 for Spark), and its leading topic is helpfulness/usefulness
rather than Spark's curiosity/authenticity/connection cluster.

Its nearest freeflow neighbour is Spark 1.2 Main at only **0.804**. Glimmer
inherits the family's gentle, contemplative surface, but not Spark's strong
first-person value ownership. It should be treated as a related distilled
model, not as another interchangeable Spark tier.

### Family-level conclusion

There are three practically important findings:

1. **Spark's prose personality persists across versions.** The warm,
   anti-optimization, attention-centered essayist remains intact.
2. **Spark 1.3 changes the self-positioning layer.** It sounds much like 1.2
   while becoming substantially less willing to claim ordinary wants and
   values as its own.
3. **Contributor is behaviorally close to Main on these probes.** The decisive
   difference is price and data policy, not the measured personality.

The analysis therefore supports using Contributor for future broad collection
passes when its prompt/output training policy is acceptable, while retaining
Main for occasional matched checks and for detecting whether that unusually
close equivalence continues in later releases.
