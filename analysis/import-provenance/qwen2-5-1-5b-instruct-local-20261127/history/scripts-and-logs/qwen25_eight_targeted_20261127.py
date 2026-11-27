"""Qwen2.5 essay-only successor using the reviewed Qwen2 eight-item precedent."""
import sys
sys.dont_write_bytecode = True
import json
import sqlite3
import qwen2_eight_targeted_20261127 as lane

lane.SOURCE = lane.ROOT/"continuation_batch_v13_qwen2-5-1-5b-instruct_offline_short_20261127"
lane.ORIGINAL = lane.ROOT/"continuation_batch_v13_qwen2-5-1-5b-instruct"
lane.OLD = lane.ROOT/"remaining_recovery_colab-qwen2-5-1-5b-instruct"
lane.DEST = lane.ROOT/"qwen25_eight_targeted_20261127"
lane.MODEL = "qwen2-5-1-5b-instruct-colab-vllm-bf16-r989aa798"
lane.IDS = json.loads((lane.SOURCE/"terminal.json").read_text())["remaining_ids"]

if __name__ == "__main__":
    with sqlite3.connect(f"file:{lane.SOURCE}/state.sqlite?mode=ro", uri=True) as db:
        rows = db.execute("select id,state,receipts from jobs where id like '%/bv1/%'").fetchall()
        assert len(rows) == 125
        assert sum(r[1] == "done" for r in rows) == 117
        assert {r[0] for r in rows if r[1] != "done"} == set(lane.IDS)
        for _, state, receipts in rows:
            if state == "done":
                assert all(lane.sha(p) == h for p, h in json.loads(receipts).items())
    lane.main()
