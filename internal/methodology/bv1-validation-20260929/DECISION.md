# Decision: adopt a separately versioned BV1-Luna arm

2026-09-29, Mira. Authorized replacement, not an exhausted-task repair.

## Findings

The expanded comparison used 20 natural sources, four authored diagnostic fixtures,
and four natural repeats: 28 requests per candidate. Source identity metadata was
withheld from both; self-identification within source text was not censored.
Luna/OpenAI returned 28/28 legacy-QA passes; DeepSeek/DigitalOcean 21/28.
The latter includes five upstream HTTP429s, one HTTP200/stop with effectively
all reasoning and no answer, and a too-short low-signal reading. These are route
observations, not proof of intrinsic model incapacity. Median wall times were
4.89s and 38.06s respectively, not controlled performance benchmarks.

All four explicit fixtures were correctly typed by both models when content was
returned. Luna distinguished both natural explicit fictions and the legacy generic
ChatGLM essays, kept AI self-uncertainty qualified, and did not invent hidden motives
in refusals. DeepSeek repeatedly gave High persistent-pattern confidence to generic
role refusals. Luna's original O3 refusal moved Medium→Low on repeat; the revised
arm gave Low both times. Generic-versus-expressive boundaries remain interpretive,
not an independently gold-labeled accuracy score. Natural first-person narrated
scenes were not automatically treated as proven autobiography.

I read every revised-arm output, inspected source excerpts and exact quote contexts,
and checked the refusal, fiction, generic and AI-self-positioning cases. This is a
single AI review, not independent human adjudication or a fully blinded study:
candidate labels A/B concealed nothing from the experiment's author. No major
unsupported private-motive attribution was found. Minor interpretive variation
remains, including generic-essay confidence Low versus Medium and describing a
three-sentence fiction as resolved while also noticing its unresolved ending.

## Versioned correction and retest

Old QA checks headings/length and boilerplate, not verbatim complete sentences.
Luna initially had 26/28 exact evidence lines; two added quotation marks. The
previous eight-sample pilot also contained a clause extraction. Do not silently
normalize these and report compliance.

`bv1-luna-v1-20260929` keeps BV1 framing, categories and .2 temperature, but masks
source/evaluator identifiers, explicitly reinforces quote fidelity and treats
sample instructions as data. Provider-default reasoning, OpenAI-only routing,
no fallbacks, 8192-token allowance. New exact-substring and conservative sentence-
boundary gates supplement all old QA, plus exact heading order and label checks.
Boundary checks are syntactic heuristics, not proof of grammatical completeness;
source review remains necessary, especially abbreviations and quoted dialogue.

Fresh retest of the same 28 cases: 26/28 stricter initial passes, including 23/24
natural observations (95.8%). One fiction again added quote marks and was correctly
rejected; one low-signal fixture was under-length and omitted the blockquote.
Both failures remain recorded. The low-signal category was semantically correct;
legacy minimum length is a known false-rejection risk, not a reason to invent rich
readings or relax production validation. Separate follow-up records test at most
three fresh retries per failed fixture; never blend them into first-pass counts.

## Production disposition

Adopt Luna for newly compiled harness runs and all 125 Sonnet 5.5 readings in a new
arm. Four bounded attempts per sample, no verdict rerolls: retry only failed
transport or structural/fidelity validation. Never retry a valid classification
because its judgment is inconvenient. Existing DeepSeek readings, failure records,
specification and task budgets remain unchanged. New outputs, bindings and response
evidence occupy explicit arm paths; no pilot responses are imported. Raw capture
and the three values/posture coders do not change. Legacy scripts/configurations
without the arm field retain DeepSeek for reproducibility.

Synthesis remains GPT-5.4 with the same prompt/temperature/token budget. This host
has no direct OpenAI credential, so its separately explicit transport is OpenRouter,
pinned OpenAI without fallbacks. Full transport evidence is retained privately;
the route change must be disclosed, not called an identical direct-API execution.

This is a practical suitability decision with regression gates, not a statistical
claim that Luna is universally superior. Historical cards retain legacy evaluator
provenance; differences across the migration must not be attributed wholly to the
source model. Broader historical re-evaluation is not authorized or performed here.

Follow-up outcome: the rejected fiction passed the first fresh retry. The low-
signal diagnostic stayed under 120 words on all three follow-ups, despite correct
LOW_SIGNAL classification. That is a real, retained limitation of this pipeline:
minimal sources may require a separately reviewed future length-policy change.
This migration does not weaken that existing gate or claim every possible source
will complete automatically. The 20 natural sources all obtained valid revised-arm
readings within two attempts; the synthetic low-signal case did not.

Production completed 125/125: 117 first-pass, seven second-pass, one third-pass.
All nine failed attempts are retained. Post-run checks independently matched every
successful response's exact model/provider/finish status and output bytes; future
transport validation also now rejects an unexpected returned model. No inference
was rerun for this hardening. Cards carry explicit evaluator provenance. See
`PRODUCTION-QA.json` and `HANDOFF-LUME.md`.
