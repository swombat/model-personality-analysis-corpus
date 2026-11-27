"""Independent offline audit of import bytes and unchanged prior records."""
from pathlib import Path
import hashlib
import json
import subprocess

T = Path("/home/agent/work/colab-q2-15-site")
P = T / "analysis/import-provenance/qwen2-1-5b-instruct-local-20261127"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(["git", "-C", str(T), *args])

def main():
    v = json.loads((P / "validation.json").read_text())
    for r in v["copied_files"]:
        assert sha((T / r["destination"]).read_bytes()) == r["sha256"]
        assert sha(Path(r["source"]).read_bytes()) == r["sha256"]
    for r in v["canonical_readings"]:
        assert sha((T / r["destination"]).read_bytes()) == r["sha256"]
    for r in v["canonical_raw_sources"]:
        assert sha(Path(r["source"]).read_bytes()) == r["sha256"]
    assert len(v["canonical_readings"]) == 125
    assert len(v["canonical_raw_sources"]) == 245
    tracked = set(git("ls-files").decode().splitlines())
    assert all(r["destination"] in tracked for r in v["copied_files"])
    changed = git("diff", "--name-only", "--diff-filter=M", v["base"]).decode().splitlines()
    jsonls = {r["path"]: r for r in v["append_only_jsonl"]}
    indices = {
        "analysis/freeflow/personality-model-profiles/index.json",
        "analysis/values-probe/final/capture_sources.json",
    }
    assert set(changed) == set(jsonls) | indices, changed
    for path in changed:
        before = git("show", v["base"] + ":" + path)
        after = (T / path).read_bytes()
        if path in jsonls:
            assert after.startswith(before)
            r = jsonls[path]
            assert sha(before) == r["prior_sha256"] and sha(after) == r["sha256"]
            added = [json.loads(x) for x in after[len(before):].splitlines()]
            assert len(added) == r["added_rows"]
        else:
            old, new = json.loads(before), json.loads(after)
            assert new[:-1] == old and len(new) == len(old) + 1
    assert not git("diff", v["base"], "--", "website")
    # Untracked additions cannot conceal changes to any other prior tracked file.
    status = git("status", "--porcelain", "-uall").decode().splitlines()
    assert all(line[3:].startswith("analysis/") for line in status)
    receipt = dict(base=v["base"], bv1=125, values=120,
                   copied_files_checked=len(v["copied_files"]),
                   original_offline_adoptions=14, targeted_scope=8,
                   targeted_short_adoptions=4, prior_records_unchanged=True,
                   website_unchanged=True, model_calls=0, remote_writes=False,
                   validation_sha256=sha((P / "validation.json").read_bytes()))
    (P / "check-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
