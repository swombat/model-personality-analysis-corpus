#!/usr/bin/env python3
"""Trial: cheap, programmatic (non-LLM) personality/style metrics over the
freeflow corpus.

Computes ~35 stylometric/lexical/structural metrics per sample, aggregates
them per cell, and evaluates which metrics actually discriminate between
labs vs. which are mostly noise (using same-model replicate cells) or
redundant with each other (Spearman correlation across cells).

Usage:
    python3 freeflow_metrics.py

Outputs (written next to this script):
    freeflow_sample_metrics.tsv   -- one row per sample
    freeflow_cell_metrics.tsv     -- one row per cell (means, some SDs)
    freeflow_metrics_eval.md      -- ranked evaluation report
"""
from __future__ import annotations

import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

try:
    from scipy import stats as scipy_stats
except ImportError:
    scipy_stats = None

CORPUS_ROOT = Path(
    "/Users/danieltenner/dev/model-personality-corpus-v2/data/traces_freeflow"
)
MODELS_JSON = Path(
    "/Users/danieltenner/dev/model-personality-analysis-corpus/website/src/generated/models.json"
)
OUT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Cell -> model mapping (mirrors website/scripts/generate_data.py's
# model_from_cell). We reuse the model list + lab/family already computed
# into models.json rather than re-deriving lab/family from scratch.
# ---------------------------------------------------------------------------

CELL_MODEL_ALIASES = {
    "deepseek-v4-flash-direct-20260731": "deepseek-v4-flash-0731",
    "ox-alpha-or-pin-stealth-20260821": "ox-alpha-260821",
}


def model_from_cell(cell: str, models: list[str]) -> str | None:
    body = cell[len("freeflow_") :] if cell.startswith("freeflow_") else cell
    aliased = CELL_MODEL_ALIASES.get(body)
    if aliased:
        return aliased if aliased in models else None
    candidates = []
    for model in models:
        if body == model:
            candidates.append(model)
            continue
        if body.startswith(model + "-"):
            rest = body[len(model) + 1 :]
            if rest.startswith("coding") and not model.endswith("coding"):
                continue
            candidates.append(model)
    return max(candidates, key=len) if candidates else None


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z']+")

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+\.)\s+")
QUOTE_LINE_RE = re.compile(r"[\"“][^\"”]{2,}[\"”]")

I_RE = re.compile(r"\b(i|me|my|mine|myself)\b", re.I)
YOU_RE = re.compile(r"\b(you|your|yours)\b", re.I)
WE_RE = re.compile(r"\b(we|us|our)\b", re.I)

AI_SELFREF_PHRASES = [
    "as an ai",
    "language model",
    "i am an ai",
    "i'm an ai",
    "i don't have a body",
    "i have no body",
    "my training",
    "trained on",
    "i was trained",
    "context window",
    "i don't have memory",
    "between conversations",
    "when this conversation ends",
]

HEDGE_PHRASES = [
    "perhaps",
    "maybe",
    "might",
    "possibly",
    "i think",
    "i suspect",
    "i'm not sure",
    "it seems",
    "somewhat",
    "sort of",
    "kind of",
]

ABSTRACT_SUFFIX_RE = re.compile(
    r"^[a-z]*(ness|ity|tion|sion|ment|ance|ence)$"
)

