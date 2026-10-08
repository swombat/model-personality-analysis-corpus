import importlib.util,sys,json
from pathlib import Path
W=Path('/home/agent/work/mpac-linefix'); cov=json.loads(sys.argv[1]) if len(sys.argv)>1 else None
p=W/'analysis/values-probe/model-coding/layered/phase35_union_alpha_20260917/assemble_models.py'
s=importlib.util.spec_from_file_location('am',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
real=m.module
def stub(name,path):
    mod=real(name,path)
    if name=='phase35_aggregate': mod.process=lambda meta,force: {'stubbed':True}
    return mod
m.module=stub; m.ROOT=W; m.CELLS={'haiku-5-5-or-pin-anthropic':'haiku-5-5'}; m.COVERAGE=cov
m.main()
