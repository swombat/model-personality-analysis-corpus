#!/usr/bin/env python3
"""Fixed analysis-only import; raw checkout is read-only untrusted evidence."""
from pathlib import Path
import gemma7_apply as lane
import yi9_import as evidence

TARGET = evidence.HOME.parent / "colab-yi9-site"
RAW = evidence.HOME.parent / "colab-yi9-raw"
HEAD = "0736983b404300033ce20858c64870b17f68d269"


def main():
    source = Path(lane.__file__).read_text()
    for old, new in (
        ("import gemma7_import as evidence", "import yi9_import as evidence"),
        ('evidence.HOME.parent / "colab-g7-site"', "TARGET"),
        ('evidence.HOME.parent / "colab-g7-raw"', "RAW"),
        ('"17d4b64f2d3c9985e64ae31f72a8ff3603057b70"', "HEAD"),
        ("gemma7", "yi9"),
    ):
        assert old in source
        source = source.replace(old, new)
    source = source.replace(
        '    module.integrate([phase])',
        '''    profiles = {p: p.read_bytes() for p in
        (TARGET / "analysis/freeflow/personality-model-profiles/profiles").glob("*.md")
        if p.stem != evidence.SLUG}
    module.integrate([phase])
    need(all(p.read_bytes() == data for p, data in profiles.items()), "prior profiles changed")''')
    source = source.replace(
        '    paths = sorted(set(imported + changed))',
        '''    report = final / "reports/yi-1-5-9b-chat.md"
    need(report.is_file(), "report absent")
    changed.append(str(report.relative_to(TARGET)))
    paths = sorted(set(imported + changed))''')
    namespace = dict(TARGET=TARGET, RAW=RAW, HEAD=HEAD, __name__="yi9_lane")
    exec(compile(source, lane.__file__, "exec"), namespace)
    namespace["main"]()


if __name__ == "__main__":
    main()
