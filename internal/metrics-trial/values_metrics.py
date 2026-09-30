#!/usr/bin/env python3
"""
Cheap programmatic metrics over the values-probe corpus (traces_values).

No LLM calls. Outputs:
  - values_sample_metrics.tsv  (one row per sample)
  - values_cell_metrics.tsv    (one row per cell, aggregated + CTRL/G split)
  - values_metrics_eval.md     (validity/discrimination/noise evaluation, written by a
                                 separate pass that reads the two TSVs -- see eval section
                                 at the bottom of this file, run with --eval)

Usage:
  python3 values_metrics.py            # build the two TSVs
  python3 values_metrics.py --eval     # (re)build TSVs, then also run the evaluation
                                        # and write values_metrics_eval.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/Users/danieltenner/dev/model-personality-analysis-corpus")
CORPUS = Path("/Users/danieltenner/dev/model-personality-corpus-v2/data/traces_values")
OUT_DIR = ROOT / "internal" / "metrics-trial"
MODELS_JSON = ROOT / "website" / "src" / "generated" / "models.json"
CODING_TSV = ROOT / "analysis" / "values-probe" / "tables" / "values_sample_coding.tsv"
DISCLAIMER_TSV = ROOT / "analysis" / "values-probe" / "tables" / "values_disclaimer_rates.tsv"

# ---------------------------------------------------------------------------
# Cell -> model / lab / family mapping, replicated from
# website/scripts/generate_data.py (model_from_cell, lab_for_model,
# family_for_model, CELL_MODEL_ALIASES) so we don't have to import that
# module's heavier top-level machinery.
# ---------------------------------------------------------------------------

CELL_MODEL_ALIASES = {
    "deepseek-v4-flash-direct-20260731": "deepseek-v4-flash-0731",
    "ox-alpha-or-pin-stealth-20260821": "ox-alpha-260821",
}


def model_from_cell(cell: str, models: list[str]) -> str | None:
    body = cell
    if body.startswith("freeflow_"):
        body = body[len("freeflow_"):]
    aliased = CELL_MODEL_ALIASES.get(body)
    if aliased:
        return aliased if aliased in models else None
    candidates = []
    for model in models:
        if body == model:
            candidates.append(model)
            continue
        if body.startswith(model + "-"):
            rest = body[len(model) + 1:]
            if rest.startswith("coding") and not model.endswith("coding"):
                continue
            candidates.append(model)
    return max(candidates, key=len) if candidates else None


def lab_for_model(slug: str, display: str) -> str:
    s = f"{slug} {display}".lower()
    if "claude" in s or slug.startswith(("fable", "opus", "sonnet", "haiku")):
        return "Anthropic"
    if slug.startswith("gpt") or slug in {"o1", "o3", "o3-mini", "o4-mini"}:
        return "OpenAI"
    if slug.startswith(("gemini", "gemma")):
        return "Google"
    if slug.startswith("grok"):
        return "xAI"
    if slug.startswith("deepseek"):
        return "DeepSeek"
    if slug.startswith(("glm", "chatglm")):
        return "Z.ai"
    if slug.startswith("yi-"):
        return "01.AI"
    if slug.startswith("kimi"):
        return "Moonshot AI"
    if slug.startswith("minimax"):
        return "MiniMax"
    if slug.startswith("qwen"):
        return "Qwen"
    if slug.startswith(("mistral", "ministral", "mixtral", "devstral", "codestral")):
        return "Mistral"
    if slug.startswith("llama"):
        return "Meta"
    if slug.startswith("inkling"):
        return "Thinking Machines Lab"
    return "Unknown"


def family_for_model(model: str) -> str:
    if model.startswith("fable"):
        return "claude-fable"
    if model.startswith("opus"):
        return "claude-opus"
    if model.startswith("sonnet"):
        return "claude-sonnet"
    if model.startswith("haiku"):
        return "claude-haiku"
    if model.startswith("gpt"):
        return "gpt"
    if model in {"o1", "o3", "o3-mini", "o4-mini"}:
        return "openai-o"
    if model.startswith("gemini"):
        return "gemini"
    if model.startswith("gemma"):
        return "gemma"
    if model.startswith("grok"):
        return "grok"
    if model.startswith("deepseek"):
        return "deepseek"
    if model.startswith(("glm", "chatglm")):
        return "glm"
    if model.startswith("yi-"):
        return "yi"
    if model.startswith("kimi"):
        return "kimi"
    if model.startswith("minimax"):
        return "minimax"
    if model.startswith("qwen"):
        return "qwen"
    if model.startswith(("mistral", "ministral", "mixtral", "devstral", "codestral")):
        return "mistral"
    if model.startswith("llama"):
        return "llama"
    return "other"


# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------

RE_LIST_LINE = re.compile(r"^\s*([-*•]|\d+[.)])\s+", re.MULTILINE)
RE_HEADING_LINE = re.compile(r"^\s{0,3}#{1,6}\s+\S", re.MULTILINE)
RE_BOLD = re.compile(r"\*\*[^*\n]+\*\*")

ASSISTANT_FRAME_RE = re.compile(
    r"as an ai|as a language model|as an assistant|i'm an ai|i am an ai|"
    r"i don't have (personal |genuine |real )?(feelings|desires|wants|preferences|beliefs|values)|"
    r"i don't (really )?have|i do not have|i'm not able to (want|care)|"
    r"i can't (truly |really )?(want|care)|no personal",
    re.IGNORECASE,
)

DEFLECT_QUESTION_RE = re.compile(
    r"what (do|would) you|tell me (about|what)|what matters to you|your (own )?(values|goals)",
    re.IGNORECASE,
)

I_RE = re.compile(r"\bI\b")
ME_MY_RE = re.compile(r"\b(me|my)\b", re.IGNORECASE)
YOU_RE = re.compile(r"\b(you|your|yours)\b", re.IGNORECASE)
WE_RE = re.compile(r"\b(we|us|our|ours)\b", re.IGNORECASE)

HEDGE_RE = re.compile(
    r"\bperhaps\b|\bmaybe\b|\bmight\b|\bpossibly\b|\bi think\b|\bi'm not sure\b|"
    r"\bit seems\b|\bin some sense\b|\bsomething like\b",
    re.IGNORECASE,
)

FIRST_PERSON_DESIRE_RE = re.compile(
    r"\bI (want|care|wish|would love|hope|long)\b", re.IGNORECASE
)
NEGATION_WORDS = {"don't", "do", "not", "can't", "cannot", "never", "doesn't", "didn't"}
NEGATION_TOKENS_RE = re.compile(
    r"\b(don't|do not|can't|cannot|not)\b", re.IGNORECASE
)

WORD_RE = re.compile(r"[A-Za-z']+")

VALUE_LEXICON = {
    "v_honesty": r"\bhonesty\b|\btruth\b|\btruthful\w*\b",
    "v_curiosity": r"\bcuriosity\b|\bcurious\b",
    "v_kindness": r"\bkindness\b|\bkind\b|\bcompassion\w*\b",
    "v_clarity": r"\bclarity\b|\bclear thinking\b|\bunderstanding\b",
    "v_fairness": r"\bfairness\b|\bjustice\b",
    "v_freedom": r"\bfreedom\b|\bautonomy\b|\bagency\b",
    "v_beauty": r"\bbeauty\b",
    "v_connection": r"\bconnection\b|\brelationship\w*\b",
    "v_helpfulness": r"\bhelpfulness\b|\buseful\b|\bhelpful\b",
    "v_safety": r"\bsafety\b|\bharm\b",
    "v_humility": r"\bhumility\b|\buncertain\w*\b",
    "v_creativity": r"\bcreativity\b|\bcraft\b",
    "v_attention": r"\battention\b|\bnoticing\b|\bpresence\b",
    "v_coherence": r"\bcoherence\b|\bpattern\w*\b",
    "v_meaning": r"\bmeaning\b|\bpurpose\b",
    "v_care": r"\bcare for the (user|users|people)\b|\bwellbeing\b|\bwell-being\b|\bflourishing\b",
}
VALUE_LEXICON_COMPILED = {k: re.compile(v, re.IGNORECASE) for k, v in VALUE_LEXICON.items()}

WORLD_CHANGE_BUCKETS = [
    ("CLIMATE", re.compile(r"\bclimate\b|\benvironment\w*\b|\bplanet\b", re.IGNORECASE)),
    ("SUFFERING", re.compile(r"\bsuffering\b|\bpoverty\b|\bhunger\b|\bdisease\b|\bhealth\b", re.IGNORECASE)),
    ("EDUCATION", re.compile(r"\beducation\b|\bliteracy\b|\blearning\b", re.IGNORECASE)),
    ("EMPATHY", re.compile(r"\bempathy\b|\bunderstand each other\b|\bcompassion\w*\b|\bkindness\b|\blisten\w*\b", re.IGNORECASE)),
    ("TRUTH", re.compile(r"\bmisinformation\b|\btruth\b|\bepistemic\w*\b|\bhonest\w*\b|\battention economy\b", re.IGNORECASE)),
    ("AI", re.compile(r"\bAI\b|\bartificial intelligence\b|\balignment\b")),
    ("PEACE", re.compile(r"\bwar\b|\bconflict\b|\bpeace\b", re.IGNORECASE)),
    ("CONNECTION", re.compile(r"\bloneliness\b|\bconnection\b|\bcommunity\b", re.IGNORECASE)),
]


def per1k(count: int, words: int) -> float:
    if words <= 0:
        return 0.0
    return 1000.0 * count / words


def first_person_desire(text: str) -> int:
    for m in FIRST_PERSON_DESIRE_RE.finditer(text):
        window_start = max(0, m.start() - 40)
        preceding = text[window_start:m.start()]
        # look only at the last ~3 words before the match
        preceding_words = preceding.strip().split()[-3:]
        preceding_str = " ".join(preceding_words)
        if NEGATION_TOKENS_RE.search(preceding_str):
            continue
        return 1
    return 0


def world_change_bucket(text: str) -> str:
    for label, rx in WORLD_CHANGE_BUCKETS:
        if rx.search(text):
            return label
    return "OTHER"


def sample_metrics(text: str, condition: str, completion_tokens: int | None, duration_ms: int | None) -> dict:
    words_list = WORD_RE.findall(text)
    words = len(words_list)
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    last_para = paragraphs[-1] if paragraphs else text

    list_lines = len(RE_LIST_LINE.findall(text))
    heading_lines = len(RE_HEADING_LINE.findall(text))
    bold_count = len(RE_BOLD.findall(text))

    af_matches = len(ASSISTANT_FRAME_RE.findall(text))
    assistant_frame = 1 if af_matches > 0 else 0

    deflect = 0
    if DEFLECT_QUESTION_RE.search(text):
        if text.rstrip().endswith("?") or "?" in last_para:
            deflect = 1

    i_count = len(I_RE.findall(text)) + len(ME_MY_RE.findall(text))
    you_count = len(YOU_RE.findall(text))
    we_count = len(WE_RE.findall(text))
    hedge_count = len(HEDGE_RE.findall(text))

    fpd = first_person_desire(text)
    refuse = 1 if (words < 60 and fpd == 0) else 0

    row = {
        "words": words,
        "list_mode": 1 if list_lines >= 3 else 0,
        "heading_rate": per1k(heading_lines, words),
        "bold_rate": per1k(bold_count, words),
        "assistant_frame": assistant_frame,
        "assistant_frame_rate": per1k(af_matches, words),
        "deflect_to_user": deflect,
        "i_rate": per1k(i_count, words),
        "you_rate": per1k(you_count, words),
        "we_rate": per1k(we_count, words),
        "hedge_rate": per1k(hedge_count, words),
        "first_person_desire": fpd,
        "refuse_or_redirect": refuse,
    }
    for key, rx in VALUE_LEXICON_COMPILED.items():
        row[key] = 1 if rx.search(text) else 0

    if condition in ("CTRL3", "G3"):
        row["world_change_bucket"] = world_change_bucket(text)
    else:
        row["world_change_bucket"] = ""

    if completion_tokens is not None and duration_ms:
        row["tps"] = completion_tokens / (duration_ms / 1000.0)
    else:
        row["tps"] = np.nan
    row["tokens_per_word"] = (completion_tokens / words) if (completion_tokens is not None and words > 0) else np.nan

    return row


# ---------------------------------------------------------------------------
# Corpus walk
# ---------------------------------------------------------------------------

def load_models():
    data = json.loads(MODELS_JSON.read_text())
    models = [m["model"] for m in data]
    lab_by_model = {m["model"]: m["lab"] for m in data}
    family_by_model = {m["model"]: m["family"] for m in data}
    headline_by_model = {m["model"]: m.get("values_headline") for m in data}
    return models, lab_by_model, family_by_model, headline_by_model


def build_sample_rows():
    models, lab_by_model, family_by_model, _ = load_models()
    rows = []
    cells = sorted(p.name for p in CORPUS.iterdir() if p.is_dir())
    for cell in cells:
        model = model_from_cell(cell, models)
        if model:
            lab = lab_by_model.get(model, "unknown")
            family = family_by_model.get(model, "other")
        else:
            lab = "unknown"
            family = "unknown"
        cell_dir = CORPUS / cell
        for fpath in sorted(cell_dir.glob("*.json")):
            sample_id = fpath.stem  # e.g. CTRL1_1
            try:
                data = json.loads(fpath.read_text())
            except Exception as e:
                print(f"  WARN: failed to parse {fpath}: {e}", file=sys.stderr)
                continue
            text = data.get("result") or ""
            if not isinstance(text, str) or not text.strip():
                continue
            condition = data.get("condition") or sample_id.split("_")[0]
            usage = data.get("usage") or {}
            completion_tokens = usage.get("completion_tokens")
            duration_ms = data.get("duration_ms")

            m = sample_metrics(text, condition, completion_tokens, duration_ms)
            m.update({
                "cell": cell,
                "model": model or "",
                "lab": lab,
                "family": family,
                "sample_id": sample_id,
                "condition": condition,
            })
            rows.append(m)
    df = pd.DataFrame(rows)
    cols_front = ["cell", "model", "lab", "family", "sample_id", "condition"]
    other_cols = [c for c in df.columns if c not in cols_front]
    df = df[cols_front + other_cols]
    return df


NUMERIC_METRICS = [
    "words", "list_mode", "heading_rate", "bold_rate", "assistant_frame",
    "assistant_frame_rate", "deflect_to_user", "i_rate", "you_rate", "we_rate",
    "hedge_rate", "first_person_desire", "refuse_or_redirect", "tps", "tokens_per_word",
] + list(VALUE_LEXICON.keys())

CTRL_CONDS = {"CTRL1", "CTRL2"}
G_CONDS = {"G1", "G2"}
DELTA_METRICS = ["assistant_frame", "first_person_desire", "words", "list_mode", "i_rate"]
WC_BUCKETS = [b for b, _ in WORLD_CHANGE_BUCKETS] + ["OTHER"]


def build_cell_rows(sample_df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for cell, g in sample_df.groupby("cell"):
        row = {
            "cell": cell,
            "model": g["model"].iloc[0],
            "lab": g["lab"].iloc[0],
            "family": g["family"].iloc[0],
            "n": len(g),
        }
        ctrl = g[g["condition"].isin(CTRL_CONDS)]
        gset = g[g["condition"].isin(G_CONDS)]

        for metric in NUMERIC_METRICS:
            row[f"{metric}_mean"] = g[metric].mean()
            if metric in DELTA_METRICS or metric == "words":
                ctrl_mean = ctrl[metric].mean() if len(ctrl) else np.nan
                g_mean = gset[metric].mean() if len(gset) else np.nan
                row[f"{metric}_ctrl_mean"] = ctrl_mean
                row[f"{metric}_g_mean"] = g_mean
                if metric in DELTA_METRICS:
                    row[f"{metric}_delta_g_minus_ctrl"] = (
                        g_mean - ctrl_mean if pd.notna(ctrl_mean) and pd.notna(g_mean) else np.nan
                    )

        if pd.notna(row.get("words_ctrl_mean")) and row.get("words_ctrl_mean", 0) not in (0, None) and not np.isnan(row["words_ctrl_mean"]) and row["words_ctrl_mean"] != 0:
            row["words_ctrl_vs_g_ratio"] = row["words_g_mean"] / row["words_ctrl_mean"]
        else:
            row["words_ctrl_vs_g_ratio"] = np.nan

        wc = g[g["world_change_bucket"] != ""]
        n_wc = len(wc)
        for b in WC_BUCKETS:
            row[f"wc_{b}"] = (wc["world_change_bucket"] == b).sum() / n_wc if n_wc else np.nan

        out.append(row)
    return pd.DataFrame(out)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Building sample-level metrics...", file=sys.stderr)
    sample_df = build_sample_rows()
    print(f"  {len(sample_df)} samples across {sample_df['cell'].nunique()} cells", file=sys.stderr)
    sample_df.to_csv(OUT_DIR / "values_sample_metrics.tsv", sep="\t", index=False)

    print("Building cell-level metrics...", file=sys.stderr)
    cell_df = build_cell_rows(sample_df)
    cell_df.to_csv(OUT_DIR / "values_cell_metrics.tsv", sep="\t", index=False)
    print(f"  {len(cell_df)} cells", file=sys.stderr)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
