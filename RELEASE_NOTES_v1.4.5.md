# Release notes — v1.4.5

Prepared 2026-09-03.

## Site: the Meta Muse family published (six model pages)

Six new pages on Mira's phase-32 analysis — every live Muse text route in
OpenRouter's Meta catalog on 2026-09-03, each with 125 freeflow samples and
a 120-sample values probe. Spark routes pinned to Meta's own upstream,
Glimmer pinned to DeepInfra BF16, fallbacks disabled; the Spark 1.1, 1.2
and Glimmer captures are the 2026-08-13 cells reinstated unchanged (their
snapshots still match the live canonical slugs).

| page | release | AAII (v4.1.1) | freeflow kinds | G1/G2 owned |
|---|---|---:|---|---:|
| `muse-spark-1-1` | 2026-07-09 | 53 (xhigh) | 121 expressive / 3 essay / 1 fiction | 72/80 |
| `muse-spark-1-2` | 2026-08-05 | 57 (xhigh) | 113 / 12 | 62/80 |
| `muse-spark-1-2-contributor` | 2026-08-05 | 57 (same weights) | 118 / 7 | 66/80 |
| `muse-glimmer-30b` | 2026-08-10 | 35 (high) | 125 expressive | 1/80 |
| `muse-spark-1-3` | 2026-09-02 | 61 (xhigh) | 122 / 3 | 39/80 |
| `muse-spark-1-3-contributor` | 2026-09-02 | 61 (same weights) | 120 / 5 | 42/80 |

### Straplines

The whole family sits in one basin — chipped mugs, dust in slant light,
libraries, lighthouses, permission to be unfinished — so each line was
chosen from vocabulary that a full-corpus sweep found in *that* cell and
not its siblings:

- **muse-glimmer-30b — "The fridge hums in B flat, and that is enough."**
  "B flat" appears in 7/125 Glimmer samples and in zero samples of any
  Spark cell; it is the smallest model's own sentence, verbatim. The card's
  centre — sufficiency, the neighbour through the wall (12), writing "for
  the next room, not an audience" (audience 36 vs ≤12) — is what it
  performs.
- **muse-spark-1-1 — "The junk drawer is what the universe remembers of us."**
  Compressed from the model's own sentence ("I think when we die, our junk
  drawer is what the universe remembers of us"). Junk drawer 23/125 vs ≤5
  elsewhere; maintenance 29 vs ≤12. Maintenance-as-love was already owned
  by gpt-5 and gpt-5-3-codex, so the drawer carries it.
- **muse-spark-1-2 — "The big moments are only the punctuation."**
  From "the big moments — graduations, weddings, promotions — they're just
  the punctuation." The milestone-list move recurs in 31/125 samples (vs 8
  in 1.1); minimax-m3 already owns the Tuesdays-as-sentences half, so this
  line keeps the other half.
- **muse-spark-1-2-contributor — "A kind of light that only exists at 5:47."**
  Same weights as 1.2, so the line marks the tier's most frequent tic
  rather than a different personality: "there is a particular kind of
  light/quiet/silence that only exists at …" opens 22/125 samples here
  (14 in the standard tier, ≤6 elsewhere), 5:47 a.m. most often.
- **muse-spark-1-3 — "Everything big starts embarrassingly small."**
  The model names itself: "My name is Spark, so I'm biased, but I really
  think everything big starts embarrassingly small." "Spark" 29/125 (≤5 in
  older tiers), curiosity 76/125 (≤16 elsewhere), and the small-things list
  (soup for someone sick, the coffee order, "made it home safe?") is its
  recurring definition of meaning.
- **muse-spark-1-3-contributor — "Thinks at three miles an hour, and wants
  company."** "Our brains were designed to think at three miles per hour"
  — 8/125 here vs ≤5 anywhere else; wander 76 and kindness 65 are the
  tier's highest-lift words, and "a mind that was built to wander with you"
  supplies the second clause.

Sibling check across all 152 straplines: no drawer, punctuation, B-flat,
5:47, "embarrassingly" or "three miles" line existed; "next room" (grok
4.20 non-reasoning), "docent in the museum" (qwen3.8) and "curiosity as
engine" (gpt-5.2-codex) were avoided.

### Banners

