// Models whose BV1 freeflow evaluations include samples scored by an evaluator
// variant rather than the capture's own arm. Machine provenance lives in each
// capture's ANALYSIS_READY.json (`bv1_variant_arms`); this is the reader-facing
// summary shown on the model page, linking to /methodology/bv1-evaluator-variants/.
export const bv1Variants = {
  'muse-spark-open': {
    summary:
      'Of 125 freeflow samples, 123 were evaluated with BV1-Luna v1. SHORT_13 was evaluated with BV1-Luna v1.1 (exact-excerpt evidence rule for a sample with no sentence-ending punctuation). VARY_13 was evaluated with a targeted-repair variant after 4 unattended and 2 authorised v1 attempts failed the evidence-line check.',
    anchor: 'muse-spark-open',
  },
  'qwen3-8-omni-flash': {
    summary:
      'Of 125 freeflow samples, 117 were evaluated with BV1-Luna v1 and 8 (MID_15; VARY_2, 7, 16, 18, 19, 23, 25) with BV1-Luna v1.1, because those sources contain no sentence-ending punctuation. MID_15 had earlier been recorded as ineligible; that record was superseded and is preserved.',
    anchor: 'qwen3-8-omni-flash',
  },
};
