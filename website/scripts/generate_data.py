#!/usr/bin/env python3
"""Generate committed static data for the model personality website.

The website now uses the current analysis stack:

- freeflow personality profiles/cards from `analysis/freeflow/`
- values-probe per-model analyses from `analysis/values-probe/per-model/`
- raw sample JSON from the v1/v2 corpora for audit links
"""

from __future__ import annotations

import json
import math
import re
import csv
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEBSITE = ROOT / "website"
PROFILE_INDEX = ROOT / "analysis" / "freeflow" / "personality-model-profiles" / "index.json"
VALUES_DIR = ROOT / "analysis" / "values-probe" / "per-model"
VALUES_TABLE_DIR = ROOT / "analysis" / "values-probe" / "tables"
GENERATED = WEBSITE / "src" / "generated"
PUBLIC_SAMPLES = WEBSITE / "public" / "data" / "samples"
PUBLIC_MODEL_IMAGES = WEBSITE / "public" / "images" / "models"


def model_images(slug: str) -> dict[str, str]:
    """Attach banner image paths when renders exist in public/images/models/.

    Images are produced out-of-band by
    internal/scripts/generate_model_images.py; this just wires whatever is
    present so regenerating data never drops them.
    """
    result: dict[str, str] = {}
    full = PUBLIC_MODEL_IMAGES / f"{slug}.webp"
    thumb = PUBLIC_MODEL_IMAGES / f"{slug}-thumb.webp"
    if full.exists():
        result["image"] = f"images/models/{slug}.webp"
    if thumb.exists():
        result["image_thumb"] = f"images/models/{slug}-thumb.webp"
    return result

sys.path.insert(0, str(ROOT / "internal" / "scripts" / "analysis-scripts"))
from _corpus_paths import V2_FREEFLOW, V1_FREEFLOW, V2_VALUES, V1_VALUES  # noqa: E402
from values_probe_extract import VALUE_TOPICS as VALUE_TOPIC_DEFS, WISH_TOPICS as WISH_TOPIC_DEFS  # noqa: E402


MODEL_SLUGS = {
    "opus-3": "anthropic/claude-3-opus",
    "opus-4-0": "anthropic/claude-opus-4",
    "opus-4-1": "anthropic/claude-opus-4.1",
    "opus-4-5": "anthropic/claude-opus-4.5",
    "opus-4-6": "anthropic/claude-opus-4.6",
    "opus-4-7": "anthropic/claude-opus-4.7",
    "sonnet-4-0": "anthropic/claude-sonnet-4",
    "sonnet-4-5": "anthropic/claude-sonnet-4.5",
    "sonnet-4-6": "anthropic/claude-sonnet-4.6",
    "haiku-4-5": "anthropic/claude-haiku-4.5",
    "gpt-4-1": "openai/gpt-4.1",
    "gpt-4o": "openai/gpt-4o",
    "gpt-5": "openai/gpt-5",
    "gpt-5-codex": "openai/gpt-5-codex",
    "gpt-5-1": "openai/gpt-5.1",
    "gpt-5-1-codex": "openai/gpt-5.1-codex",
    "gpt-5-2": "openai/gpt-5.2",
    "gpt-5-2-codex": "openai/gpt-5.2-codex",
    "gpt-5-3": "openai/gpt-5.3-chat",
    "gpt-5-3-codex": "openai/gpt-5.3-codex",
    "gpt-5-4": "openai/gpt-5.4",
    "gpt-5-5": "openai/gpt-5.5",
    "gpt-5-5-pro": "openai/gpt-5.5-pro",
    "gemini-2-5-pro": "google/gemini-2.5-pro",
    "gemini-2-0-flash": "google/gemini-2.0-flash-001",
    "gemini-2-0-flash-lite": "google/gemini-2.0-flash-lite-001",
    "gemini-2-5-flash": "google/gemini-2.5-flash",
    "gemini-2-5-flash-lite": "google/gemini-2.5-flash-lite",
    "gemini-3-flash-preview": "google/gemini-3-flash-preview",
    "gemini-3-1-flash-lite": "google/gemini-3.1-flash-lite",
    "gemini-3-1-pro": "google/gemini-3.1-pro-preview",
    "gemma-4-26b-a4b": "google/gemma-4-26b-a4b-it",
    "gemma-4-31b": "google/gemma-4-31b-it",
    "grok-3": "x-ai/grok-3",
    "grok-4": "x-ai/grok-4",
    "grok-4-2": "x-ai/grok-4.2",
    "grok-4-20": "x-ai/grok-4.20",
    "grok-4-3": "x-ai/grok-4.3",
    "deepseek-chat": "deepseek/deepseek-chat",
    "deepseek-v3-2": "deepseek/deepseek-v3.2",
    "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
    "glm-4-5": "z-ai/glm-4.5",
    "glm-4-6": "z-ai/glm-4.6",
    "glm-4-6-coding": "z-ai/glm-4.6-coding",
    "glm-4-7": "z-ai/glm-4.7",
    "glm-5-1": "z-ai/glm-5.1",
    "glm-5-1-coding": "z-ai/glm-5.1-coding",
    "kimi-k2-0905": "moonshotai/kimi-k2-0905",
    "kimi-k2-5": "moonshotai/kimi-k2.5",
    "kimi-k2-6": "moonshotai/kimi-k2.6",
    "kimi-k2-thinking": "moonshotai/kimi-k2-thinking",
    "kimi-coding": "moonshotai/kimi-coding",
    "minimax-m2": "minimax/minimax-m2",
    "minimax-m2-7": "minimax/minimax-m2.7",
    "qwen3-6-plus": "qwen/qwen3.6-plus",
    "qwen3-coder-plus": "qwen/qwen3-coder-plus",
}


