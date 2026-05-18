# Website values examples

This folder contains semantically curated example quotes for the website values sections.

- `curated_examples.json` is the committed artifact consumed by `website/scripts/generate_data.py`.
- `select_semantic_examples.py` selects short exact excerpts from coded candidate samples, returning `null` when no good concrete excerpt is found.
- `candidate_packets.json` is a large transient working file and is intentionally ignored; it can be rebuilt from the final values data.

A model is considered ready for Daniel review when all displayed rows in `curated_examples.json` for that model have non-null quotes, unless a null has been deliberately accepted as an intentional omission.