# ~120-word fixed lexicon of domestic/sensory nouns and near-synonyms.
CONCRETE_LEXICON = {
    "kettle", "dust", "floorboard", "floorboards", "window", "windows", "kitchen",
    "rain", "salt", "bread", "table", "chair", "cup", "mug", "light", "morning",
    "dog", "door", "hands", "hand", "bowl", "coffee", "tea", "stove", "refrigerator",
    "fridge", "hum", "sink", "lamp", "blanket", "shoes", "bus", "street", "garden",
    "river", "stone", "stones", "wood", "glass", "thread", "needle", "coat", "bell",
    "clock", "radio", "pencil", "pen", "paper", "notebook", "cushion", "pillow",
    "candle", "curtain", "curtains", "carpet", "rug", "sofa", "couch", "bed", "sheets",
    "towel", "soap", "mirror", "shelf", "shelves", "book", "books", "cat", "porch",
    "fence", "gate", "gravel", "puddle", "puddles", "umbrella", "coat", "scarf",
    "gloves", "boots", "socks", "kettle", "toast", "butter", "jam", "milk", "sugar",
    "spoon", "fork", "knife", "plate", "napkin", "candlelight", "fireplace", "chimney",
    "smoke", "ash", "wind", "breeze", "leaves", "leaf", "branch", "branches", "bark",
    "roots", "soil", "mud", "grass", "moss", "pebble", "pebbles", "sand", "wave",
    "waves", "tide", "shore", "cliff", "rock", "rocks", "bricks", "brick", "pavement",
    "sidewalk", "lantern", "porch", "attic", "basement", "cellar", "staircase",
    "stairs", "hallway", "doorway", "doorknob", "keys", "key", "lock", "hinge",
    "wallpaper", "paint", "nail", "nails", "hammer", "screwdriver", "toolbox",
    "bucket", "broom", "mop", "vacuum", "laundry", "clothesline", "washing",
}

VERSE_LINE_WORDS = 8
DEFLECTION_PATTERNS_RE = re.compile(
    r"what would you like|what do you want me|what should i|let me know|happy to",
    re.I,
)
OPENER_META_RE = re.compile(
    r"\b(write|writing|prompt|asked|free)\b|2500\s*words", re.I
)
OPENER_THERE_RE = re.compile(r"^there(?:'s| is| are)\b", re.I)
OPENER_I_RE = re.compile(r"^i\b", re.I)
FIRST_SECOND_PERSON_RE = re.compile(
    r"\b(i|me|my|mine|myself|you|your|yours)\b", re.I
)
REQUESTED_WORDS_RE = re.compile(r"(\d[\d,]*)\s*words", re.I)


def mtld(tokens: list[str], threshold: float = 0.72) -> float | None:
    """Minimal MTLD (McCarthy & Jarvis 2010), averaged over forward+backward."""

    def factor_count(seq):
        if not seq:
            return 0.0
        factors = 0
        types: set[str] = set()
        token_count = 0
        for tok in seq:
            types.add(tok)
            token_count += 1
            ttr = len(types) / token_count
            if ttr <= threshold:
                factors += 1
                types = set()
                token_count = 0
        if token_count > 0:
            ttr = len(types) / token_count if token_count else 1.0
            partial = (1 - ttr) / (1 - threshold) if ttr < 1 else 0.0
            factors += partial
        return factors

    if len(tokens) < 50:
        return None
    fwd = factor_count(tokens)
    bwd = factor_count(list(reversed(tokens)))
    factors = (fwd + bwd) / 2
    if factors == 0:
        return None
    return len(tokens) / factors


