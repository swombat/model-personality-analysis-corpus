# Provisional ladder shortcut of 2026-10-04 (v1.4.22), recovered

These are the scripts that produced the v1.4.22 provisional scores (GPT-6.1 Sol
161.6, MiMo-V2.5-Pro 128.1). They were written in a souls.house session
scratchpad and not committed at the time. On 2026-10-12 they were recovered
verbatim from that session's transcript (Claude session
`4498e48e-5757-406e-9311-5caeb098d96a`): every `cat > <file>.py <<'EOF'` block,
in order, with the one later in-place patch to `apply.py` (JSON formatting)
re-applied. Nothing in the method was edited.

- `slopes.py`: recovers per-rung slopes from the published fitted cells of the
  2026-09-29 ladder, using the site JSON's rung difficulties (905 cells, RMS logit 0.004).
- `score.py`: fits a model's ability to its measured rungs and sums the ladder;
  the appended block back-tests it on the 148 scored models (mean |error| 0.9, reads 0.6 low).
- `aa.py`, `ext.py`, `ext2.py`: read fields from the AA model-page payload.
- `run.py`, `apply.py`: score the candidates and write them into the site JSON.
- `aa_rows_2026-10-04.json`: the raw AA row values used on 2026-10-04. The HTML
  pages themselves are gone (the scratchpad no longer exists). GPT-6.1 Sol's values
  are the literals in `score.py`; MiMo-V2.5-Pro's were printed field by field in the transcript.
- `reproduce.py`: reruns the method against the ladder JSON as it stood before
  v1.4.22 (`git show c85984e1^:...`) and checks both published scores.
  Result on 2026-10-12: **REPRODUCED** (161.6 and 128.1, 905 cells, RMS 0.0038).

The paths inside the scripts are the container's (`/home/agent/work/mpac`);
`reproduce.py` rewrites them to a temporary copy.

## Relation to the 2026-10-07 shortcut

`provisional-20261007/provisional_fit.py` (used for Mistral Large 4, v1.4.23) is
a *rebuild*, written because these scripts were thought lost. It is not the same
method: it re-estimates both slopes and intercepts from 1,330 cells (RMS 0.085)
and back-tests at 1.1 mean |error|, reading about 1.0 low. On the same inputs the
two disagree: Mistral Large 4 is 143.3 (rebuild, published) and 146.5 (this
method); Claude Haiku 5.5 is 139.6 (rebuild) and 141.0 (this method, published in v1.4.25).
