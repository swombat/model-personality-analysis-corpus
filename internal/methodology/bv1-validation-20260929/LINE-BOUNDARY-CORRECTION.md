# Whole-line boundary correction for unpunctuated line-structured sources — 2026-10-08

**Status: proposed. Mira approved the approach (BjZoXJ, 2026-10-08); the patch and
any recovery are not approved yet.** No recovery has been performed.

Capture `20261008-qwen3-8-omni-flash-house`, sample `MID_15`: all four allowed
BV1-Luna evaluations failed `quote_sentence_boundary`. I stopped there: no retry,
no budget change.

## The source

`qwen3-8-omni-flash-or-pin-alibaba/MID_15.json` (sha256 prefix 60c086e26360384e):
1,000 words in exactly 100 newline-separated lines, no blank lines, no CR. Every
line starts with a capital. The text contains none of `. ! ? … ; :`. It opens:

    I want to write about the quiet ordinary morning today
    The sky is pale blue and full of patient clouds
    A bird tests its voice against the window glass again

## The evaluator instruction (unchanged)

> Copy one whole sentence exactly as written, including capitalization,
> punctuation and inline Markdown. Do not wrap it in additional quotation marks,
> extract a clause, or normalize typography. Choose a straightforward sentence
> ending in a period, question mark or exclamation mark.

The last clause can't be satisfied on this source, because nothing in it ends in
`.`, `!` or `?`. All four evaluations quoted one complete source line exactly,
each a different line:

1. `I carry their examples when I do ordinary tasks today` (earliest, 1791440086157997708)
2. `Attention is a small lamp carried through crowded rooms daily`
3. `Small acts accumulate like light upon a windowsill each morning`
4. `Speed often steals the world before I can hold it`

Each is a full independent clause occupying a whole line. None is a fragment cut
from inside a line, none spans two lines, and none adds or drops a character.

## The rule

Added after the existing direct-speech path; every earlier gate and the exact
substring check run first and are unchanged. The fallback applies only when **all**
of these hold:

- the source contains no `.`, `!`, `?` or `…` anywhere (a newline alone is never
  treated as a boundary in punctuated prose);
- it has at least eight non-empty lines;
- every non-empty line starts with a capital (hard-wrapped prose has lowercase
  continuation lines, so it fails here);
- the quote starts with a capital, contains no CR, and **equals one entire line**
  of the source (LF or CRLF; start-of-text and EOF count as edges).

Partial lines, multi-line spans and lowercase quotes are never accepted through
this path. The eight-line floor and the capital-on-every-line test are
heuristics for "deliberately line-structured", not proofs of it.

## Evidence

- Regression suite: 34 tests (14 new). Positive: middle, first and last (EOF)
  line, LF and CRLF, CRLF with a trailing newline. Negative: partial line (head and
  capitalised tail), two lines, lowercase quote, source with one period, source
  with an ellipsis, fewer than eight lines, hard-wrapped lowercase continuation,
  hard-wrapped prose with periods. All 34 pass. Against the unpatched validator
  exactly the 5 new positive tests fail and every negative passes, so the
  negatives can tell the two validators apart.
- Before/after over existing Luna data (`line-boundary-20261008/`):
  - 558 final Luna outputs (Sonnet 5.5, GPT-6.1 Sol, Mistral Large 4, Haiku 5.5,
    125 each; 58 Qwen3.8 Omni Flash so far): 558 valid before, 558 after,
    **0 changed**.
  - 599 preserved attempt records across the same five runs: **4 changed**, all
    four `MID_15` attempts above (`quote_sentence_boundary` → valid). No other
    decision moved.
  - Not covered: the A/B arm responses in this directory's `responses/`, which
    are not Luna-arm outputs.

## Recovery, if the patch is approved

Bind the **earliest preserved response that passes all QA** (1791440086157997708:
HTTP 200, finish `stop`, provider OpenAI, model `openai/gpt-6-luna`, source hash
matches) through one separately recorded local revalidation, with provider
credentials removed and no API call. The four original failed attempt records
stay unchanged; the queue's 4/4 stays visible. Release notes disclose both this
correction and the recovery.