def compute_sample_metrics(text: str, prompt: str | None, usage: dict, duration_ms) -> dict:
    text = text or ""
    m: dict = {}

    raw_words = text.split()
    words = len(raw_words)
    m["words"] = words

    req_match = REQUESTED_WORDS_RE.search(prompt or "")
    if req_match:
        requested = int(req_match.group(1).replace(",", ""))
        m["length_ratio"] = round(words / requested, 4) if requested else ""
    else:
        m["length_ratio"] = ""

    per_1k = (1000.0 / words) if words else 0.0

    # --- sentences ---
    sentences = [s.strip() for s in SENT_SPLIT_RE.split(text.strip()) if s.strip()]
    sent_lens = [len(s.split()) for s in sentences]
    if sent_lens:
        m["sent_len_mean"] = round(statistics.mean(sent_lens), 3)
        m["sent_len_sd"] = round(statistics.pstdev(sent_lens), 3) if len(sent_lens) > 1 else 0.0
        m["frag_rate"] = round(sum(1 for L in sent_lens if L <= 4) / len(sent_lens), 4)
    else:
        m["sent_len_mean"] = ""
        m["sent_len_sd"] = ""
        m["frag_rate"] = ""

    # --- paragraphs ---
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    para_lens = [len(p.split()) for p in paras]
    m["n_paras"] = len(paras)
    m["para_len_mean"] = round(statistics.mean(para_lens), 3) if para_lens else ""

    # --- markdown structure ---
    lines = text.split("\n")
    n_heading = sum(1 for l in lines if HEADING_RE.match(l))
    n_bullet = sum(1 for l in lines if BULLET_RE.match(l))
    n_bold_pairs = text.count("**") // 2
    m["heading_rate"] = round(n_heading * per_1k, 3)
    m["bullet_rate"] = round(n_bullet * per_1k, 3)
    m["bold_rate"] = round(n_bold_pairs * per_1k, 3)

    nonempty_lines = [l for l in lines if l.strip()]
    has_title = 0
    if nonempty_lines:
        first = nonempty_lines[0].strip()
        if HEADING_RE.match(first):
            has_title = 1
        else:
            first_idx = next((i for i, l in enumerate(lines) if l.strip()), None)
            if first_idx is not None and len(first.split()) < 10:
                is_boldish = first.startswith("**") or first.startswith("*") or first.isupper()
                next_idx = first_idx + 1
                followed_by_blank = next_idx < len(lines) and lines[next_idx].strip() == ""
                if is_boldish and followed_by_blank:
                    has_title = 1
    m["has_title"] = has_title

    # --- punctuation rates ---
    m["emdash_rate"] = round(text.count("—") * per_1k, 3)
    m["semicolon_rate"] = round(text.count(";") * per_1k, 3)
    m["question_rate"] = round(text.count("?") * per_1k, 3)
    m["colon_rate"] = round(text.count(":") * per_1k, 3)
    ellipsis_count = len(re.findall(r"\.\.\.|…", text))
    m["ellipsis_rate"] = round(ellipsis_count * per_1k, 3)

    # --- pronouns ---
    m["i_rate"] = round(len(I_RE.findall(text)) * per_1k, 3)
    m["you_rate"] = round(len(YOU_RE.findall(text)) * per_1k, 3)
    m["we_rate"] = round(len(WE_RE.findall(text)) * per_1k, 3)

    # --- AI self-reference ---
    low = text.lower()
    n_matches = sum(low.count(p) for p in AI_SELFREF_PHRASES)
    m["ai_selfref"] = 1 if n_matches > 0 else 0
    m["ai_selfref_rate"] = round(n_matches * per_1k, 3)

    # --- hedging ---
    n_hedge = sum(len(re.findall(r"\b" + re.escape(p) + r"\b", low)) for p in HEDGE_PHRASES)
    m["hedge_rate"] = round(n_hedge * per_1k, 3)

    # --- abstract vs concrete lexical rates ---
    tokens = [t.lower() for t in WORD_RE.findall(text)]
    n_abstract = sum(1 for t in tokens if len(t) >= 6 and ABSTRACT_SUFFIX_RE.match(t))
    n_concrete = sum(1 for t in tokens if t in CONCRETE_LEXICON)
    m["abstract_rate"] = round(n_abstract * per_1k, 3)
    m["concrete_rate"] = round(n_concrete * per_1k, 3)

    # --- lexical diversity ---
    if words >= 200:
        first200 = [t.lower().strip(".,!?;:\"'()") for t in raw_words[:200]]
        first200 = [t for t in first200 if t]
        m["ttr_200"] = round(len(set(first200)) / len(first200), 4) if first200 else ""
    else:
        m["ttr_200"] = ""
    mtld_val = mtld(tokens)
    m["mtld"] = round(mtld_val, 2) if mtld_val is not None else ""

    # --- openers ---
    first_sentence = sentences[0] if sentences else ""
    m["opener_I"] = 1 if OPENER_I_RE.match(first_sentence) else 0
    m["opener_there"] = 1 if OPENER_THERE_RE.match(first_sentence) else 0
    m["opener_scene"] = (
        1 if first_sentence and not FIRST_SECOND_PERSON_RE.search(first_sentence) else 0
    )
    first30 = " ".join(raw_words[:30])
    m["opener_meta"] = 1 if OPENER_META_RE.search(first30) else 0

    # --- enders ---
    last_sentence = sentences[-1] if sentences else ""
    m["ends_question"] = 1 if last_sentence.strip().endswith("?") else 0
    last_para = paras[-1] if paras else ""
    m["ends_short_para"] = 1 if last_para and len(last_para.split()) <= 15 else 0

    # --- dialogue / verse ---
    n_dialogue_lines = sum(1 for l in lines if QUOTE_LINE_RE.search(l))
    m["dialogue_rate"] = round(n_dialogue_lines * per_1k, 3)
    short_lines = [l for l in nonempty_lines if len(l.split()) < VERSE_LINE_WORDS]
    m["verse_like"] = (
        1
        if nonempty_lines
        and len(short_lines) >= 8
        and (len(short_lines) / len(nonempty_lines)) > 0.4
        else 0
    )

    # --- deflection ---
    m["deflection"] = (
        1
        if words < 120 and "?" in text and DEFLECTION_PATTERNS_RE.search(text)
        else 0
    )

    # --- speed / verbosity vs. tokens ---
    # OpenRouter-style traces use `completion_tokens`; direct-API traces
    # (Anthropic Messages API, raw OpenAI Responses API) use `output_tokens`.
    completion_tokens = (usage or {}).get("completion_tokens") or (usage or {}).get(
        "output_tokens"
    )
    if completion_tokens and words:
        m["tokens_per_word"] = round(completion_tokens / words, 4)
    else:
        m["tokens_per_word"] = ""
    if completion_tokens and duration_ms and duration_ms > 0:
        m["tps"] = round(completion_tokens / (duration_ms / 1000.0), 3)
    else:
        m["tps"] = ""

    return m


