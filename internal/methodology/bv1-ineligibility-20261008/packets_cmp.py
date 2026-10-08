import importlib.util,sys,shutil,hashlib
from pathlib import Path
W=Path('/home/agent/work/mpac-linefix'); M=Path('/home/agent/work/mpac')
cell='haiku-5-5-or-pin-anthropic'; model='anthropic/claude-haiku-5.5'
phase=M/'analysis/values-probe/model-coding/layered/capture_20261007-haiku-5-5-house_haiku-5-5-or-pin-anthropic'
def run(path,tag):
    s=importlib.util.spec_from_file_location('p'+tag,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.PHASE=phase; m.MANIFEST=Path('/tmp/claude-1000/-home-agent-identity/9eea8a12-f01d-4e67-ac25-81c89bc64a61/scratchpad/haiku_manifest.tsv'); m.ROOT=W; m.CELLS={cell:model}
    if tag=='new': m.COVERAGE=None
    old=sys.argv; sys.argv=[old[0]]
    try: m.main()
    finally: sys.argv=old
    out=W/'analysis/freeflow/personality-aggregates'/cell
    return {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.glob('packet*'))}
a=run(sys.argv[1],'old'); b=run(W/'analysis/values-probe/model-coding/layered/phase35_union_alpha_20260917/build_aggregate_packets.py','new')
print('old',a); print('new',b); print('IDENTICAL' if a==b else 'DIFFERENT')
