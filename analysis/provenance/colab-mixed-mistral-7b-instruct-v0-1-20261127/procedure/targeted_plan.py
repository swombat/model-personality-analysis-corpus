"""Build an exact bounded recovery request; deliberately no paid executor."""
import sys
sys.dont_write_bytecode = True
import argparse, json
from recovery import ROOT, rows, sha, write

def main():
    p = argparse.ArgumentParser()
    p.add_argument("screen")
    p.add_argument("output")
    a = p.parse_args()
    screen = ROOT / a.screen / "screen.json"
    out = ROOT / a.output
    assert out.parent == ROOT and not out.exists()
    data = json.loads(screen.read_text())
    assert not data["provisional"], "refresh under quiescent locks first"
    assert all(sha(c["path"]) == c["sha256"] for c in data["checks"])
    current = rows()
    ids = data["still_failed"]
    assert ids and all(k in current and not
        (current[k]["reason"] or "").startswith("dependency") for k in ids)
    assert all(not (c["valid"] and c["transport_valid"]) for c in data["checks"]
               if c["job"] in ids), "saved valid reading must be adopted"
    write(out, dict(ids=ids, source_screen=str(screen), source_screen_sha256=sha(screen),
        max_calls_per_root=2, maximum_generation_launches=2*len(ids),
        authorization=None, dispatch_enabled=False,
        required_before_dispatch=[
            "Explicit authorization; retain its identity and inherited spend, never refill.",
            "Copy only quiescent source into isolated successor; preserve source byte hashes.",
            "Rebase config/spec input paths and meta fingerprint only in successor; verify receipts.",
            "Audit historical targeted ledgers/events/intents across all ancestors; unresolved spend stops.",
            "Reject ineligibility receipt, v1 binding, unpunctuated source or dependency-blocked root.",
            "Pin harness/code; apply_bv1_targeted check_only on successor, never the live source.",
            "Separate targeted arm/output/provenance; durable debit before each launch.",
            "Stop lane on transport/provider/model/credential/STOP errors, not only after retries.",
            "No scheduler/downstream/publication. Keep failed attempts; no reset/reroll."
        ]))
    print(str(out))

if __name__ == "__main__":
    main()