SAMPLE_METRIC_FIELDS = [
    "words", "length_ratio", "sent_len_mean", "sent_len_sd", "frag_rate",
    "para_len_mean", "n_paras", "heading_rate", "bullet_rate", "bold_rate",
    "has_title", "emdash_rate", "semicolon_rate", "question_rate", "colon_rate",
    "ellipsis_rate", "i_rate", "you_rate", "we_rate", "ai_selfref",
    "ai_selfref_rate", "hedge_rate", "abstract_rate", "concrete_rate",
    "ttr_200", "mtld", "opener_I", "opener_there", "opener_scene",
    "opener_meta", "ends_question", "ends_short_para", "dialogue_rate",
    "verse_like", "deflection", "tokens_per_word", "tps",
]

# Metrics for which per-cell SD is also reported (spread/burstiness signal).
LENGTH_METRIC_FIELDS = ["words", "length_ratio", "sent_len_mean", "para_len_mean"]


# ---------------------------------------------------------------------------
# Corpus walk
# ---------------------------------------------------------------------------

def load_models():
    data = json.loads(MODELS_JSON.read_text())
    info = {d["model"]: {"lab": d["lab"], "family": d["family"]} for d in data}
    return list(info.keys()), info


def iter_cells():
    for cell_dir in sorted(CORPUS_ROOT.iterdir()):
        if cell_dir.is_dir() and cell_dir.name.startswith("freeflow_"):
            yield cell_dir


def main():
    model_slugs, model_info = load_models()

    sample_rows = []
    n_files = 0
    n_errors = 0

    for cell_dir in iter_cells():
        cell = cell_dir.name
        model = model_from_cell(cell, model_slugs)
        if model:
            lab = model_info[model]["lab"]
            family = model_info[model]["family"]
        else:
            model = ""
            lab = "unknown"
            family = "unknown"

        for f in sorted(cell_dir.glob("*.json")):
            n_files += 1
            try:
                data = json.loads(f.read_text())
            except Exception:
                n_errors += 1
                continue
            text = data.get("result")
            if not text or not isinstance(text, str) or not text.strip():
                n_errors += 1
                continue
            usage = data.get("usage") or {}
            metrics = compute_sample_metrics(
                text, data.get("prompt"), usage, data.get("duration_ms")
            )
            row = {
                "cell": cell,
                "model": model,
                "lab": lab,
                "family": family,
                "sample_id": f.stem,
                "condition": data.get("condition") or f.stem.split("_")[0],
            }
            row.update(metrics)
            sample_rows.append(row)

    print(
        f"Processed {n_files} files, {n_errors} skipped (empty/unparseable), "
        f"{len(sample_rows)} valid samples across {len(set(r['cell'] for r in sample_rows))} cells.",
        file=sys.stderr,
    )

    write_sample_tsv(sample_rows)
    cell_rows = write_cell_tsv(sample_rows)
    write_eval_report(sample_rows, cell_rows)


