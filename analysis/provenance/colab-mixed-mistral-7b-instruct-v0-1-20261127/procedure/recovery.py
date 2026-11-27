"""Offline receipt proposals only. Never updates a queue database or dispatches."""
import sys
sys.dont_write_bytecode = True
import argparse, ast, hashlib, importlib.util, inspect, json, re, socket, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNNER = ROOT.parent / "runner"
CELL = RUNNER / "state/colab-mistral-7b-instruct-v0-1"
CODE = ROOT / "validator"
COMMIT = "0736983b404300033ce20858c64870b17f68d269"

def forbidden(*args, **kwargs):
    raise RuntimeError("offline: network/model calls forbidden")

socket.socket.connect = socket.socket.connect_ex = forbidden
socket.create_connection = forbidden

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p, obj):
    p.write_text(json.dumps(obj, indent=2) + "\n")

def rows():
    # mode=ro, not immutable: include committed WAL data without checkpointing.
    with sqlite3.connect(f"file:{CELL}/state.sqlite?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        return {r["id"]: dict(r) for r in db.execute(
            "select * from jobs where state='blocked' and id like '%/bv1/%'")}

def validator():
    pinned = json.loads((CODE / "hashes.json").read_text())
    assert all(sha(CODE / n) == h for n, h in pinned.items()), "validator drift"
    spec = importlib.util.spec_from_file_location("saved_v13", CODE / "luna_v1_3.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    v.BV.api_call = forbidden
    return v

def short_checker(v):
    # Exact historical audit_short_readings.py method: only the length floor.
    bv = v.V1.BV
    src = inspect.getsource(bv.valid_output)
    assert src.count("len(txt.split()) < 120") == 1
    scope = dict(vars(bv))
    exec(compile(ast.parse(src.replace("len(txt.split()) < 120",
                                      "len(txt.split()) < 30")), "<short-audit>", "exec"), scope)
    original = bv.valid_output
    def check(text, source):
        short = 0 < len(source.split()) < 50 and len(source) <= 300
        try:
            bv.valid_output = scope["valid_output"] if short else original
            ok, why = v.valid_output(text, source)
            if ok and short:
                chunks = re.split(r"^## .+\n", text, flags=re.M)[1:]
                if not all(ch.strip() for ch in chunks):
                    return False, "empty_section"
            return ok, why
        finally:
            bv.valid_output = original
    return check

def refresh(name, quiescent=False):
    dest = ROOT / name
    assert dest.parent == ROOT and not dest.exists(), "fresh direct-child output required"
    v = validator()
    short = short_checker(v)
    before = rows()
    if quiescent:
        # Fail closed if either mixed supervisor lock is held. No locks created.
        import fcntl
        locks = [(RUNNER / "state/host-supervisor.lock").open("r"),
                 (CELL / "supervisor.lock").open("r")]
        for lock in locks:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with sqlite3.connect(f"file:{CELL}/state.sqlite?mode=ro", uri=True) as db:
            assert not db.execute("select 1 from jobs where state='running'").fetchone()
    dest.mkdir()
    checks, proposals, remaining = [], [], []
    for job, row in sorted(before.items()):
        if (row["reason"] or "").startswith("dependency"):
            continue
        model, _, sid = job.split("/")
        source = RUNNER / "raw/data/traces_freeflow" / ("freeflow_" + model) / (sid + ".json")
        source_hash = sha(source)
        source_text = json.loads(source.read_text())["result"]
        attempts = sorted(p for p in RUNNER.glob(
            "analysis-worktree/**/attempt_responses/*_BV1_" + sid + "/*.json")
            if model in str(p))
        assert attempts, (job, "missing saved attempts")
        winner = None
        for p in attempts:
            record = json.loads(p.read_text())
            assert record["source_sha256"] == source_hash
            assert record["sample_id"] == model + "/" + sid + ".json"
            assert record["arm"] == "bv1-luna-v1-20260929"
            response = record["response"]
            transport = v.transport_valid(record["http_status"], response)
            text = response["choices"][0]["message"]["content"] or ""
            ok, reason = v.valid_output(text, source_text)
            method = v.VALIDATOR
            if not ok:
                ok, reason = short(text, source_text)
                method = "offline-short-source-30-word-rule"
            checks.append(dict(job=job, path=str(p), sha256=sha(p),
                               transport_valid=transport, valid=ok, reason=reason, method=method))
            if transport and ok and winner is None:
                winner = (p, record, text, method)
        assert sha(source) == source_hash
        if winner:
            p, record, text, method = winner
            out = dest / sid
            out.mkdir()
            (out / "reading.md").write_bytes(text.encode())
            (out / "original_attempt.json").write_bytes(p.read_bytes())
            binding = dict(job=job, source=str(source), source_sha256=source_hash,
                output_sha256=sha(out / "reading.md"), generation_attempt=str(p),
                generation_attempt_sha256=sha(p), evaluator_arm=record["arm"],
                original_qa_pass=record["qa_pass"], original_qa_reason=record["qa_reason"],
                validator=method, validator_commit=COMMIT,
                validator_files_sha256=json.loads((CODE / "hashes.json").read_text()),
                revalidation_pass=True, model_calls=0)
            write(out / "revalidation.json", binding)
            proposals.append(dict(job=job, original_row=row,
                receipts={str(q): sha(q) for q in out.iterdir()}))
        else:
            remaining.append(job)
    after = rows()
    assert all(after.get(k) == r for k, r in before.items()), "blocked rows changed; discard snapshot"
    assert all(sha(c["path"]) == c["sha256"] for c in checks), "attempt drift"
    result = dict(provisional=not quiescent, source_state_mutated=False,
        adoption_proposals=proposals, still_failed=remaining, checks=checks,
        model_calls=0, scheduler_enabled=False, published=False,
        targeted_policy=dict(authorization_required=True, limit_per_root_max=2,
            inherit_all_prior_ledgers_and_started_events=True, no_allowance_refill=True,
            infrastructure_error_stops_lane=True, downstream_run=False))
    write(dest / "screen.json", result)
    print(json.dumps(dict(path=str(dest), eligible=len(proposals), still_failed=len(remaining))))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("--require-quiescent", action="store_true")
    a = p.parse_args()
    refresh(a.name, a.require_quiescent)
