#!/usr/bin/env python3
"""Scoped generation for named site slugs; every other model object is preserved.

Generalises generate_sonnet55.py (Mira, v1.4.18): a global regenerate reads
whatever canonical data the checkout happens to hold, so on a partial checkout
it silently thins older pages. This adds or refreshes only the slugs named on
the command line and asserts that all other model objects are byte-identical.

    python3 scripts/generate_scoped.py sonnet-5-5 qwen3-8-27b space-bunny-alpha

Run generate_map.py separately (it reads the public sample bundles).
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

import generate_data as g

# Raw values samples are browsable but their coding is not yet in the final
# dataset. Each entry needs a reason; remove it when the values are integrated.
VALUES_ANALYSIS_PENDING = {
    # 119 of 120 coded to consensus; one residual coder split (G2_22) awaits a
    # publication policy, so integrate_capture_values.py refuses the capture.
    "space-bunny-alpha",
}


def main(targets):
    assert targets, "name at least one site slug"
    original = json.loads((g.GENERATED / "models.json").read_text())
    index = json.loads(g.PROFILE_INDEX.read_text())
    rows = [r for r in index if g.site_slug_from_profile_model(r["model"]) in targets]
    found = {g.site_slug_from_profile_model(r["model"]) for r in rows}
    assert found == set(targets), ("not in profile index", set(targets) - found)
    destination, samples = g.GENERATED, g.PUBLIC_SAMPLES
    with tempfile.TemporaryDirectory(prefix="scoped-") as tmp:
        tmp = Path(tmp)
        shutil.copytree(destination, tmp / "generated")
        (tmp / "index.json").write_text(json.dumps(rows))
        g.PROFILE_INDEX = tmp / "index.json"
        g.GENERATED = tmp / "generated"
        g.PUBLIC_SAMPLES = tmp / "samples"
        g.main()
        generated = json.loads((g.GENERATED / "models.json").read_text())
        assert {m["model"] for m in generated} == set(targets), [m["model"] for m in generated]
        for m in generated:
            # Published samples must never exceed what was analysed.
            assert m["published_freeflow_samples"] <= m["analyzed_freeflow_samples"], m["model"]
            assert (
                m["published_values_samples"] <= m["analyzed_values_samples"]
                or m["model"] in VALUES_ANALYSIS_PENDING
            ), m["model"]
            print(
                m["model"], "|", m["display_name"], "|", m["lab"],
                "| freeflow", m["analyzed_freeflow_samples"], "/", m["published_freeflow_samples"],
                "| values", m["analyzed_values_samples"], "/", m["published_values_samples"],
                "| image", bool(m.get("image")),
            )
        keep = [r for r in original if r["model"] not in targets]
        combined = keep + generated
        combined.sort(key=lambda m: (m["lab"], m["model"]))
        assert {r["model"]: r for r in keep} == {
            r["model"]: r for r in combined if r["model"] not in targets
        }
        (destination / "models.json").write_text(
            json.dumps(combined, ensure_ascii=False, indent=2)
        )
        for t in targets:
            shutil.copy2(g.PUBLIC_SAMPLES / f"{t}.json", samples / f"{t}.json")
        print(f"{len(generated)} model(s) added/refreshed; {len(keep)} preserved exactly.")


if __name__ == "__main__":
    main(sys.argv[1:])