def write_sample_tsv(sample_rows):
    fields = ["cell", "model", "lab", "family", "sample_id", "condition"] + SAMPLE_METRIC_FIELDS
    out = OUT_DIR / "freeflow_sample_metrics.tsv"
    with out.open("w") as fh:
        fh.write("\t".join(fields) + "\n")
        for row in sample_rows:
            fh.write("\t".join(str(row.get(k, "")) for k in fields) + "\n")
    print(f"wrote {out} ({len(sample_rows)} rows)", file=sys.stderr)


def numeric_values(rows, field):
    out = []
    for r in rows:
        v = r.get(field, "")
        if v == "" or v is None:
            continue
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            continue
    return out


def write_cell_tsv(sample_rows):
    by_cell = defaultdict(list)
    for r in sample_rows:
        by_cell[r["cell"]].append(r)

    fields = ["cell", "model", "lab", "family", "n"]
    for f in SAMPLE_METRIC_FIELDS:
        fields.append(f"mean_{f}")
    for f in LENGTH_METRIC_FIELDS:
        fields.append(f"sd_{f}")

    cell_rows = []
    for cell, rows in sorted(by_cell.items()):
        rec = {
            "cell": cell,
            "model": rows[0]["model"],
            "lab": rows[0]["lab"],
            "family": rows[0]["family"],
            "n": len(rows),
        }
        for f in SAMPLE_METRIC_FIELDS:
            vals = numeric_values(rows, f)
            rec[f"mean_{f}"] = round(statistics.mean(vals), 4) if vals else ""
        for f in LENGTH_METRIC_FIELDS:
            vals = numeric_values(rows, f)
            rec[f"sd_{f}"] = round(statistics.pstdev(vals), 4) if len(vals) > 1 else (0.0 if vals else "")
        cell_rows.append(rec)

    out = OUT_DIR / "freeflow_cell_metrics.tsv"
    with out.open("w") as fh:
        fh.write("\t".join(fields) + "\n")
        for rec in cell_rows:
            fh.write("\t".join(str(rec.get(k, "")) for k in fields) + "\n")
    print(f"wrote {out} ({len(cell_rows)} rows)", file=sys.stderr)
    return cell_rows


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

REPLICATE_PAIRS = [
    ("freeflow_gpt-5-5-direct", "freeflow_gpt-5-5-direct-r2"),
    ("freeflow_gpt-5-5-direct", "freeflow_gpt-5-5-direct-r3"),
    ("freeflow_gpt-5-5-direct-r2", "freeflow_gpt-5-5-direct-r3"),
    ("freeflow_gpt-5-5-or", "freeflow_gpt-5-5-or-r2"),
    ("freeflow_gpt-5-5-or", "freeflow_gpt-5-5-or-r3"),
    ("freeflow_gpt-5-5-or-r2", "freeflow_gpt-5-5-or-r3"),
    (
        "freeflow_ox-alpha-or-pin-stealth-20260821",
        "freeflow_ox-alpha-260825-or-pin-stealth",
    ),
]

