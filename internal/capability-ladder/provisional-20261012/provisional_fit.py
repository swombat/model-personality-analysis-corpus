"""Provisional ladder shortcut, reused for Claude Haiku 5.5 (2026-10-12, souls.house container).
Same method as provisional-20261007/provisional_fit.py (Mistral Large 4); only the measured cells differ.
Variant: AA row claude-haiku-5-5-high, the median of AA's five effort rows (max/xhigh/high/medium/low),
matching Opus 5.5 and Sonnet 5.5 (Combined point = high). AA's default page row is Max and is NOT used.
Recovers per-rung slope/intercept from the published fitted cells of the 2026-09-29
ladder (website/src/generated/capability-ladder.json), validates by re-fitting every
directly scored model from its measured cells, then scores Mistral from the AA values
saved next to this file. Not the pipeline: the next refresh_capability_ladder.py run replaces it."""
import json, math, statistics as st
d=json.load(open(__import__('pathlib').Path(__file__).resolve().parents[3].as_posix()+'/website/src/generated/capability-ladder.json'))
RK=[r['key'] for r in d['rungs']]
def sig(x): return 1/(1+math.exp(-max(-40,min(40,x))))
def logit(p): return math.log(p/(1-p))
models={k:v for k,v in d['models'].items() if v.get('status')=='scored' and v.get('rungs') and not v.get('borrowed_from') and not v.get('provisional_note')}
cells=[(m,r['key'],r['points']/10) for m,v in models.items() for r in v['rungs'] if r['how']=='fitted' and 0.003<r['points']/10<0.997]
theta={m:v['ladder'] for m,v in models.items()}
P={k:(0.1,-13.0) for k in RK}
for it in range(200):
    for k in RK:
        xs=[(theta[m],logit(p)) for m,kk,p in cells if kk==k]
        if len(xs)<3: continue
        mx=st.mean(x for x,_ in xs); my=st.mean(y for _,y in xs)
        a=sum((x-mx)*(y-my) for x,y in xs)/sum((x-mx)**2 for x,_ in xs); P[k]=(a,my-a*mx)
    for m in models:
        xs=[(P[k][0],logit(p)-P[k][1]) for mm,k,p in cells if mm==m]
        if xs: theta[m]=sum(a*y for a,y in xs)/sum(a*a for a,y in xs)
    # renormalise theta scale to keep mean/sd of ladder
res=[logit(p)-(P[k][0]*theta[m]+P[k][1]) for m,k,p in cells]
print('cells',len(cells),'rms logit',(sum(r*r for r in res)/len(res))**.5, 'counts',{k:sum(1 for c in cells if c[1]==k) for k in RK})
def fit_theta(meas):
    lo,hi=min(theta.values())-80,max(theta.values())+80
    best=None; t=lo
    while t<hi:
        e=sum((sig(P[k][0]*t+P[k][1])-s)**2 for k,s in meas.items())
        if best is None or e<best[0]: best=(e,t)
        t+=0.05
    return best[1]
def ladder(meas):
    t=fit_theta(meas); rows=[]
    for k in RK:
        if k in meas: rows.append((k,'measured',round(10*meas[k],2)))
        else: rows.append((k,'fitted',round(10*sig(P[k][0]*t+P[k][1]),2)))
    return t,round(sum(r[2] for r in rows),1),rows
diffs=[]
for m,v in models.items():
    meas={r['key']:r['points']/10 for r in v['rungs'] if r['how']=='measured'}
    if len(meas)<3: continue
    t,tot,_=ladder(meas); diffs.append((tot-v['ladder'],m))
print('validation n',len(diffs),'mean abs',round(st.mean(abs(x) for x,_ in diffs),2),'mean',round(st.mean(x for x,_ in diffs),2),'worst',sorted(diffs,key=lambda x:-abs(x[0]))[:4])
for name in ['gpt-6-1-sol','mimo-v2-5-pro']:
    v=d['models'][name]; meas={r['key']:r['points']/10 for r in v['rungs'] if r['how']=='measured'}
    print(name,'published',v['ladder'],'mine',ladder(meas)[1])
import json as _j, pathlib as _p
H=_j.load(open(_p.Path(__file__).with_name('aa_claude-haiku-5-5-high_2026-10-12.json')))
assert H['slug']=='claude-haiku-5-5-high'
hle=(H['hle']-0.048)/(1-0.048)
M={'aa_lcr':H['lcr'],'scicode':H['scicode'],'automationbench':H['automationBenchPartialScore'],'briefcase_rubric':H['briefcaseBreakdown']['rubricPassRate'],'hle':hle,'omniscience_accuracy':H['omniscienceAccuracy'],'critpt':H['critpt'],'gdp_pdf':H['gdpPdfAllPass']}
t,tot,rows=ladder(M); print('HAIKU',tot); print(rows)
near=sorted(((abs(v['ladder']-tot),m,v['ladder']) for m,v in d['models'].items() if v.get('ladder')))[:6]; print(near)
json.dump({'ladder':tot,'rows':rows,'measured':M,'aa_variant':H['slug'],'intelligence_index':H['intelligenceIndex']},open(_p.Path(__file__).with_name('haiku-5-5_result_oct7_rebuild.json'),'w'),indent=1)
