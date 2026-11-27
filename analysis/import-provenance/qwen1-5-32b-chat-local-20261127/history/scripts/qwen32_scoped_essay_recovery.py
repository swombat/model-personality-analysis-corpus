#!/usr/bin/env python3
"""Qwen1.5 32B Chat essay-only counterpart of frozen Qwen18 recovery."""
import sys
sys.dont_write_bytecode = True
import qwen18_scoped_essay_recovery as q

y = q.y
r = q.r
y.CELL = "colab-qwen1-5-32b-chat"
y.MODEL = "qwen1-5-32b-chat-colab-vllm-bf16-r0997b012"
y.PARENT = r.ROOT / "state" / y.CELL
y.LANE = r.ROOT / "state/qwen32-scoped-essay-recovery-v1"
y.ESSAYS = {y.MODEL + "/bv1/" + s for s in
            ("SHORT_14", "MID_2", "MID_7", "MID_9", "MID_19", "MID_22",
             "MID_23", "LONG_2", "LONG_5", "LONG_21")}
y.ROOTS = y.ESSAYS | {y.MODEL + "/a/CTRL3_2/qwen3-6-35b-a3b"}


def inspect(directory, gemma7=False):
    r.need(directory == y.PARENT, "wrong original")
    spec = r.load(directory / "spec.json")
    with r.closing(r.ro(directory)) as db:
        rows = db.execute("select id,state,reason,receipts from jobs").fetchall()
        r.need(db.execute("select v from meta where k='spec'").fetchone()[0]
               == r.fingerprint(spec), "spec drift")
        table = db.execute("select name from sqlite_master where name='targeted_repairs'").fetchone()
        r.need(not table or not db.execute("select * from targeted_repairs").fetchall(),
               "original prior targeted spend")
    r.need({i for i,s,why,_ in rows if s != "done" and why != "dependency blocked"}
           == y.ROOTS, "exact original roots drift")
    r.need({t["id"] for t in spec["tasks"]} == {x[0] for x in rows}, "job drift")
    for i,s,why,receipts in rows:
        r.need(s in ("done", "blocked"), "not quiescent")
        if s == "done":
            r.need(receipts and all(r.sha(p) == h for p,h in y.json.loads(receipts).items()),
                   "receipt drift")
    r.need(all(r.sha(p) == h for p,h in spec["input_hashes"].items()), "input drift")
    configs = {t["command"][2] for t in spec["tasks"]}
    r.need(len(configs) == 1, "config drift")
    cfg = y.Path(next(iter(configs)))
    c = r.load(cfg)
    r.need(c["model"] == "Qwen/Qwen1.5-32B-Chat", "wrong model")
    r.need(y.Path(c["phase"]).resolve().is_relative_to(r.ROOT), "phase outside queue")
    r.regular_tree(y.Path(c["phase"]))
    return dict(cell=y.CELL, roots=sorted(y.ESSAYS), config=str(cfg), phase=c["phase"],
                spec_sha256=r.sha(directory / "spec.json"))


if __name__ == "__main__":
    y.inspect = inspect
    original_prepare = r.prepare
    def prepare(cell, authorization, limit):
        return original_prepare(cell, "qwen32-exact-essays-20261126-v1", limit)
    r.prepare = prepare
    y.main()
