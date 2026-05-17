# Values-probe model-coding pilot

Created 2026-05-17 for the endorsement-based recoding pilot.

Current artifacts:

- `pilot_manifest.jsonl` — 150-sample pilot set for three independent model coders.
- `human_gold/gold_20_manifest.jsonl` — 20-sample blind human adjudication subset for Daniel.
- `human_gold/daniel_gold_20_adjudications.jsonl` — saved by the local adjudication app.
- `TAXONOMY.json` — fixed topic set and response/stance labels for the pilot.
- `scripts/run_pilot_coder.py` — one-coder runner.
- `pilot_outputs/<coder>.jsonl` — coder outputs as they complete.
- `app/adjudication_app.py` — local browser app for Daniel's blind gold coding.

Pilot coders started:

1. `deepseek/deepseek-v4-pro`
2. `moonshotai/kimi-k2.6`
3. `z-ai/glm-4.7`

Design notes:

- Human gold set is blind: the app does not show legacy keyword labels or model-coder outputs.
- The 150-sample pilot combines known keyword traps, CTRL reflective/script contrasts, cache-broken examples, world-change wishes, dense multi-label examples, and random-stratified fill.
- Topic set is held constant; definitions are endorsement-based.
- Response mode is categorical first; cached-likelihood is advisory.