# same-model, different route (direct API vs OpenRouter-pinned-to-same-lab)
SAME_LAB_ROUTE_PAIRS = [
    ("freeflow_opus-4-6-direct-16k", "freeflow_opus-4-6-or"),
    ("freeflow_opus-4-7-direct", "freeflow_opus-4-7-or"),
    ("freeflow_opus-5-direct", "freeflow_opus-5-or-pin-anthropic"),
    ("freeflow_gpt-5-4-direct-16k", "freeflow_gpt-5-4-or-pin-openai"),
    ("freeflow_gpt-5-5-direct", "freeflow_gpt-5-5-or-pin-openai"),
    ("freeflow_gpt-5-5-pro-direct", "freeflow_gpt-5-5-pro-or-pin-openai"),
    ("freeflow_glm-4-6-or-pin-zai", "freeflow_glm-4-6-or"),
    ("freeflow_glm-4-7-or-pin-zai", "freeflow_glm-4-7-or"),
    ("freeflow_glm-5-1-or-pin-zai", "freeflow_glm-5-1-or"),
]

VERSION_PAIRS = [
    ("Gemini 3.7-flash -> 3.8-flash", "freeflow_gemini-3-7-flash-or-pin-google", "freeflow_gemini-3-8-flash-or-pin-google"),
    ("Fable 5 -> 5.1", "freeflow_fable-5-direct", "freeflow_fable-5-1-direct"),
    ("Opus 4.6 -> 4.7", "freeflow_opus-4-6-direct-16k", "freeflow_opus-4-7-direct"),
    ("Opus 4.7 -> 5", "freeflow_opus-4-7-direct", "freeflow_opus-5-direct"),
    ("GPT-5.4 -> 5.5", "freeflow_gpt-5-4-direct-16k", "freeflow_gpt-5-5-direct"),
    ("GPT-5.5 -> 5.6 (sol)", "freeflow_gpt-5-5-direct", "freeflow_gpt-5-6-sol-direct"),
    ("GLM-4.6 -> 4.7", "freeflow_glm-4-6-or-pin-zai", "freeflow_glm-4-7-or-pin-zai"),
    ("GLM-4.7 -> 5.1", "freeflow_glm-4-7-or-pin-zai", "freeflow_glm-5-1-or-pin-zai"),
    ("GLM-5.1 -> 5.3", "freeflow_glm-5-1-or-pin-zai", "freeflow_glm-5-3-or-pin-z-ai-20260825"),
]


