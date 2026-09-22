# Release notes — v1.4.15

Prepared 2026-09-22. Six new freeflow models with straplines and banners; capability ladder refreshed; similarity map extended with layouts aligned to v1.4.14.

## Six new models (freeflow only)

Each has 125 freeflow samples, a BV1 evaluation, an aggregate packet, a personality card and profile, a strapline and a banner:

- **Xiaomi MiMo-V2.6-Flash, MiMo-V2.6-Pro, MiMo-V2.6-Pro-UltraSpeed** — released 2026-09-21, collected via OpenRouter's dated Xiaomi endpoints. Xiaomi is a new lab on the site (lab/family mapping added).
- **xAI Grok 4.7** — released 2026-09-21 (OpenRouter record; matches xAI's launch coverage).
- **Z.ai GLM-5.3-FlashX** — released 2026-09-18; Z.ai's faster (quantised) serving of GLM-5.3-Flash, not a new checkpoint.
- **Qwen2.5-7B-Instruct** — the official checkpoint (`Qwen/Qwen2.5-7B-Instruct`, revision a09a3545) run locally in BF16 via Transformers/MPS, after the 2026-09-18 fidelity repair recorded in the phase38 handoff. Its values analysis stays isolated in that phase's `release_candidate/` and is **not** merged.

**Values analyses for all six are not in this release.** Raw values traces exist; layered coding is in progress (`phase37_frontier_trio_20260921`, `phase38_qwen25_handoff_20260922`, `capture_20260922-*`) and is left uncommitted here. The six pages show freeflow results and no values panel.

## Capability ladder

- Artificial Analysis snapshot 2026-09-22 (656 records). Note for the runbook: AA's leaderboard and models pages no longer parse (0 and 28 records); the full table is still embedded in every per-model page, so the capture was taken from one of those.
- **Grok 4.7: 137.8 / 190** (5 measured rungs, Combined median effort = high; xhigh variant 137.5). **MiMo-V2.6-Pro: 143.2 / 190** (5 measured rungs).
- MiMo-V2.6-Flash, UltraSpeed, FlashX and Qwen2.5-7B have no AA or Epoch row yet. UltraSpeed and FlashX deliberately do **not** borrow their siblings' scores: the serving stacks differ (quantisation), and the number would be a guess wearing a measurement's clothes.
- The refit moved 130 existing scores: median |Δ| 0.5 points, max 2.6 (Gemma 4 26B A4B). 139 models scored, 20 not scored.

## Map

- 160 models. Layouts aligned to the v1.4.14 map (orthogonal Procrustes; UMAP seeded from the previous coordinates). For the 154 models common to both releases — median shift as % of map width / on-map 3-NN kept:
  PCA 2D 1.4 % / 93 %, PCA 3D 1.6 % / 92 %, MDS 2D 3.7 % / 78 %, MDS 3D 1.9 % / 81 %, UMAP 2D 6.6 % / 70 %, UMAP 3D 9.8 % / 73 %.
  Consistent with the leave-one-out figures in `website/scripts/MAP_TESTING.md`, now with six models added at once.
- Two MDS points flipped across the map (grok-4-1-fast-reasoning in 2D, Mistral Small 3.1 in 3D): MDS's known instability for poorly-fitted points, not a data change — their cosine neighbours are unchanged.
- Sibling checks read from the shipped similarities: GLM-5.3-FlashX ↔ GLM-5.3-Flash **0.958**, ↔ Ox Alpha 260825 / 260821 **0.963 / 0.962**; MiMo-V2.6-Pro ↔ UltraSpeed **0.980** (the same level as GPT-5.5 ↔ 5.5 Pro at 0.981), Flash ↔ Pro 0.955. Both same-weights claims land where the method says they should.
- **Grok 4.7 ↔ Grok 4.6 is only 0.854.** Its nearest neighbours are MiniMax M2 (0.929), Kimi K2.6 (0.908) and GPT-5 Codex (0.907) — the first Grok whose three nearest neighbours are all outside xAI. The card reads the same way: a contemplative humanist rather than the cosmic explainer of 4.1–4.6.
- Qwen2.5-7B's nearest neighbours are GPT-4 Turbo (0.919) and GPT-4o (0.899): the 2024 assistant register, which is what its strapline says.
- Numerical fidelity suite passes.

## Provenance notes

Added to the FlashX and UltraSpeed pages (same-weights relationship, measured similarity, why the ladder score is not borrowed).

## Not included

The in-flight repair of GLM-5.3's LONG_2 / LONG_5 traces and their BV1 re-evaluation; today's new values captures; BV1 outputs for MiMo-V2.5, Qwen3.8 27B and Ternary Bonsai (not on the site). The six cells' raw traces are still uncommitted in the sibling raw-corpus repository.

## Post-release fix, same day: the OpenRouter throughput feed had been dead since 31 May

Daniel read 133 tok/s off the MiMo-V2.6-Pro-UltraSpeed page on OpenRouter while the site said
"unknown". The cause was not the model's age: OpenRouter's frontend stats routes
(`/api/frontend/stats/endpoint`, `/stats/throughput-comparison`) have returned 404 since
2026-05-31, and `refresh_openrouter.py` preserved existing throughput whenever the fresh value was
None — so 61 models kept showing 31 May numbers labelled "OpenRouter median" for four months, and
every model added since June got a sample-median or nothing. A guard built on absence has no alarm
state; this one ran on every deploy and never said a word.

- Throughput is now read from the model page's embedded per-endpoint stats (`p50_throughput`,
  request count, 30-minute window) — median across endpoints with traffic as the speed, best endpoint
  as the max. **The window is 30 minutes, not the old 30 days**, so figures are noisier and are dated.
- Every speed label now carries its observation date (`OpenRouter p50, 3 endpoints, 30-min window
  (2026-09-22)`); anything still on the old feed reads `OpenRouter daily median (stale, last 2026-05-31)`.
- `refresh_openrouter.py` prints how many models returned fresh throughput and an ERROR when none do.
