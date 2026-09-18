#!/usr/bin/env python3
"""Refresh only the three repaired values views; leave other editorial data alone."""
import importlib.util
import json
import sys
from run import PHASE, ROOT, CELLS


def main():
    spec = importlib.util.spec_from_file_location(
        "historical_site_generator", ROOT / "website/scripts/generate_data.py"
    )
    generator = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = generator
    spec.loader.exec_module(generator)
    path = generator.GENERATED / "models.json"
    models = json.loads(path.read_text())
    targets = {model for model, _ in CELLS.values()}
    seen = set()
    for model in models:
        slug = model["model"]
        if slug not in targets:
            continue
        samples = generator.final_values_for_model(slug)[0]
        assert len(samples) == 120, slug
        model["analyzed_values_samples"] = len(samples)
        model["values_headline"] = generator.values_headline_data(slug)
        model["values_summary_markdown"] = generator.build_values_summary(slug, model["values_markdown"])
        model["values_details_markdown"] = generator.build_values_details(slug)
        assert model["values_headline"] is not None
        assert "No layered values-probe analysis" not in model["values_summary_markdown"]
        seen.add(slug)
    assert seen == targets
    path.write_text(json.dumps(models, ensure_ascii=False, indent=2))
    print("Updated three values views; no raw sample, profile, editorial, or map changes")


if __name__ == "__main__":
    main()
