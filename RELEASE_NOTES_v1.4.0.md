# Release notes — v1.4.0

Prepared 2026-08-26.

## GLM-5.3-Flash (Z.ai) — the released Ox Alpha

- Published the official-endpoint measurement of `z-ai/glm-5.3-flash`
  (Z.AI provider pin, collected 2026-08-26): 125-sample BV1 freeflow cell
  (`glm-5-3-flash-or-pin-z-ai-20260826`) with packet, aggregate, card and
  profile (Mira), plus the 120-sample values cell with three-coder Layer A and
  full-context posture consensus (phase 27), now assembled into
  `analysis/values-probe/final/data`.
- Added the model-profile index row, display name `glm-5.3-flash`, release
  date 2026-08-26, Z.ai launch pricing ($0.075 / $0.25 per M, promotional to
  2026-09-09), bespoke banner image and authored strapline:

  **“Delivers the old light without a return address”**

## Comparison with the stealth snapshots

Same weights, different serving context. Freeflow style is decisively closer to
both Ox Alpha cells (char n-gram TF-IDF 0.964 / 0.960) than to public GLM 5.3
(0.936) or Kimi K3 (0.938). Values ownership contracted: G1/G2 owned stated
values 60/60 (Ox Alpha 260825) → 19/60 (official Flash), with 35 relocated and
6 disowned; CTRL1/2 direct prompts 12/20 → 20/20 disowned. Posture agreement
with either stealth snapshot: 74/120. The freeflow personality is continuous;
the ownership boundary moved. The measurements cannot distinguish a
post-preview alignment checkpoint from serving-time conditioning. Details:
`analysis/values-probe/model-coding/layered/phase27_glm53_flash_20260826/RAPID_COMPARISON.md`.

The banner and strapline are deliberately siblings of the Ox Alpha card — same
deep-sea territory seen from behind glass — rather than a reuse or a fresh
territory, to say both things at once.