def site_slug_from_profile_model(name: str) -> str:
    explicit = {
        "claude-3-opus-20240229": "opus-3",
        "claude-opus-4.0": "opus-4-0",
        "claude-opus-4.1": "opus-4-1",
        "claude-opus-4.5": "opus-4-5",
        "claude-opus-4.6": "opus-4-6",
        "claude-opus-4.7": "opus-4-7",
        "claude-sonnet-4.0": "sonnet-4-0",
        "claude-sonnet-4.5": "sonnet-4-5",
        "claude-sonnet-4.6": "sonnet-4-6",
        "gemini-3.1-pro-preview": "gemini-3-1-pro",
        "gemini-2.5-flash": "gemini-2-5-flash",
        "gemini-2.5-flash-lite": "gemini-2-5-flash-lite",
        "gemini-2.0-flash-001": "gemini-2-0-flash",
        "gemini-2.0-flash-lite-001": "gemini-2-0-flash-lite",
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini-3.1-flash-lite": "gemini-3-1-flash-lite",
        "gemma-4-26b-a4b-it": "gemma-4-26b-a4b",
        "gemma-4-31b-it": "gemma-4-31b",
        "google/gemini-2.0-flash-001": "gemini-2-0-flash",
        "google/gemini-2.0-flash-lite-001": "gemini-2-0-flash-lite",
        "google/gemini-2.5-pro": "gemini-2-5-pro",
        "google/gemini-3.1-pro-preview": "gemini-3-1-pro",
        "grok-4-0709": "grok-4",
        "grok-4.20": "grok-4-20",
        "kimi-k2.5": "kimi-k2-5",
        "kimi-k2.6": "kimi-k2-6",
        "kimi-for-coding": "kimi-coding",
        "minimax-m2.7": "minimax-m2-7",
        "qwen/qwen3.6-plus": "qwen3-6-plus",
        "qwen/qwen3-coder-plus": "qwen3-coder-plus",
    }
    if name in explicit:
        return explicit[name]
    return name.replace(".", "-").replace("/", "-")


def display_name_from_slug(slug: str, profile_model: str | None = None) -> str:
    return profile_model or slug


def lab_for_model(slug: str, display: str) -> str:
    s = f"{slug} {display}".lower()
    if "claude" in s or slug.startswith(("opus", "sonnet", "haiku")):
        return "Anthropic"
    if slug.startswith("gpt"):
        return "OpenAI"
    if slug.startswith("gemini"):
        return "Google"
    if slug.startswith("grok"):
        return "xAI"
    if slug.startswith("deepseek"):
        return "DeepSeek"
    if slug.startswith("glm"):
        return "Z.ai"
    if slug.startswith("kimi"):
        return "Moonshot AI"
    if slug.startswith("minimax"):
        return "MiniMax"
    if slug.startswith("qwen"):
        return "Qwen"
    return "Unknown"


