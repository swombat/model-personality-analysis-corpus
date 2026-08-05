# Release notes — v1.3.4

Prepared 2026-08-05.

## Provenance correction

- Restored the earlier **DeepSeek V4 Flash** as a distinct freeflow model.
  The direct `deepseek-chat` alias moved during the May 2026 top-up: 100
  traces returned `deepseek-v4-flash`, while 25 returned `deepseek-chat`.
  Those 100 traces are now partitioned into their own card, profile, and
  browser sample bundle instead of being folded into DeepSeek Chat.
- The later **DeepSeek V4 Flash 0731** remains a separate model with its own
  125 freeflow and 120 values samples.

## Qwen metadata correction

- Removed the provisional 53.4 Intelligence Index entry for Qwen 3.8 Max.
  No authoritative Artificial Analysis Intelligence Index is currently
  published for the model, so the field is intentionally blank.
