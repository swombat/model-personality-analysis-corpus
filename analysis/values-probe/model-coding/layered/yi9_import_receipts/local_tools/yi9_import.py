#!/usr/bin/env python3
"""Offline Yi 1.5 9B evidence adapter; inherited mixed-arm verification."""
from pathlib import Path
import yi34_import as predecessor

source = Path(predecessor.__file__).read_text()
for old, new in (
    ("yi-34b-chat-colab-vllm-bf16-rcf02cb50", "yi-1-5-9b-chat-colab-vllm-bf16-r1a0fc698"),
    ("yi-34b-chat", "yi-1-5-9b-chat"),
    ("01-ai/Yi-34B-Chat", "01-ai/Yi-1.5-9B-Chat"),
    ("state/yi34-layer-a-v1", "state/yi9-scoped-recovery-v1/values-capture-before-parse-v3"),
    ('{"LONG_4", "MID_2", "MID_9", "MID_14", "OPEN_15"}', '{"LONG_9", "LONG_25", "OPEN_18"}'),
    ("52557b93f5e242f6542a751a49b5c62106cf98bdaf139eab667a3c60974dc0fe", "8caeb3e5ba3041da724312dd2deca89c5facd30b7b69c61e7a106b6e6663bbdf"),
    ("a033e33f8af247560c405cb38c7730106b7b00c39e0788c1f4d05799fe1ba12e", "ee318ff6dc9c8ebf6d08a01f9b2356fd1dd4ab2d50c58f52a5ace20c1a4779ca"),
    ('else 10)', 'else 6)'),
    ('"/a/G3_25/kimi-k2-6"', '"/p/G1_20/kimi-k2-6"'),
    ('verified["attempt"] == 1', 'verified["requests"] == 1 and verified["publication_authorized"] is False'),
    ('samples/G3_25/layer_a/kimi-k2-6.jsonl', 'samples/G1_20/posture/kimi-k2-6.jsonl'),
):
    assert old in source, old
    source = source.replace(old, new)
source = source.replace(
    '    need(load(RETRY / "dispatch.json") == dict(max_requests=1, task=verified["task"]), "retry dispatch")',
    '    need(load(RETRY / "authorization.json")["max_requests"] == 1, "retry dispatch")')
source = source.replace(
    '    ready = load(phase / "QUEUE_ANALYSIS_READY.json")',
    '''    auth = load(RETRY / "authorization.json")
    need(auth["task"] == verified["task"] and auth["publication_authorized"] is False
         and auth["parent_hold_sha256"] == verified["parent_hold_sha256"], "retry authorization")
    consumed = load(RETRY / "request-consumed.json")
    answer = load(RETRY / "returned-answer.json")
    need(consumed["task"] == answer["task"] == verified["task"]
         and consumed["max_requests"] == 1 and consumed["automatic_retries"] is False
         and consumed["publication_authorized"] is False
         and answer["status"] == 200 and answer["finish_reason"] == "stop", "request provenance")
    prior_receipt = str(RETRY.parent / "values-single-request-v2/request-consumed.json")
    need(answer["request_receipt_sha256"] == auth["old_lane_hashes"][prior_receipt]
         == digest(read(RETRY / "request-consumed.json")),
         "returned answer consumed-receipt lineage")
    for filename, sha in auth["old_lane_hashes"].items():
        add(filename, "evidence", sha)
    for src in sorted(RETRY.parent.rglob("*")):
        need(not src.is_symlink(), "retry evidence symlink")
        if src.is_file():
            add(src, "evidence")
    # Raw evidence supplies data only, never scripts, modules or configuration.
    manifest_rows = [json.loads(line) for line in read(phase / "manifest.jsonl").splitlines()]
    need(len(manifest_rows) == 120, "values manifest count")
    allowed = {e["destination"][4:]: e["sha256"] for e in entries.values()
               if e["destination"].startswith("raw/")}
    for row in manifest_rows:
        need(row["trace_path"] in allowed
             and allowed[row["trace_path"]] == row["source_sha256"], "untrusted raw path")
    ready = load(phase / "QUEUE_ANALYSIS_READY.json")''')
exec(compile(source, __file__, "exec"), globals())