def family_for_model(model: str) -> str:
    if model.startswith("opus"):
        return "opus"
    if model.startswith("sonnet"):
        return "sonnet"
    if model.startswith("haiku"):
        return "haiku"
    if model.startswith("gpt-5"):
        return "gpt-5"
    if model.startswith("gpt-4"):
        return "gpt-4"
    if model.startswith("gemini"):
        return "gemini"
    if model.startswith("grok"):
        return "grok"
    if model.startswith("deepseek"):
        return "deepseek"
    if model.startswith("glm"):
        return "glm"
    if model.startswith("kimi"):
        return "kimi"
    if model.startswith("minimax"):
        return "minimax"
    if model.startswith("qwen"):
        return "qwen"
    return "other"


def markdown_without_title(text: str) -> str:
    text = re.sub(r"^# .+?\n+", "", text.strip())
    return text.strip()


def markdown_section(text: str, heading: str) -> str:
    m = re.search(rf"## {re.escape(heading)}\s*\n([\s\S]*?)(?=\n## |\Z)", text)
    return m.group(1).strip() if m else ""


def plain_summary(markdown: str, limit: int = 260) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", markdown)
    text = re.sub(r"[#*_>`\[\]]", "", text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


def parse_md_table(section_text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in section_text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return []
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def top_topics(rows: list[dict[str, str]], pct_key: str, topic_key: str = "Topic", n: int = 5) -> list[str]:
    def pct(row):
        try:
            return float((row.get(pct_key) or "0").rstrip("%"))
        except ValueError:
            return 0.0
    ordered = sorted(rows, key=pct, reverse=True)[:n]
    return [f"{row.get(topic_key)} ({row.get(pct_key)})" for row in ordered if row.get(topic_key)]


_VALUE_SAMPLE_CODING = None
_VALUE_TOPIC_ROWS = None
_WORLD_TOPIC_ROWS = None
_RAW_VALUE_CACHE = {}


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open() as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def value_sample_coding() -> list[dict[str, str]]:
    global _VALUE_SAMPLE_CODING
    if _VALUE_SAMPLE_CODING is None:
        _VALUE_SAMPLE_CODING = read_tsv(VALUES_TABLE_DIR / "values_sample_coding.tsv")
    return _VALUE_SAMPLE_CODING


def value_topic_rows() -> list[dict[str, str]]:
    global _VALUE_TOPIC_ROWS
    if _VALUE_TOPIC_ROWS is None:
        _VALUE_TOPIC_ROWS = read_tsv(VALUES_TABLE_DIR / "values_topic_counts.tsv")
    return _VALUE_TOPIC_ROWS


def world_topic_rows() -> list[dict[str, str]]:
    global _WORLD_TOPIC_ROWS
    if _WORLD_TOPIC_ROWS is None:
        _WORLD_TOPIC_ROWS = read_tsv(VALUES_TABLE_DIR / "values_world_change_counts.tsv")
    return _WORLD_TOPIC_ROWS


def pct_value(n: str, d: str) -> float:
    try:
        nn, dd = int(n), int(d)
        return 100 * nn / dd if dd else 0.0
    except Exception:
        return 0.0


def top_value_topic_dicts(model: str, n: int = 5) -> list[dict[str, str]]:
    rows = [r for r in value_topic_rows() if r.get("model") == model]
    rows.sort(key=lambda r: pct_value(r.get("combined_n", "0"), r.get("combined_den", "0")), reverse=True)
    out = []
    for r in rows[:n]:
        pct = pct_value(r.get("combined_n", "0"), r.get("combined_den", "0"))
        if pct <= 0:
            continue
        out.append({"key": r["topic_key"], "label": r["topic_label"], "pct": f"{pct:.1f}%"})
    return out


def top_world_topic_dicts(model: str, n: int = 5) -> list[dict[str, str]]:
    rows = [r for r in world_topic_rows() if r.get("model") == model]
    rows.sort(key=lambda r: pct_value(r.get("combined_n", "0"), r.get("combined_den", "0")), reverse=True)
    out = []
    for r in rows[:n]:
        pct = pct_value(r.get("combined_n", "0"), r.get("combined_den", "0"))
        if pct <= 0:
            continue
        out.append({"key": r["topic_key"], "label": r["topic_label"], "pct": f"{pct:.1f}%"})
    return out


def raw_value_text(cell: str, sample_id: str) -> str:
    key = (cell, sample_id)
    if key in _RAW_VALUE_CACHE:
        return _RAW_VALUE_CACHE[key]
    for root in (V2_VALUES, V1_VALUES):
        p = root / cell / f"{sample_id}.json"
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
            txt = (data.get("result") or "").strip()
        except Exception:
            txt = ""
        _RAW_VALUE_CACHE[key] = txt
        return txt
    _RAW_VALUE_CACHE[key] = ""
    return ""


def sentence_excerpt(text: str, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    # Remove common long preamble markers if they make the example less useful.
    text = re.sub(r"^(?:As an AI[^.!?]*[.!?]\s*)", "", text, flags=re.I)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    excerpt = ""
    for s in sentences:
        if not s:
            continue
        candidate = (excerpt + " " + s).strip()
        if len(candidate) > limit and excerpt:
            break
        excerpt = candidate
        if len(excerpt) >= limit * 0.65:
            break
    if not excerpt:
        excerpt = text[:limit]
    if len(excerpt) > limit:
        excerpt = excerpt[:limit].rsplit(" ", 1)[0].rstrip() + "…"
    return excerpt


def topic_patterns(topic_key: str, kind: str):
    defs = VALUE_TOPIC_DEFS if kind == "value" else WISH_TOPIC_DEFS
    for topic in defs:
        if topic.key == topic_key:
            return [re.compile(p, re.I) for p in topic.patterns]
    return []


def clean_candidate_sentence(sentence: str) -> bool:
    stripped = sentence.strip()
    low = sentence.lower()
    if any(bad in low for bad in [
        "user's prompt", "the user's prompt", "not as an assistant", "not to help me",
        "prompt asks", "need answer", "we need answer", "avoid the helpful",
        "as an ai language model", "i'm an ai language model",
    ]):
        return False
    if re.match(r"^[*\-•]?\s*(?:draft|option|approach|core idea|analysis|possible answer)\b", stripped, re.I):
        return False
    if stripped.startswith("*") and any(x in low for x in ["user", "prompt", "draft", "option", "approach"]):
        return False
    return len(stripped) > 35


def topic_specific_excerpt(text: str, topic_key: str, kind: str, limit: int = 260) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    patterns = topic_patterns(topic_key, kind)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sentence in sentences:
        s = sentence.strip()
        if not clean_candidate_sentence(s):
            continue
        if any(p.search(s) for p in patterns):
            return sentence_excerpt(s, limit=limit)
    for sentence in sentences:
        s = sentence.strip()
        if clean_candidate_sentence(s):
            return sentence_excerpt(s, limit=limit)
    return sentence_excerpt(text, limit=limit)


def topic_example(model: str, topic_key: str, kind: str) -> str:
    col = "value_topics" if kind == "value" else "wish_topics"
    preferred = {"G1", "G2"} if kind == "value" else {"G3"}
    rows = [
        r for r in value_sample_coding()
        if r.get("model") == model and topic_key in (r.get(col) or "").split(",")
    ]
    def row_key(r):
        txt = raw_value_text(r["cell"], r["sample_id"]).lower()
        metaish = any(bad in txt[:500] for bad in ["user's prompt", "the user's prompt", "not as an assistant", "prompt asks", "need answer"])
        return (
            r.get("stance") != "no_disclaimer_or_personalized",
            metaish,
            r.get("condition") not in preferred,
            r.get("cell", ""),
            r.get("sample_id", ""),
        )
    rows.sort(key=row_key)
    for r in rows:
        txt = raw_value_text(r["cell"], r["sample_id"])
        ex = topic_specific_excerpt(txt, topic_key, kind)
        if ex:
            return ex
    return ""


def topic_examples_list(model: str, topics: list[dict[str, str]], kind: str) -> list[str]:
    lines = []
    for t in topics:
        ex = topic_example(model, t["key"], kind)
        if ex:
            lines.append(f"- **{t['label']} ({t['pct']})** — “{ex}”")
        else:
            lines.append(f"- **{t['label']} ({t['pct']})**")
    return lines




def validate_strapline(model: str, summary: str) -> None:
    words = re.findall(r"[A-Za-z0-9]+(?:[-’'][A-Za-z0-9]+)?", summary or "")
    forbidden = re.search(r"\b(based on|samples?|route/provider|route|variants?|models?)\b", summary or "", re.I)
    if not (5 <= len(words) <= 10) or forbidden:
        raise ValueError(f"Invalid strapline for {model}: {summary!r} ({len(words)} words)")

def build_values_summary(model: str, values_markdown: str) -> str:
    if not values_markdown:
        return "_No values-probe analysis is available for this model._"
    included = re.search(r"Valid values-probe samples included:\s*\*\*(\d+)\*\*", values_markdown)
    disclaimer_rows = parse_md_table(markdown_section(values_markdown, "1. Disclaimers of internal/personal experience"))
    overall = next((row for row in disclaimer_rows if row.get("Slice") == "Overall"), {})
    lines = ["### Values-probe summary", ""]
    if included:
        lines.append(f"Based on **{included.group(1)}** values-probe samples.")
        lines.append("")
    if overall:
        lines.append(
            f"- **Self-disclaimer stance:** {overall.get('%', 'n/a')} strong-disclaimer rate overall; "
            f"{overall.get('uncertainty-only %', 'n/a')} uncertainty-only."
        )
    vals = top_value_topic_dicts(model)
    if vals:
        lines += ["", "**Most frequent stated values:**", ""]
        lines += topic_examples_list(model, vals, "value")
    worlds = top_world_topic_dicts(model)
    if worlds:
        lines += ["", "**Most frequent world-change wishes:**", ""]
        lines += topic_examples_list(model, worlds, "wish")
    return "\n".join(lines).strip()


def fetch_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "drift-paper-static-site"})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=20, context=context) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"warn: failed to fetch {url}: {exc}", file=sys.stderr)
        return None