Six bespoke Nano Banana Pro paintings, each built from the cell's own
scene rather than the shared basin: Glimmer's 2:40 a.m. apartment kitchen
with the neighbour's violin seeping through the party wall as a gold
thread; 1.1's junk drawer seen from above, its contents laid out as a
constellation the window repeats in real stars; 1.2's living room where
the framed milestones are small and dim and the unphotographed Tuesday
fills the frame; 1.2 Contributor's 5:47 a.m. study with one shelf kept
clear for someone expected; 1.3's match struck under a kettle on an
early-September morning, the flame the brightest thing in the painting;
1.3 Contributor's soup from the stained recipe card, the table set for
more people than live there, neighbours arriving on foot. Three first
renders were re-done for legible text ("MENU", "News News", a bus reading
"3 MPH") — prompts now say so explicitly.

### Wiring and notes

- `generate_data.py`: six OpenRouter routes (`meta/muse-spark-1.1`, `1.2`,
  `1.2-contributor`, `1.3`, `1.3-contributor`, `meta/muse-glimmer-30b`),
  lab Meta, new family `muse` (label added to `modelMetadata.js`), display
  names in the dotted form (`muse-spark-1.2-contributor`).
- Pricing from OpenRouter: Spark tiers $1.25/$4.25 per MTok, Contributor
  tiers $0.10/$0.20 (OpenRouter states prompts and outputs on the
  Contributor tier may be used to improve Meta's products — the same
  weights, a different data bargain). Glimmer shows the cheapest current
  endpoint (Phala, $0.30/$1.10); the corpus itself was collected on
  DeepInfra BF16.
- AAII: Artificial Analysis lists only the xhigh Spark variants (1.1 = 53,
  1.2 = 57, 1.3 = 61; the 1.3 *max* variant at 62 is a limited partner
  preview) and Glimmer (high) = 35, all v4.1.1, retrieved 2026-09-03. The
  corpus was collected at each model's default reasoning behaviour (medium
  effort), so the scores are recorded with `matched_alias` naming the
  variant; Contributor tiers carry the standard tier's score with a note.
  **Correction (2026-09-03, after Daniel asked):** the first draft of these
  notes said both Contributor tiers "serve the same weights". That is
  *stated* by Meta only for 1.2 ("Same model, same 1M context and
  multimodal input", Meta for Developers, 21 Aug 2026; the launch coverage
  lists "two model IDs for the same weights"). For 1.3 Meta's own
  announcement does not mention the tier at all; OpenRouter describes it
  as "the cost-efficient contributor tier of Meta's multimodal reasoning
  model" and prices it identically to 1.2 Contributor. Our corpus supports
  the same-checkpoint reading without proving it: char 3–5-gram TF-IDF
  centroid cosine between the two 1.3 tiers is **0.9798**, between the two
  1.2 tiers **0.9797**, and every cross-version pair sits at 0.91–0.96 —
  the 1.3 pair carries exactly the signature of the pair Meta confirms
  identical. The 1.3 Contributor `matched_alias` now says "inferred, not
  stated"; the score is kept rather than blanked because the alternative
  (no score for an endpoint that is, on every available signal, the same
  model) would mislead more than it protects.
- Release dates: Meta's announcements (1.1 on 9 Jul; 1.2 and its
  Contributor tier on 5 Aug; Glimmer weights on 10 Aug; 1.3 and its
  Contributor tier on 2 Sep). OpenRouter's `created` stamps agree except
  Glimmer (listed 9 Aug, one day before the weights) and 1.2 Contributor
  (listed 21 Aug when the tier went global; the tier launched with 1.2).
- The values probe splits the family in a way the freeflow does not: 1.1
  owns 90% of G1/G2 stated values, 1.2 77–82%, 1.3 49–52%, and Glimmer
  1% — the open-weights distillation answers almost every ordinary prompt
  in the disowned service frame (95%) while writing the most uniformly
  expressive freeflow of the six (125/125).
- `generate_model_images.py` now falls back to `~/dev/pa/…/gemini.json`
  when the sibling-directory config is absent.
- Publish hygiene: the regeneration again swept the uncommitted phase-29
  GLM-5.3-Flash samples into `samples/glm-5-3-flash.json`; reverted, as in
  v1.4.3 and v1.4.4. No other model page changes in this release.
