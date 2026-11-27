"""Freeze original/targeted attempts and every canonical receipt, offline only."""
import q2_import as m

v = m.load(m.P / "validation.json")
for name in (
    "continuation_batch_v13_qwen2-5-1-5b-instruct",
    "continuation_batch_v13_qwen2-5-1-5b-instruct_offline_short_20261127",
    "qwen25_eight_targeted_20261127",
):
    phase = m.R / name / "phase"
    if phase.exists():
        m.tree(phase, m.P / "history" / name / "phase")
for row in v["canonical_readings"]:
    for p, h in row["receipts"].items():
        assert m.sha(p) == h
        m.copy(m.Path(p), m.P / "history/frozen-source" / m.Path(p).relative_to("/"))
for name in ("qwen2_final_20261127.py", "qwen2_eight_targeted_20261127.py"):
    m.copy(m.R / name, m.P / "history/scripts-and-logs" / name)
# Seven result entries are targeted history, not seven short-rule adoptions.
v.pop("targeted_short_adoptions", None)
for row in v["canonical_readings"]:
    if "separate_short_rule" in row:
        row["separate_adoption"] = row.pop("separate_short_rule")
v["targeted_result_entries"] = 7
v["separately_adopted_readings"] = 30
v["copied_files"] = list({
    r["destination"]: r for r in v["copied_files"] + m.inventory
}.values())
m.put(m.P / "validation.json", v)