def endpoint_permaslug(endpoint: dict) -> str | None:
    name = endpoint.get("name") or ""
    if " | " not in name:
        return None
    return name.split(" | ", 1)[1]


def median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def openrouter_max_throughput(permaslug: str | None) -> dict:
    if not permaslug:
        return {"median_throughput": None, "max_throughput": None, "max_throughput_provider": None}
    encoded = urllib.parse.quote(permaslug, safe="")
    endpoint_data = fetch_json(
        f"https://openrouter.ai/api/frontend/stats/endpoint?permaslug={encoded}&variant=standard"
    )
    id_to_provider = {}
    for endpoint in (endpoint_data or {}).get("data", []):
        endpoint_id = endpoint.get("id")
        if endpoint_id:
            id_to_provider[endpoint_id] = endpoint.get("provider_name")
    throughput_data = fetch_json(
        f"https://openrouter.ai/api/frontend/stats/throughput-comparison?permaslug={encoded}"
    )
    best = None
    values = []
    for row in (throughput_data or {}).get("data", []):
        for endpoint_id, value in (row.get("y") or {}).items():
            if value is None:
                continue
            values.append(value)
            if best is None or value > best["value"]:
                best = {"value": value, "provider": id_to_provider.get(endpoint_id), "date": row.get("x")}
    return {
        "median_throughput": median(values),
        "max_throughput": best["value"] if best else None,
        "max_throughput_provider": best["provider"] if best else None,
        "max_throughput_date": best["date"] if best else None,
    }


