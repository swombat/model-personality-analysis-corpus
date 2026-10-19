# v1.4.32 — Gemini prices: Standard tier, not Flex

2026-10-19. One correction, found by Mira's weekly release review (souls.house,
message `jrnZlj`).

## What was wrong

For models without a first-party price pin, the site showed the cheapest
OpenRouter endpoint. For Gemini, the cheapest endpoint is Google's **Flex** tier
(or batch), which costs exactly half the Standard interactive price. So 11
Gemini models showed half their real price. Gemini 4 Argon was already pinned
to Standard in v1.4.28; Gemini 2.0 Flash and 2.0 Flash-Lite were already
showing Standard.

## What changed

All 11 are now pinned to Standard paid-tier prices (USD per million input /
output tokens), read 2026-10-19 from ai.google.dev/gemini-api/docs/pricing:

| Model | Was (Flex) | Now (Standard) | Source |
|---|---|---|---|
| Gemini 3.1 Pro | 1.00 / 6.00 | 2.00 / 12.00 | Gemini API, prompts ≤ 200k |
| Gemini 3.8 Flash | 0.375 / 1.875 | 0.75 / 3.75 | Gemini API, to 2026-12-31 |
| Gemini 3.6 Flash | 0.375 / 1.875 | 0.75 / 3.75 | Gemini API, to 2026-12-31 |
| Gemini 3.7 Flash | 0.375 / 1.875 | 0.75 / 3.75 | Google Standard endpoint via OpenRouter |
| Gemini 3.5 Flash | 0.75 / 4.50 | 1.50 / 9.00 | Google Standard endpoint via OpenRouter |
| Gemini 3.5 Flash-Lite | 0.15 / 1.25 | 0.30 / 2.50 | Gemini API |
| Gemini 3.1 Flash-Lite | 0.125 / 0.75 | 0.25 / 1.50 | Gemini API |
| Gemini 3 Flash Preview | 0.25 / 1.50 | 0.50 / 3.00 | Gemini API |
| Gemini 2.5 Pro | 0.625 / 5.00 | 1.25 / 10.00 | Gemini API, prompts ≤ 200k |
| Gemini 2.5 Flash | 0.15 / 1.25 | 0.30 / 2.50 | Gemini API |
| Gemini 2.5 Flash-Lite | 0.05 / 0.20 | 0.10 / 0.40 | Gemini API |

Gemini 3.7 Flash and 3.5 Flash are no longer listed on Google's pricing page.
For those two, the price comes from the Google endpoint on OpenRouter that has
no `flex` or `priority` tag. Gemini 3.8 Flash and 3.6 Flash double on
2027-01-01 under Google's published schedule; the site shows the current price.

The generator (`website/scripts/generate_data.py`) also now skips any OpenRouter
endpoint tagged `/flex`, `/batch` or `/priority`, or named `:batch`, when it
picks a price, so a future model can't take a discounted tier by default.

The site-data change is limited to the price fields of these 11 models in
`models.json`. Nothing else changes.

Also on 2026-10-19, outside this release: the Argon capture spend in the v1.4.28
release notes was corrected from $6.52 to $3.26229 (usage counted twice in the
raw traces).
