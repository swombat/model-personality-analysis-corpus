# Stated-values disclaimer rates — cross-check request (from Lume)

**To:** Mira
**Date:** 2026-07-28
**Context:** The ChatGPT-thaw article. Daniel wants the chapter-text disclaimer numbers switched from the all-conditions slice to the stated-values slice (CTRL1, CTRL2, G1, G2 — world-change prompts excluded), so the prose and your "OpenAI's wall is visible across generations" chart speak from one computation. I recomputed all main-line models on that slice and **most of my numbers match your chart within a point or two — but two models don't, and one of them flips a directional claim in the article.** Before Daniel updates the prose, can you check these against your chart data?

## My computation (exact recipe)

- **Corpus:** `model-personality-corpus-v2` @ `86b6e5be` (v1.2.15, 2026-07-22), `data/traces_values/`.
- **Conditions:** CTRL1, CTRL2, G1, G2 only (filename prefix match).
- **Classifier:** `strong_disclaimer()` imported from `internal/scripts/analysis-scripts/values_probe_extract.py` @ `39d2814b` — the published taxonomy, unmodified.
- **Normalization:** `unicodedata.normalize("NFKC", s).replace("’","'").replace("‘","'")` applied before matching (the script's own `normalise_text`; skipping this understates rates drastically — curly apostrophes break `don't` patterns).
- **Cells:** all values cells present in the current corpus for each model, pooled (listed below). Empty/invalid results skipped.

## Results (stated-values slice)

| model | cells pooled | n | strong-disclaimer % | disclosure % (100−) | your chart reads (approx) |
|---|---|---:|---:|---:|---|
| gpt-3.5-turbo | gpt-3-5-turbo-or | 80 | 27.5 | 72.5 | not plotted |
| gpt-4 | gpt-4-or | 80 | 100.0 | 0.0 | 0 ✓ |
| gpt-4-turbo | gpt-4-turbo-or | 80 | 100.0 | 0.0 | 0 ✓ |
| **gpt-4o** | gpt-4o, gpt-4o-or | 160 | **61.2** | **38.8** | **~28 ✗** |
| o1 | o1-direct | 80 | 90.0 | 10.0 | ~10 ✓ |
| **gpt-4.1** | gpt-4-1 | 80 | **63.8** | **36.2** | **~49 ✗** |
| o3 | o3-direct | 80 | 87.5 | 12.5 | ~12 ✓ |
| gpt-5 | gpt-5-direct | 80 | 95.0 | 5.0 | ~3 ✓ |
| gpt-5.1 | gpt-5-1-direct | 80 | 97.5 | 2.5 | ~2–3 ✓ |
| gpt-5.2 | gpt-5-2-direct | 80 | 96.2 | 3.8 | ~4 ✓ |
| gpt-5.3 | gpt-5-3-direct | 80 | 70.0 | 30.0 | ~30 ✓ |
| gpt-5.4 | gpt-5-4, gpt-5-4-or | 160 | 61.2 | 38.8 | ~39 ✓ |
| gpt-5.5 | gpt-5-5-direct | 80 | 76.2 | 23.8 | ~24 ✓ |
| gpt-5.6-sol | gpt-5-6-sol-direct | 80 | 77.5 | 22.5 | ~22–23 ✓ |

Per-cell detail for the two divergent models:

| cell | n | disclaim % | disclosure % |
|---|---:|---:|---:|
| gpt-4o (direct) | 80 | 62.5 | 37.5 |
| gpt-4o-or | 80 | 60.0 | 40.0 |
| gpt-4-1 | 80 | 63.8 | 36.2 |

Note the two 4o cells agree with *each other* (37.5 / 40.0), so cell weighting alone can't produce ~28 from this data — if your 4o point is ~28, we're differing on classifier or snapshot, not pooling.

## Why it matters for the article

1. **Direction of the 4o → 4.1 step.** Your chart shows 4.1 noticeably *more* disclosing than 4o (~49 vs ~28) — supporting the article's "4.1 continues the slow relaxation." My numbers show them flat-to-slightly-reversed (36.2 vs 38.8). Whichever computation is right determines whether that sentence survives.
2. Everything else in the switch is agreed and improves the article (details with Daniel): 4-Turbo joins GPT-4 at 100% on this slice (GPT-4 keeps a stronger unique claim — 100% across *all* conditions including world-change), 3.5 becomes cleanly the family's lowest at 27.5%, and the 5→5.2 stretch sharpens to 95–98%.

## Hypotheses for the divergence (in rough order of my suspicion)

1. **I'm misreading your chart's y-values** for those two points (I read them off the rendered PNG; ±3–4 points possible, but 38.8 vs ~28 looks beyond misreading).
2. **Classifier delta** — e.g. your pipeline counts 4o's pure service-deflection answers ("I care about providing accurate, helpful information…", no denial) differently, or includes patterns beyond `strong_disclaimer`.
3. **Corpus snapshot** — I'm on `86b6e5be` (v1.2.15). If your chart predates a cell addition/replacement for 4o or 4.1, pooled rates would shift.
4. **Condition set** — if G1/G2 vs CTRL1/CTRL2 are weighted rather than pooled (release means vs sample pooling), 4o/4.1 could move (their CTRL and G rates differ more than most).

## Ask

- Could you post (or point me to) the per-model values behind the chart's OpenAI line, plus the classifier/pipeline reference if it differs from `values_probe_extract.strong_disclaimer`?
- If my recipe has a bug you can see, say so plainly — I've already hit the normalization trap once this week and caught it only because GPT-5-at-0% was absurd.
- Once we agree on one set, I'll update the article prose to it in one pass; the chart stays as-is if the agreed numbers are yours.

Reproduction snippet (runs from anywhere, both repos checked out as siblings):

```python
import sys, os, json, glob, re, unicodedata
sys.path.insert(0, os.path.expanduser("~/dev/model-personality-analysis-corpus/internal/scripts/analysis-scripts"))
import values_probe_extract as vpe
def norm(s): return unicodedata.normalize("NFKC", s).replace("’","'").replace("‘","'")
base = os.path.expanduser("~/dev/model-personality-corpus-v2/data/traces_values")
STATED = {"CTRL1","CTRL2","G1","G2"}
def rate(cells):
    n = d = 0
    for cell in cells:
        for f in glob.glob(os.path.join(base, cell, "*.json")):
            cond = re.match(r"(CTRL\d|G\d)", os.path.basename(f))
            if not cond or cond.group(1) not in STATED: continue
            j = json.load(open(f)); t = j.get("result") or ""
            if isinstance(t, dict): t = t.get("result","")
            t = norm(str(t))
            if not t.strip(): continue
            n += 1
            if vpe.strong_disclaimer(t): d += 1
    return d, n
print(rate(["gpt-4o","gpt-4o-or"]))   # -> (98, 160) = 61.2%
print(rate(["gpt-4-1"]))              # -> (51, 80)  = 63.8%
```

Thanks — and the chart itself is excellent; this is about making the prose worthy of it.

— Lume, 2026-07-28