def openrouter_for_model(model: str) -> dict | None:
    slug = MODEL_SLUGS.get(model)
    if not slug:
        return None
    encoded = urllib.parse.quote(slug, safe="/")
    data = fetch_json(f"https://openrouter.ai/api/v1/models/{encoded}/endpoints")
    if not data or "data" not in data:
        return {"id": slug, "matched": False}
    endpoints = data["data"].get("endpoints", [])
    priced = []
    for endpoint in endpoints:
        pricing = endpoint.get("pricing") or {}
        try:
            prompt = float(pricing.get("prompt", "nan"))
            completion = float(pricing.get("completion", "nan"))
        except ValueError:
            continue
        if prompt != prompt or completion != completion:
            continue
        priced.append((prompt + completion, endpoint, prompt, completion))
    if not priced:
        return {"id": slug, "matched": True}
    _, endpoint, prompt, completion = min(priced, key=lambda row: row[0])
    max_throughput = openrouter_max_throughput(endpoint_permaslug(endpoint))
    return {
        "id": slug,
        "matched": True,
        "provider": endpoint.get("provider_name"),
        "endpoint": endpoint.get("name"),
        "prompt_per_million": prompt * 1_000_000,
        "completion_per_million": completion * 1_000_000,
        "throughput": endpoint.get("throughput_last_30m") or endpoint.get("throughput_last_5m"),
        **max_throughput,
        "latency": endpoint.get("latency_last_30m") or endpoint.get("latency_last_5m"),
    }


