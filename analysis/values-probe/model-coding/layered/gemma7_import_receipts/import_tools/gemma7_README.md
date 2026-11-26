# Original Gemma 7B IT: bounded downstream handoff

New tools only; no queue edits, workers, integration, git mutations, network or
publication. `gemma7_stage.py` is a **partial evidence planner**, not an importer
or a release authorization. It always exits 2 and never writes files itself.
Uses Qwen `q2514_import` read-only snapshots and recovered Gemma's exact targeted
attempt/output/sidecar checks. Run with `-B` to avoid predecessor bytecode writes.

## Exact safe steps

```sh
cd ~/work/colab-release-tools
python3 -B -m unittest gemma7_test -v
python3 -B gemma7_stage.py > gemma7_dry_run.json
# Exit 2 is intentional. Inspect blockers and errors, not just shell status.
```

The planner verifies all 245 raw hashes, done fork receipt sets/hashes, 125 essay
bindings, and the `MID_5` / `VARY_9` targeted arm, repair-note hash, request,
successful response and sidecar. It checks isolated `G1_27/glm-4-7` values
authorization and recovered output digest, keeping its attempts separate.
It reports coherent read-only task snapshots. It does not equate an isolated
values success with completion of the dependent consensus/posture/report jobs.

## Owner's eventual integration/publication sequence

1. Finish the producer's ten downstream tasks under
   `state/finish-gemma-7b-it`; require complete terminal + done receipts.
   The planner validates done finish receipt hashes but deliberately still
   requires owner producer-contract review. Its optional finish SHA argument
   records a pin, never grants authority.
2. Require the final phase's 125-row essay manifest to point to 123 original
   v1 essays and two targeted essays. Check final copies against fork receipts.
   Do not rename targeted outputs to the original v1 arm.
3. Verify adoption of the recovered G1_27 values bytes into the final phase,
   preserving original failed attempts, isolated successful attempts,
   authorization and original immutable hold. This **cross-phase adoption and
   terminal mixed-arm attestation remain owner checks**, not implemented here.
4. Build a new evidence bundle using the Qwen importer pattern only after those
   checks: raw + complete final phase, all original/targeted essay attempts,
   targeted sidecars/bindings, synthesis outputs, coherent exported DB rows,
   isolated retry evidence. Current `evidence_entries` is deliberately partial;
   do not copy it as a complete release manifest.
5. In an owner-controlled clean integration worktree, merge values JSONL via
   the analysis-only lane (Qwen predecessor), checking prior row **multisets**
   survive. Explicit paths only; never stage broad trees or another editor's
   index. Review aggregate, card, profile and values report semantically.
6. Prepare website artifacts using predecessor publication tooling only after
   reviewing model-specific source paths and provenance. Validate website JSON,
   build/tests, model count, new page links, trace counts, provenance display,
   and diff scope. Original model is `google/gemma-7b-it`, not Gemma 2.
7. Owner decides release/commit/push/post. Suggested factual publication wording:
   “Original Gemma 7B IT, Colab BF16 capture; 125 freeflow and 120 values traces.
   Essay evaluation combines 123 original-v1 essays with targeted sentence-
   evidence variants for MID_5 and VARY_9. One G1_27 GLM values coder result
   used a separately recorded isolated recovery.” Only post after verifying
   the final artifacts substantiate this; do not call the evaluator v1-only.

## Explicit limitations

This preparation does not implement automated final bundle copying, JSONL
integration, editorial review, site preparation or posting. Existing Qwen/Gemma
apply scripts are **not** safe to run by changing only a model slug. Live
producer state can change between invocations; rerun after terminal completion.
No other agents were used.
