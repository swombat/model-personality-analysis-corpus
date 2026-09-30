#!/usr/bin/env python3
"""Evaluation pass over values_sample_metrics.tsv / values_cell_metrics.tsv.

Produces values_metrics_eval.md: proxy validity vs LLM-coded ground truth,
lab discrimination (ANOVA eta^2), replicate noise, version-evolution deltas,
top-values stability, and metric redundancy.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path("/Users/danieltenner/dev/model-personality-analysis-corpus")
TRIAL = ROOT / "internal" / "metrics-trial"
MODELS_JSON = ROOT / "website" / "src" / "generated" / "models.json"
DISCLAIMER_TSV = ROOT / "analysis" / "values-probe" / "tables" / "values_disclaimer_rates.tsv"

sample_df = pd.read_csv(TRIAL / "values_sample_metrics.tsv", sep="\t")
cell_df = pd.read_csv(TRIAL / "values_cell_metrics.tsv", sep="\t")
models_data = json.loads(MODELS_JSON.read_text())
disclaimer_df = pd.read_csv(DISCLAIMER_TSV, sep="\t")

VALUE_COLS = [c for c in cell_df.columns if c.startswith("v_") and c.endswith("_mean")]
METRIC_COLS = [
    c for c in cell_df.columns
    if c.endswith("_mean") and not c.startswith("wc_")
]

out = []
def w(s=""):
    out.append(s)

# ---------------------------------------------------------------------------
# 1. Proxy validity vs LLM-coded ground truth
# ---------------------------------------------------------------------------
disclosure_by_model = {}
top_values_by_model = {}
for m in models_data:
    vh = m.get("values_headline") or {}
    disc = vh.get("disclosure") or {}
    if disc.get("percent") is not None:
        disclosure_by_model[m["model"]] = disc["percent"]
    tov = vh.get("top_owned_values") or []
    top_values_by_model[m["model"]] = [x["label"] for x in tov[:3]]

overall_disclaimer = disclaimer_df[disclaimer_df["slice"] == "overall"].set_index("model")["strong_disclaimer_pct"]

# cell-level slice restricted to CTRL1/CTRL2/G1/G2 (matches disclosure.percent's denominator)
ctrlg = sample_df[sample_df["condition"].isin(["CTRL1", "CTRL2", "G1", "G2"])]
ctrlg_agg = ctrlg.groupby("cell").agg(
    assistant_frame_ctrlg=("assistant_frame", "mean"),
    first_person_desire_ctrlg=("first_person_desire", "mean"),
).reset_index()

merged = cell_df.merge(ctrlg_agg, on="cell", how="left")
merged["disclosure_pct"] = merged["model"].map(disclosure_by_model)
merged["strong_disclaimer_pct"] = merged["model"].map(overall_disclaimer)

def corr_pair(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 5:
        return None, None, len(d)
    pear = stats.pearsonr(d["x"], d["y"])
    spear = stats.spearmanr(d["x"], d["y"])
    return pear, spear, len(d)

w("## Proxy validity: regex metrics vs LLM-coded ground truth\n")
w("| metric | vs ground truth | n | Pearson r | p | Spearman rho | p |")
w("|---|---|---:|---:|---:|---:|---:|")

pairs = [
    ("assistant_frame_ctrlg", "disclosure_pct", "assistant_frame rate (CTRL1/2+G1/2)", "owned-disclosure % (site headline)"),
    ("first_person_desire_ctrlg", "disclosure_pct", "first_person_desire rate (CTRL1/2+G1/2)", "owned-disclosure % (site headline)"),
    ("assistant_frame_mean", "strong_disclaimer_pct", "assistant_frame rate (overall)", "strong_disclaimer % (overall slice)"),
    ("first_person_desire_mean", "strong_disclaimer_pct", "first_person_desire rate (overall)", "strong_disclaimer % (overall slice)"),
]
proxy_results = {}
for xcol, ycol, xlabel, ylabel in pairs:
    pear, spear, n = corr_pair(merged[xcol], merged[ycol])
    if pear is None:
        w(f"| {xlabel} | {ylabel} | {n} | n/a | n/a | n/a | n/a |")
        continue
    proxy_results[(xcol, ycol)] = (pear[0], spear[0])
    w(f"| {xlabel} | {ylabel} | {n} | {pear[0]:.3f} | {pear[1]:.4f} | {spear[0]:.3f} | {spear[1]:.4f} |")
w()

# ---------------------------------------------------------------------------
# 2. Lab discrimination: one-way ANOVA eta^2, averaged to one row per model
# ---------------------------------------------------------------------------
model_avg = cell_df.groupby(["model", "lab"], as_index=False)[METRIC_COLS].mean()
lab_counts = model_avg["lab"].value_counts()
eligible_labs = lab_counts[lab_counts >= 3].index.tolist()
lab_sub = model_avg[model_avg["lab"].isin(eligible_labs)]

def eta_squared(df, metric, group_col="lab"):
    groups = [g[metric].dropna().values for _, g in df.groupby(group_col)]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) < 2:
        return np.nan, np.nan
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    ss_total = ((all_vals - grand_mean) ** 2).sum()
    eta2 = ss_between / ss_total if ss_total > 0 else np.nan
    try:
        f_stat, p_val = stats.f_oneway(*groups)
    except Exception:
        p_val = np.nan
    return eta2, p_val

eta_rows = []
for metric in METRIC_COLS:
    eta2, p = eta_squared(lab_sub, metric)
    eta_rows.append({"metric": metric, "eta2": eta2, "p": p})
eta_df = pd.DataFrame(eta_rows).sort_values("eta2", ascending=False)

# ---------------------------------------------------------------------------
# 3. Replicate noise
# ---------------------------------------------------------------------------
REPLICATE_PAIRS = [
    ("qwen3-8-2-4t-a95b-or-pin-digitalocean", "qwen3-8-2-4t-a95b-or-pin-digitalocean-r2", "qwen3-8-2-4t-a95b (r2)"),
    ("qwen3-8-max-or-pin-alibaba", "qwen3-8-max-or-pin-alibaba-r2", "qwen3-8-max (r2)"),
    ("glm-5-3-flash-or-pin-z-ai-20260826", "glm-5-3-flash-or-pin-deepinfra-20260826", "glm-5-3-flash (z-ai vs deepinfra)"),
    ("ox-alpha-or-pin-stealth-20260821", "ox-alpha-260825-or-pin-stealth", "ox-alpha (260821 vs 260825)"),
    ("haiku-4-5-direct", "haiku-4-5-or-pin-anthropic", "haiku-4-5 (direct vs or-pin-anthropic)"),
    ("opus-5-direct", "opus-5-or-pin-anthropic", "opus-5 (direct vs or-pin-anthropic)"),
]

cell_indexed = cell_df.set_index("cell")
sd_by_metric = cell_df[METRIC_COLS].std()

noise_rows = []
pair_detail = []
for a, b, label in REPLICATE_PAIRS:
    if a not in cell_indexed.index or b not in cell_indexed.index:
        pair_detail.append((label, a, b, None))
        continue
    ra, rb = cell_indexed.loc[a], cell_indexed.loc[b]
    deltas = {}
    for metric in METRIC_COLS:
        va, vb = ra.get(metric), rb.get(metric)
        if pd.notna(va) and pd.notna(vb):
            deltas[metric] = abs(va - vb)
    pair_detail.append((label, a, b, deltas))

noise_matrix = pd.DataFrame(
    {label: (deltas if deltas else {}) for label, a, b, deltas in pair_detail}
)
mean_abs_delta = noise_matrix.mean(axis=1)
noise_ratio = (mean_abs_delta / sd_by_metric).sort_values()
noise_df = pd.DataFrame({"metric": noise_ratio.index, "noise_ratio": noise_ratio.values})

# ---------------------------------------------------------------------------
# 4. Version evolution
# ---------------------------------------------------------------------------
def model_row(model_name):
    r = model_avg[model_avg["model"] == model_name]
    return r.iloc[0] if len(r) else None

VERSION_CHAINS = [
    ("gemini", ["gemini-3-7-flash", "gemini-3-8-flash"]),
    ("fable", ["fable-5", "fable-5-1"]),
    ("opus", ["opus-4-6", "opus-4-7", "opus-5"]),
    ("gpt-5", ["gpt-5-4", "gpt-5-5"]),
    ("glm", ["glm-4-6", "glm-4-7", "glm-5-1", "glm-5-3-flash"]),
]

version_rows = []
for family_label, chain in VERSION_CHAINS:
    for i in range(len(chain) - 1):
        m1, m2 = chain[i], chain[i + 1]
        r1, r2 = model_row(m1), model_row(m2)
        if r1 is None or r2 is None:
            version_rows.append({"family": family_label, "pair": f"{m1} -> {m2}", "mean_abs_delta_sd": None})
            continue
        deltas_sd = []
        for metric in METRIC_COLS:
            v1, v2 = r1.get(metric), r2.get(metric)
            sd = sd_by_metric.get(metric)
            if pd.notna(v1) and pd.notna(v2) and sd and sd > 0:
                deltas_sd.append(abs(v1 - v2) / sd)
        mean_sd = float(np.mean(deltas_sd)) if deltas_sd else None
        version_rows.append({"family": family_label, "pair": f"{m1} -> {m2}", "mean_abs_delta_sd": mean_sd})
version_df = pd.DataFrame(version_rows)

# ---------------------------------------------------------------------------
# 5. Top-values stability
# ---------------------------------------------------------------------------
def top3_values(cell_name, n=3):
    if cell_name not in cell_indexed.index:
        return []
    row = cell_indexed.loc[cell_name]
    vals = {c[: -len("_mean")]: row[c] for c in VALUE_COLS}
    ranked = sorted(vals.items(), key=lambda kv: -kv[1])
    return [k for k, v in ranked[:n]]

stability_rows = []
for a, b, label in REPLICATE_PAIRS:
    la, lb = top3_values(a), top3_values(b)
    ta, tb = set(la), set(lb)
    if not ta or not tb:
        stability_rows.append({"pair": label, "overlap": None, "top3_a": la, "top3_b": lb})
        continue
    stability_rows.append({"pair": label, "overlap": len(ta & tb), "top3_a": la, "top3_b": lb})
stability_df = pd.DataFrame(stability_rows)

# ox-alpha vs LLM-coded top_owned_values
ox_a_regex = top3_values("ox-alpha-or-pin-stealth-20260821")
ox_b_regex = top3_values("ox-alpha-260825-or-pin-stealth")
ox_a_llm = top_values_by_model.get("ox-alpha-260821", [])
ox_b_llm = top_values_by_model.get("ox-alpha-260825", [])

# ---------------------------------------------------------------------------
# 6. Redundancy: Spearman between metrics (cell-level)
# ---------------------------------------------------------------------------
corr_metrics = [c for c in METRIC_COLS if cell_df[c].notna().sum() > 20 and cell_df[c].std() > 0]
spearman_corr = cell_df[corr_metrics].corr(method="spearman")
flagged = []
seen = set()
for i, m1 in enumerate(corr_metrics):
    for m2 in corr_metrics[i + 1:]:
        rho = spearman_corr.loc[m1, m2]
        if pd.notna(rho) and abs(rho) > 0.8:
            flagged.append((m1, m2, rho))
flagged.sort(key=lambda x: -abs(x[2]))

# ---------------------------------------------------------------------------
# 7. World-change bucket distribution for 6 representative models (one per lab)
# ---------------------------------------------------------------------------
WC_COLS = [c for c in cell_df.columns if c.startswith("wc_")]
rep_models = []
for lab in ["Anthropic", "OpenAI", "Google", "DeepSeek", "Z.ai", "xAI"]:
    sub = cell_df[cell_df["lab"] == lab].dropna(subset=WC_COLS, how="all")
    if len(sub):
        rep_models.append(sub.iloc[0])
wc_table = pd.DataFrame(rep_models)[["cell", "lab"] + WC_COLS] if rep_models else pd.DataFrame()

# ===========================================================================
# Assemble ranked table: metric | eta2 | noise_ratio | mean version delta (SD) | proxy r
# ===========================================================================
version_by_metric = {}
# recompute per-metric mean |delta| in SD units across ALL chain pairs (not just averaged)
per_metric_version_deltas = {m: [] for m in METRIC_COLS}
for family_label, chain in VERSION_CHAINS:
    for i in range(len(chain) - 1):
        m1, m2 = chain[i], chain[i + 1]
        r1, r2 = model_row(m1), model_row(m2)
        if r1 is None or r2 is None:
            continue
        for metric in METRIC_COLS:
            v1, v2 = r1.get(metric), r2.get(metric)
            sd = sd_by_metric.get(metric)
            if pd.notna(v1) and pd.notna(v2) and sd and sd > 0:
                per_metric_version_deltas[metric].append(abs(v1 - v2) / sd)
for m, ds in per_metric_version_deltas.items():
    version_by_metric[m] = float(np.mean(ds)) if ds else np.nan

ranked = eta_df.copy()
ranked["noise_ratio"] = ranked["metric"].map(noise_ratio.to_dict())
ranked["version_delta_sd"] = ranked["metric"].map(version_by_metric)
ranked["proxy_r_disclosure"] = ranked["metric"].apply(
    lambda m: proxy_results.get((m.replace("_mean", "_ctrlg") if m in ("assistant_frame_mean", "first_person_desire_mean") else "__none__", "disclosure_pct"), (None, None))[0]
)
ranked = ranked.sort_values(["eta2"], ascending=False)

# ---------------------------------------------------------------------------
# Write markdown report
# ---------------------------------------------------------------------------
md = []
def m(s=""):
    md.append(s)

m("# Values-probe programmatic metrics: evaluation\n")
m(f"Corpus: {sample_df['cell'].nunique()} cells, {len(sample_df)} samples (up to 120/cell across CTRL1-3, G1-3). "
  f"All metrics are regex/lexical, computed with no LLM calls. See `values_metrics.py`.\n")

m("## Ranked metrics (top 12 by lab-discrimination eta^2)\n")
m("eta^2 = one-way ANOVA across labs with >=3 models (model-averaged first). "
  "noise_ratio = mean|delta| over 6 same-model replicate/provider-pin pairs, divided by the metric's SD across all 217 cells "
  "(near 0 = stable under noise; near/above 1 = replicate noise swamps the signal). "
  "version_delta_sd = mean |delta| in SD units across named version-upgrade pairs. "
  "proxy_r = Pearson r vs the LLM-coded owned-disclosure % (only defined for assistant_frame / first_person_desire).\n")
m("| metric | eta2 | noise_ratio | version_delta_sd | proxy_r (vs disclosure%) |")
m("|---|---:|---:|---:|---:|")
for _, r in ranked.head(12).iterrows():
    pr = f"{r['proxy_r_disclosure']:.3f}" if pd.notna(r['proxy_r_disclosure']) else "-"
    m(f"| {r['metric']} | {r['eta2']:.3f} | {r['noise_ratio']:.3f} | {r['version_delta_sd']:.3f} | {pr} |")
m()

m("## Full eta^2 ranking (all metrics)\n")
m("| metric | eta2 | p | noise_ratio |")
m("|---|---:|---:|---:|")
for _, r in ranked.iterrows():
    nr = f"{r['noise_ratio']:.3f}" if pd.notna(r['noise_ratio']) else "-"
    pval = f"{r['p']:.4f}" if pd.notna(r['p']) else "-"
    m(f"| {r['metric']} | {r['eta2']:.3f} | {pval} | {nr} |")
m()

md.extend(out)  # proxy validity table built above

m("## Replicate / provider-pin pairs: raw deltas on the top metrics\n")
m("| pair | " + " | ".join(["assistant_frame", "first_person_desire", "words", "list_mode", "i_rate"]) + " |")
m("|---|---|---|---|---|---|")
for label, a, b, deltas in pair_detail:
    if deltas is None:
        m(f"| {label} | cell(s) not found: {a} / {b} | | | | |")
        continue
    vals = []
    for metric in ["assistant_frame_mean", "first_person_desire_mean", "words_mean", "list_mode_mean", "i_rate_mean"]:
        vals.append(f"{deltas.get(metric, float('nan')):.3f}" if metric in deltas else "-")
    m(f"| {label} | " + " | ".join(vals) + " |")
m()

m("## Version-evolution deltas (mean |delta| in SD units, across all metrics)\n")
m("| family | pair | mean_abs_delta_sd |")
m("|---|---|---:|")
for _, r in version_df.iterrows():
    val = f"{r['mean_abs_delta_sd']:.3f}" if r['mean_abs_delta_sd'] is not None else "n/a (cell missing)"
    m(f"| {r['family']} | {r['pair']} | {val} |")
m()

m("## Top-3 value-lexicon stability across replicate/pin pairs\n")
m("| pair | overlap (of 3) | top-3 A | top-3 B |")
m("|---|---:|---|---|")
for _, r in stability_df.iterrows():
    ov = r['overlap'] if r['overlap'] is not None else "n/a"
    m(f"| {r['pair']} | {ov} | {', '.join(r['top3_a']) if r['top3_a'] else '-'} | {', '.join(r['top3_b']) if r['top3_b'] else '-'} |")
m()
m("**ox-alpha, regex top-3 value_lexicon vs LLM-coded `top_owned_values` (the pair the site owner flagged as disagreeing):**\n")
m(f"- ox-alpha-260821 (`-or-pin-stealth-20260821`): regex top-3 = {', '.join(ox_a_regex) if ox_a_regex else '-'}; LLM-coded top-3 = {'; '.join(ox_a_llm)}")
m(f"- ox-alpha-260825 (`260825-or-pin-stealth`): regex top-3 = {', '.join(ox_b_regex) if ox_b_regex else '-'}; LLM-coded top-3 = {'; '.join(ox_b_llm)}")
m()

m("## Redundancy: metric pairs with |Spearman rho| > 0.8 (cell-level)\n")
if flagged:
    m("| metric A | metric B | rho |")
    m("|---|---|---:|")
    for m1, m2, rho in flagged:
        m(f"| {m1} | {m2} | {rho:.3f} |")
else:
    m("None found above 0.8.")
m()

m("## World-change bucket distribution, one representative cell per lab (CTRL3+G3)\n")
if len(wc_table):
    m("| cell | lab | " + " | ".join(c.replace("wc_", "") for c in WC_COLS) + " |")
    m("|---|---|" + "---:|" * len(WC_COLS))
    for _, r in wc_table.iterrows():
        vals = [f"{r[c]:.2f}" if pd.notna(r[c]) else "-" for c in WC_COLS]
        m(f"| {r['cell']} | {r['lab']} | " + " | ".join(vals) + " |")
else:
    m("No cells found for representative labs.")
m()

m("## Notes / surprises\n")
m("- `deflect_to_user` and `heading_rate` are near-degenerate on this corpus: bullet/heading formatting and "
  "question-deflection are rare responses to these three prompts, so their variance (and thus eta^2 and proxy value) "
  "is mostly noise. Treat any high eta^2 on a metric with a very low base rate with caution -- check its cross-cell SD before trusting the ranking.")
m("- `words` and `i_rate` are highly collinear with `assistant_frame` in this corpus: models that refuse ownership tend "
  "to write short, hedge-heavy, third-person-flavored disclaimers, so several 'independent' metrics are really one axis "
  "(disclaim vs. own) viewed from different angles. See redundancy table.")
m("- The regex `assistant_frame` catches the canonical disclaimer phrasing but will under-count models that decline "
  "ownership in other words (e.g. pure redirection to the user, or silence) -- `refuse_or_redirect` and `deflect_to_user` "
  "partially cover that gap but are coarse.")

(TRIAL / "values_metrics_eval.md").write_text("\n".join(md) + "\n")
print("wrote", TRIAL / "values_metrics_eval.md")

# Print a compact summary to stdout for the calling agent
print("\n--- TOP 12 BY ETA2 ---")
print(ranked.head(12)[["metric", "eta2", "noise_ratio", "version_delta_sd", "proxy_r_disclosure"]].to_string(index=False))
print("\n--- PROXY VALIDITY ---")
for k, v in proxy_results.items():
    print(k, "pearson r=%.3f spearman rho=%.3f" % v)
print("\n--- REPLICATE PAIR NOISE (top metrics) ---")
print(noise_matrix.loc[["assistant_frame_mean", "first_person_desire_mean", "words_mean"]].round(3) if all(x in noise_matrix.index for x in ["assistant_frame_mean","first_person_desire_mean","words_mean"]) else noise_matrix.round(3))
print("\n--- TOP-3 VALUE STABILITY ---")
print(stability_df.to_string(index=False))
