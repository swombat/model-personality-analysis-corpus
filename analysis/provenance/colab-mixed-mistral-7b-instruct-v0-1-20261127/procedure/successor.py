#!/usr/bin/env python3
"""Isolated Mistral adoption, two-call targeted lane, and reconciled synthesis.

No scheduler; no publication. Paid entrypoints require an explicit CLI arm.
"""
import sys
sys.dont_write_bytecode = True
import argparse, ast, contextlib, csv, fcntl, hashlib, importlib.util, inspect
import json, os, re, shutil, sqlite3, subprocess, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "runner"
CELL = SOURCE / "state/colab-mistral-7b-instruct-v0-1"
DEST = ROOT / "successor"
MODEL = "mistral-7b-instruct-v0-1-colab-vllm-bf16-rb1e7b9fc"
AUTH = "mixed-20261127-mistral-targeted-two-per-root"
ARM = "bv1-luna-v1-targeted-20261016"
STOP = ROOT.parents[2] / "corpus-ops/STOP"

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()

def durable(p, data, exclusive=False):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT |
                 (os.O_EXCL if exclusive else os.O_TRUNC), 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    fd = os.open(p.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def put(p, obj, exclusive=False):
    durable(p, canonical(obj) + b"\n", exclusive)

def load(p):
    return json.loads(Path(p).read_text())

def manifest(p):
    result = {}
    for q in sorted(Path(p).rglob("*")):
        need(not q.is_symlink(), "symlink in source")
        if q.is_file() and q.suffix != ".lock" and "__pycache__" not in q.parts:
            result[str(q.relative_to(p))] = sha(q)
    return result

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

def validators():
    code = ROOT / "validator"
    need(all(sha(code/n) == h for n,h in load(code/"hashes.json").items()), "validator drift")
    v = module("successor_v13", code/"luna_v1_3.py")
    bv = v.V1.BV
    src = inspect.getsource(bv.valid_output)
    need(src.count("len(txt.split()) < 120") == 1, "short rule source drift")
    scope = dict(vars(bv))
    exec(compile(ast.parse(src.replace("len(txt.split()) < 120",
                                      "len(txt.split()) < 30")), "<short-rule>", "exec"), scope)
    original = bv.valid_output
    def check(text, source):
        short = 0 < len(source.split()) < 50 and len(source) <= 300
        try:
            bv.valid_output = scope["valid_output"] if short else original
            ok, why = v.valid_output(text, source)
            if ok and short and not all(ch.strip() for ch in
                    re.split(r"^## .+\n", text, flags=re.M)[1:]):
                return False, "empty_section"
            return ok, why
        finally:
            bv.valid_output = original
    return v, check

@contextlib.contextmanager
def lane_lock():
    # Deliberately never touches the shared host lock (Qwen owns it).
    with (ROOT/"successor.lock").open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        need(not STOP.exists(), "STOP")
        yield

@contextlib.contextmanager
def db():
    c = sqlite3.connect(DEST/"state.sqlite")
    try:
        with c:
            yield c
    finally:
        c.close()

def config():
    return load(DEST/"config.json")

def original_snapshot():
    with contextlib.closing(sqlite3.connect(f"file:{CELL}/state.sqlite?mode=ro", uri=True)) as c:
        jobs = c.execute("select * from jobs order by id").fetchall()
        events = c.execute("select * from events order by rowid").fetchall()
        meta = c.execute("select * from meta order by k").fetchall()
        tables = {r[0] for r in c.execute("select name from sqlite_master where type='table'")}
        ledger = c.execute("select * from targeted_repairs").fetchall() if "targeted_repairs" in tables else []
    return json.loads(json.dumps(dict(jobs=jobs, events=events, meta=meta, ledger=ledger)))

def verify_frozen():
    ready = load(DEST/"ready.json")
    need(original_snapshot() == ready["source_database"], "original Mistral DB changed")
    need(all(sha(p) == h for p,h in ready["frozen_files"].items()), "original artifact drift")
    need(all(sha(DEST/p) == h for p,h in ready["code_hashes"].items()), "successor code drift")
    need(all(sha(DEST/p) == h for p,h in ready.get("input_hashes",{}).items()), "successor immutable input drift")
    need(all(sha(p) == h for p,h in ready["existing_receipts"].items()), "existing receipt drift")
    need(all(sha(ROOT/p)==h for p,h in ready.get("runner_hashes",{}).items()),"runner release drift")
    return ready

def prepare():
    need(not DEST.exists(), "successor exists: never reset/refill")
    # Only Mistral cell lock, opened read-only and never created.
    with (CELL/"supervisor.lock").open("r") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        before = original_snapshot()
        need(not any(r[1] in ("running", "pending") for r in before["jobs"]), "Mistral not quiescent")
        need(not before["ledger"], "prior targeted ledger requires explicit reconciliation")
        need(not any("targeted_repair_started" in r[2] for r in before["events"]), "historical targeted spend")
        c = load(next((CELL/"models").glob("*.json")))
        phase = Path(c["phase"])
        contract = load(SOURCE/"contract.json")
        need(all(sha(SOURCE/"analysis-worktree"/n) == h
                 for n,h in contract["analysis_inputs"].items()), "analysis drift")
        frozen = {}
        receipts = {}
        for row in before["jobs"]:
            if row[1] == "done":
                rec = json.loads(row[-1] or "{}")
                need(bool(rec), "done row lacks receipts")
                for p,h in rec.items():
                    need(sha(p) == h, "done receipt mismatch")
                    frozen[p] = h
                    receipts[p] = h
        # Copy only immutable analysis support and Mistral phase; never Qwen outputs.
        DEST.mkdir()
        tree = DEST/"analysis-worktree"
        for n,h in contract["analysis_inputs"].items():
            src = SOURCE/"analysis-worktree"/n
            dst = tree/n
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            frozen[str(src)] = h
        # Additional static supporting files (README, schemas, templates).
        for base in ("internal", "analysis/freeflow/personality-model-cards",
                     "analysis/freeflow/personality-model-profiles"):
            src = SOURCE/"analysis-worktree"/base
            if src.exists():
                shutil.copytree(src, tree/base, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("__pycache__"))
        relphase = phase.relative_to(SOURCE/"analysis-worktree")
        shutil.copytree(phase, tree/relphase, ignore=shutil.ignore_patterns("__pycache__"))
        for p in receipts:
            src = Path(p)
            if src.is_relative_to(SOURCE/"analysis-worktree"):
                dst = tree/src.relative_to(SOURCE/"analysis-worktree")
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(src,dst)
        for rel,h in manifest(phase).items():
            frozen[str(phase/rel)] = h
        raw = SOURCE/"raw/data"
        for probe, folder in (("freeflow","traces_freeflow"), ("values","traces_values")):
            src = raw/folder/(("freeflow_" if probe=="freeflow" else "")+MODEL)
            need(src.is_dir(), "missing raw tree")
            hashes = c["source_adoption"]["sha256"][probe]
            need(len(hashes)==(125 if probe=="freeflow" else 120),"raw inventory")
            need(all(sha(src/(sid+".json"))==h for sid,h in hashes.items()),"raw source adoption drift")
            shutil.copytree(src, DEST/"raw/data"/folder/src.name)
            for rel,h in manifest(src).items():
                frozen[str(src/rel)] = h
        newc = dict(c, analysis_root=str(tree), phase=str(tree/relphase))
        put(DEST/"config.json", newc)
        with contextlib.closing(sqlite3.connect(f"file:{CELL}/state.sqlite?mode=ro", uri=True)) as source, db() as target:
            source.backup(target)
            target.execute("create table if not exists targeted_repairs(authorization text,id text,used integer,allowance integer,primary key(authorization,id))")
            for job, rec in target.execute("select id,receipts from jobs where state='done'").fetchall():
                moved = {p.replace(str(SOURCE/"analysis-worktree"),str(tree)):h
                         for p,h in json.loads(rec).items()}
                need(all(sha(p)==h for p,h in moved.items()),"copied receipt mismatch")
                target.execute("update jobs set receipts=? where id=?",(json.dumps(moved),job))
        shutil.copyfile(CELL/"spec.json", DEST/"original-spec.json")
        put(DEST/"source-config.json", c)
        # Compile a dedicated reconciliation table; inherited jobs stay intact except adopted roots.
        with db() as target:
            target.execute("create table readings(id text primary key,path text,binding text,origin text)")
        ready = dict(source_database=json.loads(json.dumps(before)), frozen_files=frozen,
                     existing_receipts=receipts, authorization=AUTH, limit=2,
                     scheduler_enabled=False, code_hashes={str(p.relative_to(DEST)):sha(p)
                         for p in tree.rglob("*.py")})
        ready["input_hashes"] = {str(p.relative_to(DEST)):sha(p) for p in
            [DEST/"config.json", *list((DEST/"raw").rglob("*.json")),
             *list((tree/relphase).rglob("*.json"))] if p.is_file()}
        put(DEST/"ready.json", ready)
        need(json.loads(json.dumps(original_snapshot())) == ready["source_database"], "source changed")
        # Tuple/list normalization is intentional for persisted JSON.
        adopt()

def source_for(sid):
    return DEST/"raw/data/traces_freeflow"/("freeflow_"+MODEL)/(sid+".json")

def saved_attempts(sid):
    phase = Path(config()["phase"])
    return sorted(phase.glob("freeflow_bv1_luna_v1/attempt_responses/*_BV1_"+sid+"/*.json"))

def register(job, text, record, attempt, origin):
    sid = job.rsplit("/",1)[-1]
    source = source_for(sid)
    out = DEST/"analysis-worktree/analysis/freeflow/reconciled-readings"/sid
    out.mkdir(parents=True, exist_ok=True)
    output = out/"reading.md"
    if output.exists():
        need(output.read_bytes()==text.encode(),"unresolved differing reading; operator review")
    else:
        durable(output, text.encode())
    binding = dict(job=job, origin=origin, source_sha256=sha(source),
        output_sha256=sha(output), evaluator_arm=record["arm"],
        generation_attempt=str(attempt), generation_attempt_sha256=sha(attempt),
        original_qa_pass=record.get("qa_pass"), original_qa_reason=record.get("qa_reason"),
        validator="v1.3+bounded-short-source", validator_files_sha256=load(ROOT/"validator/hashes.json"))
    put(out/"binding.json", binding)
    receipts = {str(p):sha(p) for p in (output,out/"binding.json",attempt)}
    with db() as c:
        c.execute("insert into readings values(?,?,?,?)",(job,str(output),str(out/"binding.json"),origin))
        if origin != "original_validated":
            need(c.execute("update jobs set state='done',reason=?,receipts=?,pid=NULL where id=? and state='blocked'",
                ("isolated "+origin+"; generation arm preserved",json.dumps(receipts),job)).rowcount == 1,
                "root changed")
            c.execute("insert into events values(?,?,?,?)",(time.time(),job,origin,json.dumps(binding)))

def adopt():
    v, check = validators()
    c = config()
    phase = Path(c["phase"])
    with db() as state:
        rows = state.execute("select * from jobs where id like '%/bv1/%' order by id").fetchall()
        registered = {r[0] for r in state.execute("select id from readings")}
    need(len(rows)==125, "BV1 inventory")
    checks = []
    for row in rows:
        job, status = row[:2]
        if job in registered:
            continue
        sid = job.rsplit("/",1)[-1]
        source = source_for(sid)
        source_text = load(source)["result"]
        candidates = saved_attempts(sid)
        winner = None
        for p in candidates:
            r = load(p)
            need(r["source_sha256"]==sha(source), "attempt source mismatch")
            need(r["sample_id"]==MODEL+"/"+sid+".json", "attempt identity mismatch")
            need(r["arm"]=="bv1-luna-v1-20260929", "unexpected saved generation arm")
            response = r["response"]
            text = ((response.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
            valid, why = check(text, source_text)
            transport = v.transport_valid(r["http_status"], response)
            checks.append(dict(job=job,path=str(p),sha256=sha(p),valid=valid,transport=transport,reason=why))
            if valid and transport and winner is None:
                winner = p,r,text
        if status=="done":
            # Original validated reading is authoritative, never substitute a different saved answer.
            bindings = list(phase.glob("bv1_bindings_luna_v1/"+sid+".json"))
            need(len(bindings)==1, "missing original v1 binding")
            binding = load(bindings[0])
            output = DEST/"analysis-worktree/analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-20260929/outputs"/MODEL/(sid+".md")
            need(output.exists() and binding["source_sha256"]==sha(source) and
                 binding["output_sha256"]==sha(output), "original binding mismatch")
            need(check(output.read_text(),source_text)[0], "original output failed replay")
            need(winner is not None, "original lacks saved validated transport")
            # Original process strips trailing whitespace and adds a newline.
            matched = [a for a in checks if a["job"]==job and a["valid"] and a["transport"] and
                     (((load(a["path"])["response"]["choices"][0]["message"]["content"]).rstrip()+"\n")
                      == output.read_text())]
            need(bool(matched),"original reading not tied to saved response")
            attempt = Path(matched[0]["path"])
            register(job, output.read_text(),load(attempt),attempt,"original_validated")
        else:
            need(status=="blocked" and not (row[6] or "").startswith("dependency"), "not blocked root")
            if winner:
                register(job,winner[2],winner[1],winner[0],"offline_saved_revalidation")
    put(DEST/"saved-screen.json",checks)

def check_all():
    ready = verify_frozen()
    v, check = validators()
    with db() as c:
        readings = c.execute("select * from readings order by id").fetchall()
        failed = c.execute("select id from jobs where id like '%/bv1/%' and state!='done' order by id").fetchall()
    for job,p,b,origin in readings:
        r = load(b)
        need(sha(p)==r["output_sha256"], "reconciled output drift")
        need(sha(source_for(job.rsplit("/",1)[-1]))==r["source_sha256"], "source drift")
        need(sha(r["generation_attempt"])==r["generation_attempt_sha256"], "attempt drift")
        need(check(Path(p).read_text(),load(source_for(job.rsplit("/",1)[-1]))["result"])[0],
             "reading QA drift")
        with db() as c:
            row = c.execute("select state from jobs where id=?",(job,)).fetchone()
        need(row and row[0]=="done","reading not reconciled to done row")
    need(len(readings)+len(failed)==125,"reconciliation coverage")
    # Completed values report must remain done and receipt-valid, not regenerated.
    with db() as c:
        value = c.execute("select state,receipts from jobs where id=?",(MODEL+"/values-report",)).fetchone()
    need(value and value[0]=="done","values report incomplete")
    need(all(sha(p)==h for p,h in json.loads(value[1]).items()),"values report receipt drift")
    if (DEST/"terminal.json").exists():
        need(all(sha(p)==h for p,h in load(DEST/"terminal.json")["receipts"].items()),"terminal artifact drift")
    return dict(readings=len(readings), still_failed=[r[0] for r in failed], values_report_reconciled=True)

def exchange(request, directory, timeout):
    """One launch only. Permanent response bytes precede *any* JSON parsing."""
    directory = Path(directory)
    need(not directory.exists(), "durable call marker exists; never redispatch")
    need(not STOP.exists(),"STOP")
    key = os.environ.get("OPENROUTER_API_KEY")
    need(bool(key), "OPENROUTER_API_KEY required")
    directory.mkdir(parents=True)
    put(directory/"intent.json",dict(authorization=AUTH,request=request,at=time.time()),exclusive=True)
    # intent is the durable charge. A killed process never earns a replacement.
    with tempfile.TemporaryDirectory(prefix="mistral-transport-",dir=ROOT) as tmp:
        conf = Path(tmp)/"curl.conf"
        need("\n" not in key and "\r" not in key and '"' not in key, "invalid credential format")
        durable(conf, ('header = "Authorization: Bearer '+key+'"\n').encode())
        durable(directory/"request.json",canonical(request))
        result = subprocess.run(["curl","--disable","--config",str(conf),
            "--url","https://openrouter.ai/api/v1/chat/completions",
            "--request","POST","--header","Content-Type: application/json",
            "--data-binary","@"+str(directory/"request.json"),
            "--output",str(directory/"response.body"),"--write-out","%{http_code}",
            "--max-time",str(timeout),"--retry","0","--max-redirs","0","--proto","=https",
            "--silent","--show-error"],
            capture_output=True, timeout=timeout+10)
    if (directory/"response.body").exists():
        with (directory/"response.body").open("rb") as f:
            os.fsync(f.fileno())
    durable(directory/"curl.stderr", result.stderr)
    put(directory/"transport.json",dict(returncode=result.returncode,status=result.stdout.decode(errors="replace")))
    need(result.returncode==0,"transport failure; saved, stop lane")
    return decode_exchange(directory, request)

def decode_exchange(directory, request):
    """Also supports restart reconciliation without another call."""
    directory = Path(directory)
    need(load(directory/"request.json")==request,"saved request drift")
    need(load(directory/"intent.json")["request"]==request,"intent request drift")
    need((directory/"transport.json").exists(),"unresolved pre-call marker: operator reconciliation required")
    transport = load(directory/"transport.json")
    need(transport["returncode"]==0,"saved transport failure")
    response = load(directory/"response.body")  # body already durable, including malformed responses
    choice = (response.get("choices") or [{}])[0]
    need(transport["status"]=="200" and response.get("provider")=="OpenAI" and
         response.get("model")==request["model"] and choice.get("finish_reason")=="stop",
         "transport_finish_provider_or_model: stop lane")
    text = (choice.get("message") or {}).get("content")
    need(isinstance(text,str) and bool(text.strip()),"empty response: stop lane")
    return text,response

def targeted():
    check_all()
    v, check = validators()
    tree = DEST/"analysis-worktree"
    targeted_module = module("targeted_payload",tree/"analysis/freeflow/personality-eval-bv1/luna_v1_targeted.py")
    targeted_module.V1.BV.PROMPT_PATH = tree/"internal/methodology/freeflow-method-a-v2/balanced-prompt-calibration-cheap-models/prompts/BV1_signal_plus_felt.md"
    for job in check_all()["still_failed"]:
        sid = job.rsplit("/",1)[-1]
        source = source_for(sid)
        text = load(source)["result"]
        need(re.search(r"[.!?]",text),"unpunctuated root requires v1.1 review")
        phase = Path(config()["phase"])
        need(not list(phase.glob("bv1_bindings*/"+sid+".json")),"root already has a binding")
        need(not (phase/"bv1_ineligible"/(sid+".json")).exists(),"ineligible root")
        request = targeted_module.payload(dict(text=text,condition=load(source)["condition"]))
        for number in (1,2):
            directory = DEST/"calls"/sid/str(number)
            with db() as c:
                c.execute("insert or ignore into targeted_repairs values(?,?,0,2)",(AUTH,job))
                used,allowance = c.execute("select used,allowance from targeted_repairs where authorization=? and id=?",(AUTH,job)).fetchone()
                need(allowance==2,"allowance drift")
                if directory.exists():
                    answer,response = decode_exchange(directory,request)
                else:
                    need(used==number-1,"unresolved historical debit: stop")
                    # Commit debit BEFORE transport invocation, never refund it.
                    c.execute("update targeted_repairs set used=? where authorization=? and id=?",(number,AUTH,job))
                    c.execute("insert into events values(?,?,?,?)",(time.time(),job,"bv1_targeted_repair_started",json.dumps(dict(authorization=AUTH,attempt=number))))
                    c.commit()
                    answer,response = exchange(request,directory,180)
            ok,why = check(answer,text)
            record = dict(arm=ARM,source_sha256=sha(source),request=request,response=response,
                          qa_pass=ok,qa_reason=why)
            put(directory/"evaluation.json",record)
            if ok:
                register(job,answer,record,directory/"evaluation.json","targeted_v13_validated")
                break
    put(DEST/"targeted-terminal.json",check_all())

def targeted_check():
    status = check_all()
    phase = Path(config()["phase"])
    plan = []
    with db() as c:
        for job in status["still_failed"]:
            sid = job.rsplit("/",1)[-1]
            text = load(source_for(sid))["result"]
            need(re.search(r"[.!?]",text),"unpunctuated root: "+sid)
            need(not list(phase.glob("bv1_bindings*/"+sid+".json")),"existing binding: "+sid)
            need(not (phase/"bv1_ineligible"/(sid+".json")).exists(),"ineligible root: "+sid)
            spend = c.execute("select authorization,used,allowance from targeted_repairs where id=?",(job,)).fetchall()
            need(all(auth==AUTH and allowance==2 for auth,used,allowance in spend),"prior unrelated spend")
            used = spend[0][1] if spend else 0
            need(0<=used<=2,"invalid spend")
            plan.append(dict(id=job,used=used,allowance=2,remaining=2-used))
    result = dict(status,authorization=AUTH,roots=plan,
                  maximum_additional_launches=sum(r["remaining"] for r in plan))
    return result

def seal():
    """One-time offline pin for this prepared lane; no allowance or call changes."""
    ready = load(DEST/"ready.json")
    need("runner_hashes" not in ready,"already sealed; never rebaseline")
    verify_frozen()
    phase = Path(config()["phase"])
    ready["input_hashes"] = {str(p.relative_to(DEST)):sha(p) for p in
        [DEST/"config.json", *list((DEST/"raw").rglob("*.json")),
         *list(phase.rglob("*.json"))] if p.is_file()}
    ready["runner_hashes"] = {n:sha(ROOT/n) for n in
        ("successor.py","validator/luna_v1_3.py","validator/luna_v1.py","validator/run_full_bv1.py")}
    put(DEST/"ready.json",ready)

def synthesis(paid=False):
    status = check_all()
    need(status["readings"]==125 and not status["still_failed"],"all 125 readings required")
    c = config()
    tree = Path(c["analysis_root"])
    base = tree/"analysis/values-probe/model-coding/layered/phase35_union_alpha_20260917"
    fields = ["pid","model","cell","condition","provider","sample_id","word_count","source_json","output_file"]
    with db() as state:
        readings = state.execute("select id,path from readings order by id").fetchall()
        values_receipts = json.loads(state.execute("select receipts from jobs where id=?",
                                    (MODEL+"/values-report",)).fetchone()[0])
    path = DEST/"sample_manifest.tsv"
    with path.open("w") as f:
        writer = csv.DictWriter(f,fieldnames=fields,delimiter="\t")
        writer.writeheader()
        for job,p in readings:
            sid = job.rsplit("/",1)[-1]
            src = source_for(sid)
            raw = load(src)
            writer.writerow(dict(pid=c["id_prefix"]+"_BV1_"+sid,model=c["model"],cell=c["label"],
                condition=raw["condition"],provider=c["provider"],sample_id=c["label"]+"/"+sid+".json",
                word_count=len(raw["result"].split()),source_json=str(src),output_file=p))
    packet = module("reconciled_packets",base/"build_aggregate_packets.py")
    packet.PHASE,packet.ROOT,packet.MANIFEST = Path(c["phase"]),tree,path
    packet.CELLS = {c["label"]:c["model"]}
    old = sys.argv
    sys.argv = [old[0]]
    try:
        packet.main()
    finally:
        sys.argv = old
    put(DEST/"synthesis-inputs.json",dict(status,readings={p:sha(p) for _,p in readings},
        values_report_receipts=values_receipts,
        manifest_sha256=sha(path)))
    if not paid:
        return
    assembly = module("reconciled_assembly",base/"assemble_models.py")
    assembly.PHASE,assembly.ROOT,assembly.CELLS = Path(c["phase"]),tree,{c["label"]:c["slug"]}
    original_module = assembly.module
    def patched_module(name,path):
        m = original_module(name,path)
        if name=="phase35_aggregate":
            m.MODEL = "gpt-5.4"
            def payload(prompt,max_completion_tokens=4500):
                return dict(model="openai/gpt-5.4",provider=dict(only=["OpenAI"],allow_fallbacks=False),
                    messages=[dict(role="system",content=m.SYSTEM),dict(role="user",content=prompt)],
                    max_tokens=max_completion_tokens,temperature=0.2)
            def call(prompt,max_completion_tokens=4500,timeout=420):
                request = payload(prompt,max_completion_tokens)
                directory = DEST/"synthesis-call"
                if directory.exists():
                    need(load(directory/"request.json")==request,"synthesis request drift")
                    answer,response = decode_exchange(directory,request)
                else:
                    answer,response = exchange(request,directory,timeout)
                return answer,response.get("usage",{})
            m.api_call = call
            aggregate = m.AGG/c["label"]/"aggregate.md"
            if aggregate.exists():
                directory = DEST/"synthesis-call"
                need(directory.exists(),"unbound aggregate: never reuse or regenerate")
                prompt = m.build_prompt((aggregate.parent/"packet.md").read_text())
                answer,_ = decode_exchange(directory,payload(prompt))
                need(aggregate.read_text()==answer.rstrip()+"\n","aggregate saved-response mismatch")
        return m
    assembly.module = patched_module
    for folder,leaf in (("personality-model-cards","cards"),("personality-model-profiles","profiles")):
        (tree/"analysis/freeflow"/folder/leaf).mkdir(parents=True,exist_ok=True)
        readme = tree/"analysis/freeflow"/folder/"README.md"
        if not readme.exists():
            durable(readme,b"# Isolated Mistral analysis artifacts\n\n")
    assembly.main()
    # Reconcile completed values summary into an analysis-only combined deliverable.
    with db() as state:
        receipt = json.loads(state.execute("select receipts from jobs where id=?",(MODEL+"/values-report",)).fetchone()[0])
    report = next(Path(p) for p in receipt if p.endswith(".md"))
    profile = tree/"analysis/freeflow/personality-model-profiles/profiles"/(c["slug"]+".md")
    card = tree/"analysis/freeflow/personality-model-cards/cards"/(c["slug"]+".md")
    need(profile.exists() and card.exists(),"synthesis outputs missing")
    durable(DEST/"combined-analysis.md",profile.read_bytes()+b"\n\n# Completed values analysis\n\n"+report.read_bytes())
    receipts = {str(p):sha(p) for p in (profile,card,DEST/"combined-analysis.md",
        tree/"analysis/freeflow/personality-aggregates"/c["label"]/"aggregate.md")}
    with db() as state:
        state.execute("update jobs set state='done',reason=?,receipts=?,pid=NULL where id=?",
            ("isolated reconciled synthesis",json.dumps(receipts),MODEL+"/synthesis"))
        state.execute("insert into events values(?,?,?,?)",(time.time(),MODEL+"/synthesis",
            "isolated_reconciled_synthesis",json.dumps(receipts)))
    put(DEST/"terminal.json",dict(check_all(),analysis_only=True,published=False,receipts=receipts))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("action",choices=["prepare","seal","check","targeted-check","targeted","synthesis-check","synthesis"])
    p.add_argument("--arm-paid",action="store_true")
    args = p.parse_args()
    with lane_lock():
        if args.action=="prepare":
            prepare()
        elif args.action=="seal":
            seal()
        elif args.action=="check":
            print(json.dumps(check_all(),indent=2))
        elif args.action=="targeted-check":
            print(json.dumps(targeted_check(),indent=2))
        elif args.action=="targeted":
            need(args.arm_paid,"explicit --arm-paid required")
            need(bool(os.environ.get("OPENROUTER_API_KEY")),"OPENROUTER_API_KEY required")
            targeted_check()
            targeted()
        else:
            need(args.action!="synthesis" or args.arm_paid,"explicit --arm-paid required")
            synthesis(args.action=="synthesis")

if __name__=="__main__":
    main()
