"""How far a fit on AutomationBench + Omniscience accuracy + GDP.pdf alone strays from the same model's fit on all its
measured rungs (same recovered 2026-10-04 method). Reads the published ladder; glm-5-3-flashx (a duplicate row of
glm-5-3-flash) is skipped. Writes three_rung_bias.json beside this file."""
import json, os, pathlib, subprocess, tempfile, statistics
ROOT = pathlib.Path('/home/agent/work/mpac'); P4 = ROOT/'internal/capability-ladder/provisional-20261004'
pre = subprocess.run(['git','-C',str(ROOT),'show','c85984e1^:website/src/generated/capability-ladder.json'],capture_output=True,text=True,check=True).stdout
tmp = tempfile.mkdtemp(); lad = os.path.join(tmp,'capability-ladder.json'); open(lad,'w').write(pre); cwd=os.getcwd(); os.chdir(tmp)
src = lambda f: (P4/f).read_text().replace('/home/agent/work/mpac/website/src/generated/capability-ladder.json', lad)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(src('slopes.py'), {}); g = {}; exec(src('score.py').split('# validate')[0], g)
os.chdir(cwd)
m = json.load(open(ROOT/'website/src/generated/capability-ladder.json'))['models']
K = ('automationbench','omniscience_accuracy','gdp_pdf'); out=[]
for k,v in m.items():
    if not v.get('ladder') or k in ('gemini-4-hydrogen','qwen4-max','glm-5-3-flashx'): continue
    d = {x['key']:x['points']/10 for x in v.get('rungs',[]) if x['how']=='measured'}
    if all(n in d for n in K) and v.get('measured_rungs',0) >= 6:
        full = g['score']({n:g['cc'](n,val) for n,val in d.items()})[1]
        three = g['score']({n:g['cc'](n,d[n]) for n in K})[1]
        out.append((three-full, k, v['ladder'], full, three, v['measured_rungs']))
out.sort()
for o in out: print('%+.1f %-22s pub %.1f refit-all %.1f three-only %.1f n=%d' % o)
ds=[o[0] for o in out]; print('n',len(ds),'mean %+.2f median %+.2f sd %.2f'%(statistics.mean(ds),statistics.median(ds),statistics.pstdev(ds)))

fr=[o[0] for o in out if o[2]>=150]
summary=dict(all=dict(n=len(ds),median=round(statistics.median(ds),2),mean=round(statistics.mean(ds),2)),
  published_150_plus=dict(n=len(fr),median=round(statistics.median(fr),2),mean=round(statistics.mean(fr),2),min=min(fr),max=max(fr)),
  rows=[dict(model=o[1],published=o[2],refit_all=o[3],three_only=o[4],delta=round(o[0],2),measured=o[5]) for o in out])
json.dump(summary,open(pathlib.Path(__file__).resolve().parent/'three_rung_bias.json','w'),indent=1); print('150+',summary['published_150_plus'])
