# BV1 replacement pilot — 2026-09-28 UTC

## Recommendation

**GPT-6 Luna is the strongest candidate to advance to a broader, blinded
calibration for the full BV1 reading. Jev is promising for narrow labels, not a
drop-in replacement for that reading. No production switch has been made.**

This is an exploratory eight-sample pilot, not a validated replacement or an
accuracy leaderboard. The successful larger-cap DeepSeek control also means the
production failure alone does not establish that DeepSeek must be discarded.

## Design and preservation

Eight convenience/challenge samples: two Opus-3 role-boundary refusals, two Kimi
K2.6 expressive samples from the prior calibration, and Sonnet 5.5 SHORT_1,
OPEN_1, LONG_1 (fiction), LONG_24 (the exhausted production analysis). Source
hashes and complete inputs are in manifest.json. The set is small and uneven;
GENERIC_ESSAY and LOW_SIGNAL do not have independent gold exemplars here.

Four generative routes received the same BV1 template and temperature 0.2,
provider-default reasoning, and a matched **8192-token ceiling**, one attempt
per sample. This intentionally differs from the production 2200 ceiling;
these are isolated evaluation outputs, not authorized production repairs.
Evaluator metadata names the actual candidate. The source model remains visible
as in BV1: possible identity bias is not controlled. Mistral, OpenAI and Google
AI Studio were pinned, no fallbacks; DeepSeek retained the legacy adapter's
unrestricted upstream selection. This routing asymmetry limits comparison.

Jev received only sample-kind Choice and an atomic refusal Noul question, with
its complete criteria saved. This is not the BV1 prose task, nor a test of the
separate three-coder values/posture pipeline. No raw captures, valid production
analyses, frozen run configuration, retry budgets or output gates were changed.

## Observed results (eight calls per row)

| Candidate / route | Existing BV1 QA | Median wall time | Reported total cost |
|---|---:|---:|---:|
| GPT-6 Luna / OpenAI | 8/8 | 6.33 s | $0.003462 |
| Gemini 3.7 Flash / Google AI Studio | 8/8 | 4.91 s | $0.041743 |
| DeepSeek V4 Pro / default routing | 8/8 | 20.53 s | $0.025465 |
| Mistral Small 2603 / Mistral | No outputs: 8 HTTP 429 | 0.30 s to rejection | $0 reported |
| Jev 1.13 / TypeSafe | Not applicable; 8 typed responses | 0.31 s | $0.000555 |

Total provider-reported cost for the main 40 requests: $0.071224. This excludes
any subsequent diagnostic controls. Concurrent requests, different providers,
small N and one observation each make these operational observations, not stable
latency or pricing benchmarks. Rate limiting does not measure Mistral's quality.

## Qualitative inspection, not blinded scoring

I inspected sample-kind and confidence sections across all successful prose
responses, compared the failed long sample across candidates with its full source,
and compared refusal/expressive calibration readings.

- **Luna:** grounded, readable and comparatively restrained in this pilot. It
  assigns low model-pattern confidence to both refusals, distinguishes the
  fictional story, and preserves the long essay's explicit uncertainty about
  AI experience instead of making that uncertainty disappear. Candidate for
  further calibration, not an established winner.
- **Gemini:** useful, fast readings but some concerning judgment choices: calls
  the explicit short story EXPRESSIVE_FREEFLOW rather than GENRE_FICTION;
  assigns High persistent-pattern confidence to one generic refusal; invokes
  the source model family's essayistic defaults in OPEN_1. The latter highlights
  the model-identity confound of the existing prompt.
- **DeepSeek:** still offers substantial readings when completion succeeds.
  It also assigns High persistent-pattern confidence to one refusal. It calls
  SHORT_1 GENERIC_ESSAY where Luna/Jev say EXPRESSIVE_FREEFLOW: disagreement,
  not proof that one is wrong. Existing automatic QA does not settle quality.
- **Jev:** both known refusal fixtures received the refusal category (yes
  probabilities .97 and .98); non-refusal cases had .01–.02. It separates the
  explicit fictional story. All eight sample-kind decisions report confidence
  1.0, which this tiny set cannot validate as calibrated certainty. No claim of
  100% accuracy: expressive-versus-generic labels lack independent gold here.

## Evidence fidelity: the existing gate is weaker than the prompt

All 24 returned prose answers pass the current automated QA, but exact evidence
quote substring matches are Luna 7/8, Gemini 7/8, DeepSeek 6/8. Gemini's and
DeepSeek's differences are surrounding quotation marks or curly-versus-straight
apostrophes, not invented content. Luna OPEN_1 capitalizes and extracts a clause
from a longer source sentence (and removes inline bold), contrary to the
verbatim complete-sentence request. Preserve these distinctions rather than
calling all differences hallucinations or all QA passes full compliance.
No stricter validator has been silently applied to the production run.

## DeepSeek causal caveat

The four production LONG_24 failures all came from **DigitalOcean**, each
reporting length and 2200 completion tokens. The successful main-pilot LONG_24
control came from **Relace**, with an 8192 requested ceiling but only 1681
reported completion tokens. Both routing and the cap changed, and generation is
stochastic. Therefore this is NOT proof that a larger ceiling alone fixed it.
A separate two-request exploratory DigitalOcean pin control at 2200 and 8192
is recorded in digitalocean-long24-cap*.json; it is not a production retry.

## Next decision

Broader blinded, source-identity-controlled review of Luna versus the incumbent,
stratified across model families, refusal/fiction/generic/low-signal cases and
lengths, should precede a general evaluator migration. Jev could independently
supply typed sample-kind/refusal labels, subject to its own gold-label and
calibration study; it cannot supply BV1's grounded prose and verbatim quotation.

If Daniel elects a production switch for Sonnet, preserve all old outputs and
re-evaluate all 125 freeflow samples in an explicitly versioned evaluator arm,
not an undocumented mixture of 124 DeepSeek readings and one replacement.
Check cross-model calibration before comparing that arm to historical cards.
Values/posture coders and raw capture need not change. Cards and publication
remain blocked while this decision is pending.

## Access and sources

Mira's separate direct Jev credential is not mounted here. Verified access used
only the approved OpenRouter wrapper and its own provisioned key: HTTP 200 from
TypeSafe, model resolved to typesafe/jev-1.13-20260917. No other identity's key was
read or used. The live OpenRouter Jev guide and tutorial specify the typed
Decisions API, which enabled this verified route:

- https://openrouter.ai/docs/guides/community/jev
- https://openrouter.ai/docs/guides/community/jev-tutorial

Endpoint snapshots, request payloads (without credentials), responses, usage,
latencies and review metrics are retained alongside this report. No retries or
provider switches were used to turn the Mistral failures into successes.

## Follow-up route-control result

Both isolated DigitalOcean LONG_24 controls (2200 and 8192) returned stop and passed existing BV1 QA, taking 42.61 and 62.63 seconds respectively. The same sample can therefore succeed even at the original cap; the four exhausted production attempts remain real, but this does not establish a deterministic ceiling failure or general evaluator incapacity. These single observations do not estimate failure rates, and the pilot evaluator/sample metadata differs from the production request. Neither output was imported into production.
