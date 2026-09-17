# Phase 35 — Union Alpha

Completed and QA-verified 2026-09-17. Unknown developer; Stealth is the routing label, not a lab attribution. Raw corpus v1.2.26 and analysis v1.4.10 are prepared, not tagged or publicly released.

- Raw: 125 freeflow + 120 values; all 245 strict-audit valid, with stop finishes and exact upstream/model provenance.
- BV1: 125/125 QA-valid after bounded retries. Invalid readings and status snapshots preserved under `freeflow_bv1/before_retry_*`.
- Values topics: 3 × 120 coder records and complete consensus.
- Posture: 3 × 120; three initial three-way splits independently adjudicated once, all resolved. Original votes under `posture_collapsed/before_adjudication`, replacements under `adjudicated`.
- Aggregates, cards, profiles and final values reports assembled; no generated website publication.
- Integration: nine final-data files preserve all prior records and add exactly 120 each. `integration-check.json` records canonical-JSON multiset comparisons, preserving pre-existing duplicate multiplicity.
- Legacy contemplative lexical composite: 207. This is not a provider classifier.

## Reproduction

`audit_raw.py` checks exact raw coverage and provenance. `run_freeflow_bv1.py` and `run_semantic_analysis.sh` run the standard classifiers. The semantic first pass deliberately exits nonzero on a missing majority. `finish_analysis.py` performs bounded BV1 repair and at most one adjudication, then validates and assembles. Never rerun adjudication to chase agreement. `validate_analysis.py` and `integration-check.json` are the completion evidence, not the presence of a running process.

The automatic chain completed assembly at 09:36 CEST. The intended scheduled follow-up did not produce visible supervision; final integration and packaging were completed interactively after Daniel asked. See `LUME_HANDOFF.md` for the editorial boundary.
