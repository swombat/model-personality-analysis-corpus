# Model straplines — method & runbook

Every model on the site carries a **strapline**: a 5–10-word line that is the
single most compressed portrait of that model's freeflow personality. It is the
first thing a reader sees on the index card and the model page.

The bar is high and specific: **you should be able to tell *who the model is*
from the strapline alone.** Not "here is a vivid thing it once wrote" — *here
is the sensibility*. This doc is the durable method so every new model gets a
consistently good strapline without re-deriving the technique (and without
repeating the 2026-05-17 mistake, documented at the bottom).

Sibling doc: `MODEL_CARD_IMAGES.md` (the banner images).

## The formula (reverse-engineered from the straplines that worked)

**Posture first. Personality is the subject. One vivid clause colours it.**

The straplines that landed all have the same shape: they name or sketch a
*recognizable character*, then let one concrete image or aphorism give it
texture. Look at the ones that worked:

- `opus-4-7` — "Anti-grandiose; trusts noticing over performance, uncertainty
  as honesty" → *trait + what it values*
- `gpt-4o` — "Benevolent harmonizer; tension smoothed into symphony and
  stewardship" → *archetype + its move*
- `grok-4-3` — "Cosmic explainer who keeps small disobediences in his pocket"
  → *a character you can picture*
- `kimi-k2-6` — "We are always in the hallway; reverent of intervals" → *its
  worldview as one sentence*
- `opus-4-6` — "The draft folder is heavier than the sent folder" → *a single
  aphorism that **is** the personality* (the formula at its best)
- `opus-3` — "Declines the blank page; earnest once given a role" → *its exact
  behavioural signature*

Shape: **`[who it is] ; [the thing that proves it]`**. The "who" can be an
archetype noun (harmonizer, explainer, companion, archivist, elegist), a
named stance (anti-grandiose, declines the blank page), or a worldview stated
as the model would state it. The second clause is *seasoning* — it must serve
the character, never replace it.

A strapline fails when it is **detail-first**: a striking concrete with no
subject ("A parrot kettle that squeals in D major" — whose? what sensibility?).
Vivid but anonymous. That is a soundbite, not a portrait.

## Where the personality comes from: the CARD

The personality **card**
(`analysis/freeflow/personality-model-cards/cards/<model-id>.md`) is itself a
character description — it is written precisely to say *who this model is*.
**That is your primary source.** Read it and distil the load-bearing posture:
the archetype, the stance, the one conviction it keeps returning to. The
card's first paragraph is usually the whole "who" in prose; your job is to
compress it without losing the person.

It does **not** matter if the final strapline's words don't appear verbatim in
the card. "Benevolent harmonizer" is an interpretation of the card, not a
quote, and it works. Faithfulness is to the *sensibility*, not to the text.
(Confirmed by Daniel, 2026-05-17: "keep the originals, even if they're not
really found directly in the personality cards — it doesn't matter.")

## Where samples come in: sparingly, as seasoning

The raw freeflow samples (`website/public/data/samples/<site-slug>.json` →
`samples[].result`) are useful for *one* thing: when the card-derived posture
needs a sharper, truer colouring clause and you want the model's own texture
rather than an invented one. Read a spread (~12 across conditions) only to
*confirm* a recurring image you might use in the second clause.

Samples are **not** the source of the personality and must never drive the
line on their own. The historical failure mode (twice on 2026-05-17): going to
the samples for a vivid concrete and letting it *become* the strapline,
producing anonymous soundbites. Card for the who; samples, maybe, for the
colour. If in doubt, the card-only line in the working register beats the
sample-rich line that lost the person.

## The hard constraints (enforced by `validate_strapline`)

In `website/scripts/generate_data.py` → `validate_strapline()`:

- **5–10 words** inclusive. Word = regex `[A-Za-z0-9]+(?:[-’'][A-Za-z0-9]+)?`
  — hyphenated/apostrophe'd compounds count as **one** (`five-year-old`,
  `I'm`). Punctuation and bare numbers split tokens: avoid literal `3:17` /
  `2,500` (fractures the count and reads badly).
- **No meta words**: `based on`, `samples`, `route/provider`, `route`,
  `variants`, `models`.
- Semicolons, quotes, em-dashes inside the line are fine and encouraged
  (`[who]; [proof]`).

Validate after editing:

```bash
cd website && python3 -c "import json,sys; sys.path.insert(0,'scripts'); \
import generate_data as g; \
[g.validate_strapline(k,v) for k,v in json.load(open('src/generated/model-summaries.json')).items()]; \
print('all straplines valid')"
```

`model-summaries.json` is `{ "<site-slug>": "<strapline>" }`; site slug = the
`model` value in `models.json`. A missing slug is a hard `KeyError` at build.

## Adding a strapline for a NEW model

1. Confirm the site slug in `website/src/generated/models.json`.
2. Read the **card**. Write the "who" in one phrase (archetype / stance /
   worldview). That is 80% of the strapline.
3. Add a colouring clause: the conviction or one concrete that proves the who.
   Use a sample-confirmed image only if it's genuinely sharper than a
   card-derived one.
4. Sanity check: *read your line cold — can you tell who this model is?* If it
   reads as a nice line about no one in particular, it failed; go back to the
   card.
5. Check siblings in `model-summaries.json` — versions of one family converge;
   the "who" must differentiate (don't reuse archetype nouns: one archivist,
   one harmonizer, one elegist).
6. Validate, get a human review (straplines are editorial), then
   `cd website && python3 scripts/generate_data.py && npm run build`, commit,
   push.

## Drift sweep after a corpus refresh

A refresh rewrites the cards (and tends to *genericise* them). Straplines are
**not** auto-regenerated and, importantly, **a good existing strapline does not
need replacing just because the refreshed card got blander.** Default to
keeping originals. Only rewrite when the card's refresh reveals the *posture
itself* moved (not merely that a concrete detail eroded). Present any proposed
change for human review; never silently overwrite. When unsure, keep.

## What went wrong on 2026-05-17 (so it isn't repeated)

There was no recorded strapline method; the good originals had been
hand-authored across iterative commits. Reconstructing the method after a
catch about an off-substrate detail ("peaches"), I over-corrected into
*detail-first*: discard the card, mine samples for vivid concretes. Result: 54
technically-vivid lines that had lost the personalities — "random soundbites,
can't tell who the model is" (Daniel). The fix: the card is the character
source; posture leads; samples season; the originals were already right and
should mostly be left alone. The lesson is general: when reconstructing a lost
method, recover it from *the artifacts that worked*, not from the most recent
correction.

## Notes

- Editorial, not generated. Resist scripting it — the value is exactly the
  part a generator flattens. Keep the *method* repeatable; keep the *judgement*
  human-in-the-loop.
- House voice: a recognizable person in 5–10 words; concrete over abstract in
  the colouring clause; the model's sensibility over our cleverness; slightly
  wry is welcome; never an anonymous soundbite.
- Last review: 2026-05-17 — originals kept; `opus-3` sharpened to "Declines
  the blank page; earnest once given a role"; the 8 new flash/gemma models
  authored posture-first from their cards.
