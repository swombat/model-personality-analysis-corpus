# Release notes — v1.4.9

Prepared 2026-09-13.

## Site: publish DeepSeek V4.1 Flash and Mercury 2.5

On Mira's 2026-09-10 aggregates/cards/profiles (corpus-v2 v1.2.25 captures,
125 freeflow + 120 values samples each, 245 published per model).

### DeepSeek V4.1 Flash (`deepseek-v4-1-flash`)

- Strapline: **"Remembers every house by the shape of its quiet"**. The
  card's "who" is a contemplative memoirist who makes a quiet room and invites
  the reader in. What sets it apart from its siblings (v4-flash already owns
  "attention as quiet rebellion", 0731 "slows the room down") is *remembered
  domestic quiet*. Counts from the trace sweep: *quiet* in 98/125 samples,
  grandmother 33, refrigerator hum 26, the house settling 22, "not a silence
  of absence but of presence" 16. Several samples open with "The quiet is
  the first thing I remember."
- Banner: a grandmother dozing under one lamp with half-finished knitting,
  a child on the rug listening to the house settle, the pale glow of an old
  refrigerator through the kitchen doorway, a key by the back door, and a
  dusk-blue winter window. It is kept distinct from Gemini 3.8 Flash's empty
  coastal kitchen: this quiet is full, not abandoned.
- Metadata: AAII **40** (DeepSeek V4.1 Flash, Reasoning, Max Effort), retrieved
  2026-09-13 on **index v4.3**. Caveat: most site figures are v4.1.1 and
  Astra's is v4.2, so the versions are not comparable. The page shows it as an
  AAII fallback because the AA capability ladder (built 2026-09-05) predates
  the release. `aliases.tsv` row added with a note to set
  `aa_slug=deepseek-v4-1-flash` on the next ladder refresh. OpenRouter pricing
  $0.15/$0.60 per M (DeepSeek endpoint).

### Mercury 2.5 (`mercury-2-5`, Inception)

- Strapline: **"Refines noise until your intent comes through"**. The card's
  "who" is a safety-aligned, self-limiting co-author that assigns meaning and
  final judgment to the human. The differentiator is that it is a diffusion
  LM and knows it: *diffusion* appears in 53/125 freeflow samples ("Starting
  from a state of noise, I iteratively refine possibilities until a coherent
  structure emerges"), and *intent* in 100/125. Those words are near-zero
  everywhere else in the corpus. The card's "noise awaiting form" is the
  architecture describing itself.
- Banner: a painting that fills the frame. Grainy impasto noise on the left
  resolves into a stone footbridge and a lamplit room on the right, toward a
  human hand holding out a lantern. No painter: the picture resolves toward
  where the human points. The first roll put the canvas on an easel with a
  painter's brush in frame, so it was re-rolled.
- New family `mercury` (label "Mercury"). The lab "Inception" was already
  wired by Mira.
- Metadata: **no AAII.** Artificial Analysis has no Mercury 2.5 page
  (404 on 2026-09-13; only Mercury 2, AAII 12 on v4.3), and Epoch has no
  entry either. The page shows "not yet scored". OpenRouter pricing
  $0.04/$0.15 per M (Inception endpoint). OpenRouter's throughput stats 404
  for the new permaslug, so speed comes from the sample median.

Reverted the recurring `samples/glm-5-3-flash.json` sweep. Build verified
clean (`npm run build`, 347 pages).