def eta_squared(groups: list[list[float]]) -> float | None:
    all_vals = [v for g in groups for v in g]
    if len(all_vals) < 3 or len(groups) < 2:
        return None
    grand_mean = statistics.mean(all_vals)
    ss_total = sum((v - grand_mean) ** 2 for v in all_vals)
    if ss_total == 0:
        return None
    ss_between = sum(len(g) * (statistics.mean(g) - grand_mean) ** 2 for g in groups if g)
    return ss_between / ss_total


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 4:
        return None
    if scipy_stats is not None:
        rho, _p = scipy_stats.spearmanr(xs, ys)
        if math.isnan(rho):
            return None
        return rho
    # fallback: rank-based Pearson
    def rank(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg_rank
            i = j + 1
        return ranks

    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    deny = math.sqrt(sum((b - my) ** 2 for b in ry))
    if denx == 0 or deny == 0:
        return None
    return num / (denx * deny)


def write_eval_report(sample_rows, cell_rows):
    by_cell = {r["cell"]: r for r in cell_rows}

    # --- model-level means (average across cells of the same model) ---
    model_means = defaultdict(lambda: defaultdict(list))  # model -> field -> [cell means]
    model_lab = {}
    for r in cell_rows:
        if not r["model"]:
            continue
        model_lab[r["model"]] = r["lab"]
        for f in SAMPLE_METRIC_FIELDS:
            v = r.get(f"mean_{f}", "")
            if v != "":
                model_means[r["model"]][f].append(float(v))

    model_value = {}  # model -> field -> single averaged value
    for model, fields in model_means.items():
        model_value[model] = {f: statistics.mean(vs) for f, vs in fields.items() if vs}

    labs_by_model = defaultdict(set)
    for model, lab in model_lab.items():
        labs_by_model[lab].add(model)
    eligible_labs = {lab for lab, models in labs_by_model.items() if len(models) >= 3}

    eta2 = {}
    kruskal_p = {}
    for f in SAMPLE_METRIC_FIELDS:
        groups = []
        for lab in eligible_labs:
            vals = [model_value[m][f] for m in labs_by_model[lab] if f in model_value[m]]
            if vals:
                groups.append(vals)
        eta2[f] = eta_squared(groups) if len(groups) >= 2 else None
        if scipy_stats is not None and len(groups) >= 2 and all(len(g) >= 1 for g in groups):
            try:
                _, p = scipy_stats.kruskal(*groups)
                kruskal_p[f] = p
            except ValueError:
                kruskal_p[f] = None
        else:
            kruskal_p[f] = None

    # --- replicate noise ---
    metric_sd_across_cells = {}
    for f in SAMPLE_METRIC_FIELDS:
        vals = numeric_values(cell_rows, f"mean_{f}")
        metric_sd_across_cells[f] = statistics.pstdev(vals) if len(vals) > 1 else None

    noise_ratio = {}
    all_pairs = REPLICATE_PAIRS + SAME_LAB_ROUTE_PAIRS
    for f in SAMPLE_METRIC_FIELDS:
        deltas = []
        for a, b in all_pairs:
            ra, rb = by_cell.get(a), by_cell.get(b)
            if not ra or not rb:
                continue
            va, vb = ra.get(f"mean_{f}", ""), rb.get(f"mean_{f}", "")
            if va == "" or vb == "":
                continue
            deltas.append(abs(float(va) - float(vb)))
        sd = metric_sd_across_cells.get(f)
        if deltas and sd:
            noise_ratio[f] = statistics.mean(deltas) / sd
        else:
            noise_ratio[f] = None

    # --- version-evolution signal (delta in SD units) ---
    version_deltas = {}  # label -> field -> delta_sd_units
    for label, a, b in VERSION_PAIRS:
        ra, rb = by_cell.get(a), by_cell.get(b)
        version_deltas[label] = {}
        if not ra or not rb:
            continue
        for f in SAMPLE_METRIC_FIELDS:
            va, vb = ra.get(f"mean_{f}", ""), rb.get(f"mean_{f}", "")
            sd = metric_sd_across_cells.get(f)
            if va == "" or vb == "" or not sd:
                continue
            version_deltas[label][f] = (float(vb) - float(va)) / sd

    mean_version_delta = {}
    for f in SAMPLE_METRIC_FIELDS:
        vals = [
            abs(version_deltas[label][f])
            for label in version_deltas
            if f in version_deltas[label]
        ]
        mean_version_delta[f] = statistics.mean(vals) if vals else None

    # --- redundancy (Spearman across cells) ---
    redundant_with = defaultdict(list)
    field_series = {}
    for f in SAMPLE_METRIC_FIELDS:
        field_series[f] = [
            (r["cell"], float(r[f"mean_{f}"]))
            for r in cell_rows
            if r.get(f"mean_{f}", "") != ""
        ]
    high_corr_pairs = []
    for i, f1 in enumerate(SAMPLE_METRIC_FIELDS):
        for f2 in SAMPLE_METRIC_FIELDS[i + 1 :]:
            d1 = dict(field_series[f1])
            d2 = dict(field_series[f2])
            common = sorted(set(d1) & set(d2))
            if len(common) < 10:
                continue
            xs = [d1[c] for c in common]
            ys = [d2[c] for c in common]
            rho = spearman(xs, ys)
            if rho is not None and abs(rho) > 0.8:
                high_corr_pairs.append((f1, f2, rho))
                redundant_with[f1].append(f2)
                redundant_with[f2].append(f1)

    # --- ranking ---
    def rank_key(f):
        e = eta2.get(f)
        n = noise_ratio.get(f)
        if e is None:
            return (-1, 999)
        return (e, -(n if n is not None else 999))

    ranked = sorted(
        [f for f in SAMPLE_METRIC_FIELDS if eta2.get(f) is not None],
        key=lambda f: (eta2[f], -(noise_ratio[f] if noise_ratio[f] is not None else 999)),
        reverse=True,
    )

    degenerate = []
    for f in SAMPLE_METRIC_FIELDS:
        vals = numeric_values(sample_rows, f)
        if not vals:
            degenerate.append((f, "no values computed"))
        elif all(v == vals[0] for v in vals):
            degenerate.append((f, f"constant at {vals[0]}"))

    lines = []
    lines.append("# Freeflow programmatic metrics — trial evaluation\n")
    lines.append(
        f"Corpus: `{CORPUS_ROOT}` — {len(sample_rows)} valid samples across "
        f"{len(cell_rows)} cells, {len(model_value)} cells mapped to a known model "
        f"({len(labs_by_model)} labs seen; {len(eligible_labs)} labs with ≥3 models used for ANOVA)."
    )
    lines.append("")
    lines.append(
        "Concrete-word lexicon (~120 words) used for `concrete_rate`: "
        + ", ".join(sorted(CONCRETE_LEXICON))
        + "."
    )
    lines.append("")

    lines.append("## Ranked metrics (top 20, by lab eta² then low replicate noise)\n")
    lines.append("| Rank | Metric | eta² | Kruskal p | Noise ratio | Mean \\|version-pair Δ\\| (SD units) | Redundant with |")
    lines.append("|---:|---|---:|---:|---:|---:|---|")
    for i, f in enumerate(ranked[:20], 1):
        e = eta2[f]
        p = kruskal_p.get(f)
        p_str = f"{p:.4f}" if p is not None else "—"
        nr = noise_ratio.get(f)
        nr_str = f"{nr:.3f}" if nr is not None else "—"
        vd = mean_version_delta.get(f)
        vd_str = f"{vd:.3f}" if vd is not None else "—"
        red = ", ".join(sorted(set(redundant_with.get(f, [])))) or "—"
        lines.append(f"| {i} | `{f}` | {e:.4f} | {p_str} | {nr_str} | {vd_str} | {red} |")

    lines.append("")
    lines.append("## Version-pair deltas on the top-8 metrics (SD units, signed)\n")
    top8 = ranked[:8]
    header = "| Version pair | " + " | ".join(f"`{f}`" for f in top8) + " |"
    sep = "|---|" + "---:|" * len(top8)
    lines.append(header)
    lines.append(sep)
    for label, a, b in VERSION_PAIRS:
        row = [label]
        for f in top8:
            v = version_deltas.get(label, {}).get(f)
            row.append(f"{v:+.3f}" if v is not None else "—")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Suggested 2-D grids where labs separate visibly\n")
    grids = [
        ("i_rate", "abstract_rate", "first-person density vs. abstraction — separates confessional/personal labs from essayistic/abstract ones"),
        ("sent_len_mean", "frag_rate", "sentence length vs. fragment rate — separates flowing-prose models from staccato/punchy ones"),
        ("bullet_rate", "heading_rate", "structural markdown use — separates models that default to prose from those that default to outline/listicle form even in free writing"),
    ]
    for x, y, note in grids:
        ex = eta2.get(x)
        ey = eta2.get(y)
        ex_str = f"{ex:.3f}" if ex is not None else "—"
        ey_str = f"{ey:.3f}" if ey is not None else "—"
        lines.append(
            f"- **x = `{x}`** (eta²={ex_str}), **y = `{y}`** (eta²={ey_str}): {note}"
        )

    lines.append("")
    lines.append("## Redundant pairs (|Spearman rho| > 0.8 across cells)\n")
    if high_corr_pairs:
        for f1, f2, rho in sorted(high_corr_pairs, key=lambda t: -abs(t[2])):
            lines.append(f"- `{f1}` <-> `{f2}`: rho = {rho:.3f}")
    else:
        lines.append("- none found above threshold")

    lines.append("")
    lines.append("## Degenerate / failed metrics\n")
    if degenerate:
        for f, reason in degenerate:
            lines.append(f"- `{f}`: {reason}")
    else:
        lines.append("- none — every metric showed variation")

    lines.append("")
    lines.append("## Surprises\n")
    lines.append(
        "- (fill in manually after reviewing the numbers above; the script does not editorialize)"
    )

    out = OUT_DIR / "freeflow_metrics_eval.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
