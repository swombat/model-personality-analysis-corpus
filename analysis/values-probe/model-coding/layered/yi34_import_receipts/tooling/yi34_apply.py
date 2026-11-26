#!/usr/bin/env python3
"""Adapt Gemma's fixed analysis-only lane, retaining its multiset/scope guards."""
from pathlib import Path
import gemma7_apply as lane
import yi34_import as evidence

TARGET = evidence.HOME.parent / "colab-yi34-site"
RAW = evidence.HOME.parent / "colab-yi34-raw"
HEAD = "4410d5e467b792ca0344b4b0d45fb1d8d3aa1fd2"


def main():
    # Execute the reviewed predecessor with only model-specific identifiers
    # replaced; the website-block removal and row-multiset checks remain intact.
    source = Path(lane.__file__).read_text()
    source = source.replace("import gemma7_import as evidence", "import yi34_import as evidence")
    source = source.replace('evidence.HOME.parent / "colab-g7-site"', "TARGET")
    source = source.replace('evidence.HOME.parent / "colab-g7-raw"', "RAW")
    source = source.replace('"17d4b64f2d3c9985e64ae31f72a8ff3603057b70"', "HEAD")
    source = source.replace("gemma7", "yi34")
    # git diff omits new untracked reports: explicitly inventory this model's
    # integrator output rather than scooping up the owner's concurrent work.
    anchor = '    paths = sorted(set(imported + changed))'
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        '    report_path = final / "reports/yi-34b-chat.md"\n'
        '    need(report_path.is_file(), "final report absent")\n'
        '    changed.append(str(report_path.relative_to(TARGET)))\n' + anchor)
    namespace = dict(TARGET=TARGET, RAW=RAW, HEAD=HEAD, __name__="yi34_analysis_lane")
    exec(compile(source, lane.__file__, "exec"), namespace)
    namespace["main"]()


if __name__ == "__main__":
    main()
