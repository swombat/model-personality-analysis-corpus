# Qwen2 0.5B Instruct — local analysis import

Second independent model import on the Gemma `41207b3d3` worktree.
The phase comes from finish-lane config.json. Includes 125 essay readings,
120 values samples, aggregate, card, profile and existing synthesis/report.
No analysis was regenerated.

`validation.json` inventories copied bytes and append-only shared JSONL.
`original-offline-adoption/` preserves original short-source readings,
generation attempts and selection receipts. Producing-arm output paths retain
the original readings; capture revalidation bindings remain separate from
original generation bindings. `validator-sources/` preserves exact,
hash-checked validator sources, not a producing evaluator arm.

Inherited Markdown whitespace is preserved for byte fidelity; plain
git diff --check reports it. No website changes, calls, posts, remote writes
or delegation occurred.
