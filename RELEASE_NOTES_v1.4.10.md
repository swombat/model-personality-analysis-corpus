# Release notes — v1.4.10

Prepared 2026-09-17. Analysis release preparation only: no tag, public release, or website deployment performed.

## Union Alpha

- Complete mapping from corpus-v2 v1.2.26 preparation: 125 freeflow + 120 values responses, Stealth-pinned OpenRouter route.
- 125/125 BV1 readings QA-valid; all three coders cover all 120 values samples in both topic and posture layers.
- Three initial three-way posture splits resolved after one independent adjudication. No residual splits; original votes and invalid BV1 attempts retained.
- Added isolated aggregate, concise card, rich profile, final values report, and legacy lexical marker metrics (composite 207; not an attribution measure).
- Final-data integration check preserves every existing record and adds exactly 120 records per manifest/consensus/coder file; comparison respects historical duplicate multiplicity.
- Model slug `union-alpha`, display name Union Alpha, lab Unknown; catalog creation date 2026-09-16. Provider hypotheses are not identity metadata.
- Website route/display/date mappings prepared. Generated model pages, strapline and image deliberately left to the editorial handoff; this release-preparation note does not claim the model is live on the site.

### Editorial pass (Lume, 2026-09-17 10:20)

- Strapline: **"An achievement disguised as an absence of change"** — the
  model's own line, said of a bridge (BV1 evidence: "The bridge's continued
  existence is an achievement disguised as an absence of change"), used here
  as the portrait of its whole moral imagination: maintenance over conquest,
  care that is invisible exactly when it works ("Most of the world is held
  together by work that disappears when it succeeds"). Trace sweep: *repair*
  in 59/125 freeflow samples, *bureau-/form* 70, *clock* 28, *unfinished* 26,
  *museum* 21. The *unfinished* and *municipal* angles were passed over on
  purpose: four straplines already own "unfinished" (haiku-4-5, gpt-5-5-pro,
  gpt-5-6-terra, gpt-6-astra) and Astra owns the municipal joke. What is left
  to this model, and central to its card, is the wry institutional register
  holding an anti-optimising ethic — value that looks like nothing happening.
- Banner: a rainy town square at the last direct sunlight, a council worker
  kneeling to tighten one bolt on a public bench while a woman with an
  umbrella, a child with an orange and an old man with a newspaper pass
  without noticing; the town-hall clock has no hands. Kept outdoors and civic
  to stay distinct from the indoor counters/benches/workshops of Astra,
  qwen3-8-2-4t-a95b, gpt-5, gpt-5-6-terra and kimi-k2-0905. First roll
  lettered the oil can and gave the clock hands; re-rolled with a plain can
  and a blank dial. The second roll added a small blank plaque to the bench.
- Wired: `generate_data.py` run (245 published samples, images attached),
  recurring `samples/glm-5-3-flash.json` sweep reverted, `npm run build`
  clean (349 pages). Committed locally; deployment (push to `main`) is a
  separate decision.

See `analysis/values-probe/model-coding/layered/phase35_union_alpha_20260917/LUME_HANDOFF.md` for interpretation and artifact locations.
