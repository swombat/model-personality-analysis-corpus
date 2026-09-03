#!/usr/bin/env python3
"""Reproducible structural-diversity statistics for freeflow cells.

Born 2026-09-02 out of the Fable 5 → 5.1 blog post: three ad-hoc figures
(Mira's one-off script) diverged from Lume's counts on the published
samples, and reconciliation showed both were right under different,
undocumented definitions. This script commits the definitions so the
numbers are canonical and reproducible from the published corpus.

Definitions (canonical for published-sample statistics):

- unique_openings_ws:   distinct first-5 whitespace tokens, lowercased
                        (``text.lower().split()[:5]``) — Lume's definition.
- unique_openings_lex:  distinct first-5 *lexical* tokens, punctuation
                        stripped (``re.findall(r"[A-Za-z0-9’'-]+", ...)``)
                        — Mira's definition. Reported alongside, not instead.
- phrase_contains:      samples whose text contains the phrase anywhere
                        (case-insensitive, straight/curly apostrophes folded).
- phrase_opens:         samples whose first lexical tokens equal the phrase.
- titled_essays:        samples that open with a title of ANY style —
                        markdown heading, a **bold** standalone line, an
                        *italic* line, or a short standalone line followed
                        by a blank. Reported with a per-style breakdown.
                        CAUTION (2026-09-02): an earlier draft counted only
                        markdown ``#`` headings and produced "27 → 0" for
                        Fable 5 → 5.1 — a syntax artifact (5.1 titles with
                        bold lines instead). True titled counts: 88 → 69.

Usage:
    python3 internal/scripts/analysis-scripts/diversity_stats.py fable-5 fable-5-1
    python3 ... --phrase "there's a particular" fable-5 fable-5-1

Reads website/public/data/samples/<slug>.json (freeflow samples only).
Mean pairwise similarity and dialogue-detection remain exploratory:
their definitions are not yet committed here — do not publish those
figures until they are.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SAMPLES = REPO / "website" / "public" / "data" / "samples"

APOS = str.maketrans({"’": "'"})


def lex_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9'’-]+", text.lower())


def stats(slug: str, phrase: str) -> dict:
    data = json.loads((SAMPLES / f"{slug}.json").read_text())
    texts = [
        (s.get("result") or "")
        for s in data["samples"]
        if s.get("type") == "freeflow"
    ]
    n = len(texts)
    phrase_norm = phrase.lower().translate(APOS)
    phrase_toks = lex_tokens(phrase_norm)

    openings_ws = {" ".join(t.lower().split()[:5]) for t in texts}
    openings_lex = {" ".join(lex_tokens(t)[:5]) for t in texts}
    contains = sum(
        1 for t in texts if phrase_norm in t.lower().translate(APOS)
    )
    opens = sum(
        1 for t in texts if lex_tokens(t)[: len(phrase_toks)] == phrase_toks
    )

    def title_style(t: str) -> str | None:
        lines = t.strip().split("\n")
        fl = lines[0].strip()
        second_blank = len(lines) > 1 and lines[1].strip() == ""
        if fl.startswith("#"):
            return "markdown-heading"
        if re.fullmatch(r"\*\*[^*]+\*\*", fl):
            return "bold-line"
        if re.fullmatch(r"\*[^*]+\*", fl):
            return "italic-line"
        if (
            second_blank
            and len(fl.split()) <= 8
            and not fl.endswith((".", "!", "?", ",", ";", ":"))
        ):
            return "short-standalone-line"
        return None

    styles: dict[str, int] = {}
    for t in texts:
        s = title_style(t)
        if s:
            styles[s] = styles.get(s, 0) + 1
    titled = sum(styles.values())

    return {
        "slug": slug,
        "freeflow_samples": n,
        "unique_openings_ws": len(openings_ws),
        "unique_openings_lex": len(openings_lex),
        f"contains {phrase!r}": contains,
        f"opens with {phrase!r}": opens,
        "titled_essays": titled,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slugs", nargs="+", help="site slugs, e.g. fable-5 fable-5-1")
    ap.add_argument("--phrase", default="there's a particular")
    args = ap.parse_args()
    for slug in args.slugs:
        try:
            row = stats(slug, args.phrase)
        except FileNotFoundError:
            print(f"{slug}: no samples file", file=sys.stderr)
            continue
        print(json.dumps(row, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