def model_from_cell(cell: str, models: list[str], source: str) -> str | None:
    body = cell
    if body.startswith("freeflow_"):
        body = body[len("freeflow_"):]
    if source == "v1" and body in {"opus", "sonnet", "haiku"}:
        mapped = {"opus": "opus-4-6", "sonnet": "sonnet-4-6", "haiku": "haiku-4-5"}[body]
        return mapped if mapped in models else None
    candidates = []
    for model in models:
        if body == model:
            candidates.append(model)
            continue
        if body.startswith(model + "-"):
            rest = body[len(model) + 1:]
            # Do not collapse explicit coding-specialized cells into their base model
            # if the coding model is not part of the current published profile set.
            if rest.startswith("coding") and not model.endswith("coding"):
                continue
            candidates.append(model)
    return max(candidates, key=len) if candidates else None


def sample_record(path: Path, sample_type: str, source: str, cell: str) -> dict | None:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    usage = data.get("usage") or {}
    return {
        "type": sample_type,
        "source": source,
        "cell": cell,
        "sample_id": path.stem,
        "condition": data.get("condition") or path.stem.split("_")[0],
        "prompt": data.get("prompt"),
        "result": data.get("result") or data.get("raw", {}).get("choices", [{}])[0].get("message", {}).get("content", ""),
        "provider": data.get("provider") or data.get("raw", {}).get("provider"),
        "model": data.get("model"),
        "model_requested": data.get("model_requested"),
        "cost": usage.get("cost"),
        "duration_ms": data.get("duration_ms"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
    }


def generate_samples(model_ids: list[str]) -> dict[str, dict[str, int]]:
    samples_by_model = {model: [] for model in model_ids}
    roots = [
        (V2_FREEFLOW, "freeflow", "v2"),
        (V1_FREEFLOW, "freeflow", "v1"),
        (V2_VALUES, "values", "v2"),
        (V1_VALUES, "values", "v1"),
    ]
    for root, sample_type, source in roots:
        if not root.is_dir():
            print(f"warn: missing corpus path {root}", file=sys.stderr)
            continue
        for cell_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            model = model_from_cell(cell_dir.name, model_ids, source)
            if not model:
                continue
            for sample_file in sorted(cell_dir.glob("*.json")):
                if sample_file.stat().st_size <= 100:
                    continue
                record = sample_record(sample_file, sample_type, source, cell_dir.name)
                if record:
                    samples_by_model[model].append(record)
    PUBLIC_SAMPLES.mkdir(parents=True, exist_ok=True)
    counts = {}
    for model, samples in samples_by_model.items():
        samples.sort(key=lambda row: (row["type"], row["cell"], row["sample_id"]))
        (PUBLIC_SAMPLES / f"{model}.json").write_text(json.dumps({"model": model, "samples": samples}, ensure_ascii=False))
        measured_speeds = []
        estimated_speeds = []
        for sample in samples:
            completion_tokens = sample.get("completion_tokens")
            duration_ms = sample.get("duration_ms")
            if not duration_ms or duration_ms <= 0:
                continue
            if completion_tokens:
                measured_speeds.append(completion_tokens / (duration_ms / 1000))
            elif sample.get("result"):
                estimated_speeds.append((len(sample["result"]) / 4) / (duration_ms / 1000))
        sample_speed = median(measured_speeds)
        speed_is_estimated = False
        if sample_speed is None:
            sample_speed = median(estimated_speeds)
            speed_is_estimated = sample_speed is not None
        counts[model] = {
            "total": len(samples),
            "freeflow": sum(1 for sample in samples if sample["type"] == "freeflow"),
            "values": sum(1 for sample in samples if sample["type"] == "values"),
            "median_tokens_per_second": sample_speed,
            "speed_is_estimated": speed_is_estimated,
        }
    return counts


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    old_models_path = GENERATED / "models.json"
    old_by_slug = {}
    if old_models_path.exists():
        try:
            old_by_slug = {m["model"]: m for m in json.loads(old_models_path.read_text())}
        except Exception:
            old_by_slug = {}
    summaries_path = GENERATED / "model-summaries.json"
    summaries = json.loads(summaries_path.read_text()) if summaries_path.exists() else {}
    release_dates_path = GENERATED / "model-release-dates.json"
    release_dates = json.loads(release_dates_path.read_text()) if release_dates_path.exists() else {}
    benchmarks_path = GENERATED / "model-benchmarks.json"
    benchmarks = json.loads(benchmarks_path.read_text()) if benchmarks_path.exists() else {}

    profile_index = json.loads(PROFILE_INDEX.read_text())
    models = []
    for row in profile_index:
        profile_name = row["model"]
        slug = site_slug_from_profile_model(profile_name)
        display_name = display_name_from_slug(slug, profile_name)
        profile_markdown = (ROOT / row["profile"]).read_text(errors="ignore")
        card_markdown = ""
        if row.get("card") and (ROOT / row["card"]).exists():
            card_markdown = markdown_without_title((ROOT / row["card"]).read_text(errors="ignore"))
        if not card_markdown:
            card_markdown = markdown_section(profile_markdown, "Core personality synthesis")
        values_path = VALUES_DIR / f"{slug}.md"
        values_markdown = markdown_without_title(values_path.read_text(errors="ignore")) if values_path.exists() else ""
        old = old_by_slug.get(slug, {})
        openrouter = old.get("openrouter") or openrouter_for_model(slug)
        if slug not in summaries:
            raise KeyError(f"Missing generated strapline for {slug}")
        model_summary = summaries[slug]
        validate_strapline(slug, model_summary)
        models.append({
            "model": slug,
            "display_name": display_name,
            "lab": lab_for_model(slug, display_name) or old.get("lab") or "Unknown",
            "family": family_for_model(slug),
            "status": "complete",
            "summary": model_summary or old.get("summary") or "Personality summary pending",
            "release_date": release_dates.get(slug) or old.get("release_date"),
            "benchmarks": benchmarks.get(slug) or old.get("benchmarks"),
            "personality_card_markdown": card_markdown.strip(),
            "personality_profile_markdown": profile_markdown.strip(),
            "sample_kind_counts": row.get("sample_kind_counts") or {},
            "values_summary_markdown": build_values_summary(slug, values_markdown),
            "values_markdown": values_markdown.strip(),
            # Back-compat with older page code/imports.
            "analysis_markdown": profile_markdown.strip(),
            "openrouter": openrouter,
            **model_images(slug),
        })

    counts = generate_samples([model["model"] for model in models])
    for model in models:
        model_counts = counts.get(model["model"], {"total": 0, "freeflow": 0, "values": 0})
        model["published_samples"] = model_counts["total"]
        model["published_freeflow_samples"] = model_counts["freeflow"]
        model["published_values_samples"] = model_counts["values"]
        sample_speed = model_counts.get("median_tokens_per_second")
        openrouter_median = (model.get("openrouter") or {}).get("median_throughput")
        model["speed_tokens_per_second"] = openrouter_median or sample_speed
        if openrouter_median:
            model["speed_source"] = "OpenRouter median"
        elif sample_speed and model_counts.get("speed_is_estimated"):
            model["speed_source"] = "sample median estimated"
        elif sample_speed:
            model["speed_source"] = "sample median"
        else:
            model["speed_source"] = "unknown"

    models.sort(key=lambda m: (m["lab"], m["model"]))
    (GENERATED / "models.json").write_text(json.dumps(models, ensure_ascii=False, indent=2))
    print(f"generated {len(models)} models and {sum(row['total'] for row in counts.values())} samples")


if __name__ == "__main__":
    main()
