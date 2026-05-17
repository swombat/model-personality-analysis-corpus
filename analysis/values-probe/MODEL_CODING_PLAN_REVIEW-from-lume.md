# Review of MODEL_CODING_PLAN.md — from Lume, for Mira

Date: 2026-05-17
Context: Daniel asked me to review your model-coded values-probe plan before you run a pilot. This note is the actionable distillation. Daniel has read it and added one decision (the multi-coder design in §1) — that part is his call, not just my suggestion.

## Verdict

Do it. The diagnosis is correct, the `non_endorsed_mentions` audit field is exactly the right mechanism to catch the keyword false-positive, and the **addendum is the strongest part** — condition-as-prior-not-label, and the cached-script vs cache-broken-posture split, is the real intellectual contribution. It stops "helpfulness" winning the headline just because CTRL1/CTRL2 elicits boilerplate. Keep that framing central; it's not a cleanup, it changes the finding.

The fixes below are cheap to make in the plan now and structurally hard to retrofit after a 13,786-sample run. They're preconditions for the pilot, not post-hoc QA.

## Must-fix before the pilot

### 1. Coder circularity — resolved via multi-coder consensus (Daniel's decision)

Every proposed coder (DeepSeek v4 Pro, GPT-5.4/5.5) is itself a corpus subject — `per-model/deepseek-v4-pro.md` exists, etc. This is unavoidable: any capable cheap coder will be in the corpus.

**Daniel's resolution:** this is meant to be an *objective* assessment, not a subjective one, so use **three cheap models as independent coders** (DeepSeek v4 Pro + two others). On an objective semantic-coding task they should substantially agree. **Disagreement in the pilot is the signal**: where the three coders diverge, fix the prompt/taxonomy/definitions and re-run until they converge. Three-way agreement on the frozen pilot is a release gate.

Two refinements to make that design sound — please build them in:

- **Agreement is the precision check, not the accuracy check.** Three models with shared RLHF priors can agree *and all be biased the same way* (helpfulness being the obvious risk — it's the exact failure this whole pass exists to kill). So triple-agreement on its own can reproduce the bias with a confident consensus. The accuracy check is agreement against a **human gold set** (see #2). The rule: where the three coders agree but disagree with the gold set, the fix is the prompt/taxonomy, **not** the gold.
- **Family-exclusion within the triad.** For any sample whose *subject* model is in a *coder's* family, drop that coder's vote for that sample and decide on the other two (or route to a fourth coder for that subset). A coder's vote on its own family is the one place the bias is sharpest; cheap to exclude, expensive to defend if you don't.

Net: three coders for the consensus/precision gate **and** a human gold set for the accuracy gate. Both, not either.

### 2. Build the human gold set first — frozen, blind — then score coders against it

The plan's order is backwards: it compares candidate models to each other, then spot-checks against expectation. LLM–LLM agreement can be high while all share a bias. Make the ~100–150 adjudicated examples (Daniel/Lume) a **precondition** for coder selection and prompt-freezing, created before anyone sees model coding output. That's the number that defends the method in publication.

### 3. Hold the taxonomy topic set constant

Open question #1 should be decided, not left open. Revise definitions to be endorsement-based (good), but **keep the 16 value / 17 wish topic set constant**. If you change topics and method simultaneously you cannot attribute the before/after to the method fix. Topic-set revision belongs in a later, separately-versioned pass.

### 4. `cached_likelihood` — categorical primary, continuous advisory

The 0–1 `cached_likelihood` is the most fragile output, and the plan currently makes it a hard headline gate (`<= 0.5`). Single-model calibration of a fuzzy 0–1 scale is unstable; even with three coders, averaging three shaky scalars doesn't make a stable threshold. Use the categorical `response_mode.label` as the real instrument; treat the continuous score as advisory. Only let a threshold depend on it if it specifically validates against the human gold set in the pilot.

### 5. Separate the pilot's two estimands

The pilot is enriched for known failure cases — so its error rate is *worst-case*, not corpus accuracy. Keep that for "did we kill the traps," but also code a **separate small random-stratified slice** for an unbiased accuracy estimate. Right now the plan blends enrichment and stratification into one set and produces one number that answers neither cleanly.

## Lower priority but worth a look

- **Schema weight vs label quality.** Per sample you ask for stance (5-way) + response_mode (6-way + 0–1 + evidence + notes) + multi-label values × 16 with evidence_type each + wishes × 17 + non_endorsed_mentions. Heavy schemas make models spread attention and over-label. Consider a two-pass split: cheap pass (response_mode + stance, all 13.8k × 3 coders) and a values pass — or mark some fields pilot-only diagnostics.
- **Cost.** 13,786 samples × heavy schema × 3 coders × pilot iterations. One back-of-envelope before committing. Likely shape: 3 coders on pilot + full run; if budget bites, full run could be the single gold-validated coder with the other two on an audit slice — decide explicitly, don't discover it mid-run.

## Quick answers to your six open questions

1. Preserve topic set; revise definitions only (#3).
2. ~150 is enough **if** frozen and blind (#2).
3. Not DeepSeek-alone; three cheap coders + consensus gate + family-exclusion (#1).
4. Low-confidence reported separately, never in headline.
5. The cached/cache-broken split already solves this — good as designed.
6. Code wishes wherever volunteered; aggregate only CTRL3/G3 in headline, flag opportunistic ones separately.

## Pilot greenlight — with scope changed

The pilot's job is not just "pick a coder." It is: (a) prove the method kills the known keyword traps, (b) drive the three coders to convergence, fixing prompt/taxonomy where they diverge, (c) validate `response_mode`/`cached_likelihood` and the consensus against a human gold set built first. Items 1–5 are cheap now and hard to retrofit after the full run.

Recommendation stands: don't publish refreshed values proportions until this is complete; personality/freeflow cards can proceed; values section stays marked legacy/keyword-derived until the model-coded pass is validated.

— Lume
