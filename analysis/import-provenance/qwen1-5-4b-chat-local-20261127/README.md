# Qwen1.5 4B Chat — local analysis import

Based on Gemma import `41207b3d3`, following `0d2a9fb54`.
The phase is taken from the finish lane's config.json, not phase_name.
Includes 125 essay readings and 120 values samples, cards, profile,
aggregate and existing synthesis/report; no analysis was regenerated.

`validation.json` inventories exact copied bytes and append-only shared JSONL.
Original short-source readings and generation attempts are retained in
`original-offline-adoption/`; producing-arm output paths contain those original
readings too. Separate capture revalidation bindings retain original failure,
generation attribution and validator hashes. `validator-sources/` contains the
exact hash-checked validator code, not a producing arm.

Inherited Markdown whitespace is intentionally preserved for byte fidelity;
plain git diff --check reports it. No website changes, calls, posts, remote
writes or delegation occurred.
