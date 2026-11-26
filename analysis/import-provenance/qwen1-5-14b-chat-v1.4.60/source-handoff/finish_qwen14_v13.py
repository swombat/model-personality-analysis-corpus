"""Explicit isolated downstream adapter; never edits worker or original lanes."""
import os
import json
import shutil
import socket
from pathlib import Path
import qa_short_continuation as qa

b = qa.base
lane = b.ROOT / "continuation_qwen14_v13_20261127"
dest = b.ROOT / "finish_qwen14_v13_20261127c"
def put(p, obj):
    with p.open("x") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
def main():
    with b.lock():
        contract = b.load(b.ROOT / "contract.json")
        qa.preflight(contract, armed=True)
        assert not (b.ROOT.parent / "corpus-ops/STOP").exists()
        assert not dest.exists(), "no automatic re-entry"
        evidence = b.load(b.ROOT / "qwen14_downstream_review_20261127/validation.json")
        assert evidence["verified"] == 125 and evidence["model_calls"] == 0
        # Re-run full offline verification, not just trust its saved summary.
        sockets = (socket.socket.connect, socket.socket.connect_ex, socket.create_connection)
        import verify_qwen14_downstream_hold as verify
        verify.OUT = dest / "verification"
        dest.mkdir()
        # verifier requires a new destination and writes only evidence.
        verify.main()
        socket.socket.connect, socket.socket.connect_ex, socket.create_connection = sockets
        old = b.load(lane / "config.json")
        root = dest / "analysis"
        phase = dest / "phase"
        shutil.copytree(b.WORKTREE, root, ignore=shutil.ignore_patterns(".git"))
        shutil.copytree(Path(old["analysis_root"]), root, dirs_exist_ok=True)
        shutil.copytree(lane / "phase", phase)
        c = dict(old, analysis_root=str(root), phase=str(phase))
        put(dest / "config.json", c)
        w = b.verified_worker(contract)
        original_bv1 = w.bv1
        def bv1(config, ph, sid, validate=False, **kw):
            assert validate, "adapter never generates BV1"
            if sid != "LONG_12":
                return original_bv1(config, ph, sid, True, **kw)
            binding = b.load(lane / "offline_adoption/revalidation.json")
            src = w.trace_path(config, "freeflow", sid)
            d, source_hash = w.read_trace(config, "freeflow", sid)
            output = root / "offline_adoption/outputs/LONG_12.md"
            if not output.exists():
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(lane / "offline_adoption/outputs/LONG_12.md", output)
            assert source_hash == binding["source_sha256"] and b.sha(output.read_bytes()) == binding["output_sha256"]
            assert verify.module(lane / "offline_validator/luna_v1_3.py").valid_output(output.read_text(), d["result"]) == (True, "")
            # Original producing-arm binding remains original; separate validator
            # binding is consumed explicitly here, never presented as a new arm.
            target_binding = w.bv1_paths(config, ph, binding["evaluator_arm"])[2] / (sid + ".json")
            if not target_binding.exists():
                put(target_binding, {k:binding[k] for k in ("source_sha256","output_sha256","evaluator_arm")})
            return dict(pid=config["id_prefix"]+"_BV1_"+sid, model=config["model"],
                        cell=config["label"], condition=d["condition"],
                        provider=config["provider"], sample_id=config["label"]+"/"+sid+".json",
                        word_count=len(d["result"].split()), source=str(src),
                        outpath=str(output), text=d["result"], evaluator_arm=binding["evaluator_arm"])
        w.bv1 = bv1
        w.validate_source_config(c)
        for probe in ("freeflow", "values"):
            for sid in w.identities(probe):
                w.read_trace(c, probe, sid)
        assert w.bv1_ready_fields(c, phase)["bv1"] == 125
        for func in (w.assemble_values, w.adjudicate, w.values_report):
            func(c, phase, True)
        # Interpose only at the aggregate module loader boundary. The approved
        # route and transport remain unchanged; durable gate forbids a second call.
        original_module = w.module
        def module(name, path):
            m = original_module(name, path)
            if name == "capture_assembly":
                inner = m.module
                def load(name2, path2):
                    obj = inner(name2, path2)
                    if name2 == "phase35_aggregate":
                        call = obj.api_call
                        def once(*a, **k):
                            assert not (b.ROOT.parent / "corpus-ops/STOP").exists()
                            put(dest / "PRECALL.json", dict(route="openrouter-openai",
                                model="gpt-5.4", maximum_requests=1,
                                packet_sha256=b.sha(a[0].encode()), status="dispatch_may_have_occurred"))
                            return call(*a, **k)
                        obj.api_call = once
                    return obj
                m.module = load
            return m
        w.module = module
        os.environ.update(PERSONALITY_CELL_AGG_ROUTE="openrouter-openai",
                          PERSONALITY_CELL_AGG_MODEL="gpt-5.4",
                          COLAB_QUEUE_ARM=b.load(b.STATE/"active-arm.json")["nonce"])
        w.synthesis(c, phase, False)
        w.synthesis(c, phase, True)
        w.ready(c, phase, False)
        w.ready(c, phase, True)
        put(dest / "terminal.json", dict(status="queue-ready", model_requests=1,
            publication=False, bv1=125, expected=125,
            generation_and_revalidation_separate=True))
if __name__ == "__main__":
    main()
