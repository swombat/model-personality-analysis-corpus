import json,math
I=json.load(open('items.json'));a,b=I['a'],I['b']
C=json.load(open('/home/agent/work/mpac/website/src/generated/capability-ladder.json'))
R=C['rungs']; ch={r['key']:r['chance'] for r in R}
sig=lambda x:1/(1+math.exp(-max(-40,min(40,x))))
def score(meas):  # meas: key -> chance-corrected score in [0,1]
  best=min((sum((sig(a[j]*(t-b[j]))-s)**2 for j,s in meas.items()),t) for t in [x/20 for x in range(1000,4001)])
  t=best[1]; rows=[]
  for r in R:
    k=r['key']; m=k in meas
    p=meas[k] if m else sig(a[k]*(t-b[k]))
    rows.append(dict(how='measured' if m else 'fitted',key=k,max=10,name=r['name'],points=round(10*p,2)))
  return t,round(sum(10*(meas[r['key']] if r['key'] in meas else sig(a[r['key']]*(t-b[r['key']]))) for r in R),1),rows
cc=lambda k,x:max(0,min(1,(x-ch[k])/(1-ch[k])))
# validate: GPT-6 Sol from its site measured points
g=C['models']['gpt-6-sol']; meas={r['key']:r['points']/10 for r in g['rungs'] if r['how']=='measured'}
t,L,_=score(meas); print('gpt-6-sol site-measured -> theta',t,'ladder',L,'site says',g['ladder'])
for name,raw in [('gpt-6-sol high TODAY',dict(aa_lcr=.837,scicode=.549,automationbench=.6012584,briefcase_rubric=.3787879,hle=.441,critpt=.254,gdp_pdf=.244,omniscience_accuracy=.537)),
                 ('gpt-6-1-sol high TODAY',dict(aa_lcr=.823,scicode=.558,automationbench=.6449524,briefcase_rubric=.4909091,hle=.514,critpt=.3,gdp_pdf=.32,omniscience_accuracy=.608))]:
  t,L,rows=score({k:cc(k,v) for k,v in raw.items()}); print(name,'theta',t,'ladder',L)
  t2,L2,_=score({k:cc(k,v) for k,v in raw.items() if k!='omniscience_accuracy'}); print('   without omniscience',t2,L2)
print('--- calibration over all directly-measured site models')
d=[]
for m,e in C['models'].items():
  if e.get('borrowed_from') or not e.get('rungs') or e.get('ladder') is None: continue
  meas={r['key']:r['points']/10 for r in e['rungs'] if r['how']=='measured'}
  t,L,_=score(meas); d.append((L-e['ladder'],m,e['ladder'],I['theta'].get(m),t))
d.sort(); import statistics
print('n',len(d),'median diff',statistics.median(x[0] for x in d),'mean abs',statistics.mean(abs(x[0]) for x in d))
for x in d[:4]+d[-4:]: print(x)
print([x for x in d if 'sol' in x[1] or 'opus' in x[1] or 'luna' in x[1]])
