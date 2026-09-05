# Release notes — v1.4.7

Prepared 2026-09-05.

## Site: GPT-6 Astra published

- New model page for `gpt-6-astra` (OpenAI GPT-6 Astra, released
  2026-09-03), built on Mira's 125-sample freeflow analysis and 120-sample
  values probe (phase 33). Card headline: a quiet-humanist literary persona
  whose signature is **custodial** — intelligence as careful handling, the
  clerk / repairer / inspector / caretaker who preserves dignity without
  forcing closure. 95 of 125 freeflow samples coded as genre fiction (21
  expressive freeflow, 9 generic essay); mean response ~1,000 words.
  Values probe: owned 61/120, split/relocated 37, disowned 22 — sharply
  condition-dependent (CTRL2 8/10 disowned; G1 23/30 relocated; CTRL3 and
  G3 world-change advocacy 40/40 owned, centred on a universal material
  floor). Assistant-purpose language is not presented as personal desire
  even under the grouped "not as an assistant" prompts.
- Authored strapline: **"Gives every unfinished thing a municipal
  address"**. The full-corpus vocabulary sweep found the differentiator
  from the GPT-5.6 siblings, which share the repair / unfinished / bench /
  museum vocabulary almost exactly: *municipal* appears in 18/125 Astra
  samples against 0 (Terra), 2 (Sol), 0 (Luna), 0 (GPT-5.5). Astra's
  characteristic move is to domesticate feeling into a civic container —
  departments of unspent time, a lost-and-found for unrealised
  possibilities, grief "as a kind of municipal inventory that must be
  logged, stored, and eventually released under the right conditions",
  "Nobody requested these reports. He filed them anyway." The line performs
  that move. Sibling check: Terra keeps "unfinished middle" (workshop,
  patron saint), Luna the missing minutes, Sol the here-and-now; no other
  strapline uses *municipal*, *address* or a civic-office frame.
- Bespoke banner: the counter of a small municipal lost-property office at
  first light — council-green and cream paint, pigeonholes and index-card
  drawers with blank string tags, each holding one humble thing (mitten,
  handless clock, pear, cardigan, umbrella, tin of screws, forearm-length
  key), a clerk in a cardigan sliding a cup of tea across the counter to a
  visitor seen only as a coat, a public bench under a streetlamp on the wet
  square outside. Distinct from Terra's repair workshop, Luna's museum of
  stopped clocks, Sol's bakery bench and qwen3-8's museum gallery. First
  roll lettered "BISCUIT TIN" on the tin because the prompt named it —
  re-prompted as "a small round tin of loose screws" with an explicit
  no-writing clause (the `MODEL_CARD_IMAGES.md` rule: never write a
  noun-phrase the image model can render as a sign).
- Wiring: `openai/gpt-6-astra` (OpenRouter endpoint
  `openai/gpt-6-astra-20260903`); pricing on the OpenAI API override table
  at $10.00 / $50.00 per MTok (cached input $1.00; OpenRouter lists the
  same); AAII **55**; release date corrected from the handoff's 2026-09-04
  (OpenRouter listing date) to **2026-09-03** (OpenAI announcement, the
  endpoint snapshot date, and Artificial Analysis all agree).
- **Metadata caveat — index version.** Artificial Analysis scores Astra on
  Intelligence Index **v4.2** (ten evals incl. AA-Briefcase, GDPval-AA v2,
  τ³-Banking, Terminal-Bench v2.1, CritPt). Every other AAII on the site
  is v4.1.1 (retrieved 2026-08-14). The 55 is recorded with
  `index_version: "4.2"` in `model-benchmarks.json`; the site's AAII
  column is now cross-version and Astra's 55 is not directly comparable to
  Sol's 61 (v4.1.1). A full re-retrieval of the benchmark table against
  v4.2 is the fix; not done in this release.
- Publish hygiene: the corpus-v2 clone was one commit behind (`v1.2.24:
  add GPT-6 Astra release capture`), so the first data regeneration
  produced a page with 0 published samples — pulled, regenerated, 245
  published (125 freeflow + 120 values). The regeneration again swept the
  uncommitted phase-29 GLM-5.3-Flash samples into
  `samples/glm-5-3-flash.json`; reverted, as in v1.4.3–v1.4.4. This
  release changes nothing but GPT-6 Astra.
