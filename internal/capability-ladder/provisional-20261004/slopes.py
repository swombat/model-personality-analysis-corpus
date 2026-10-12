import json,math
C=json.load(open('/home/agent/work/mpac/website/src/generated/capability-ladder.json'))
R={r['key']:r for r in C['rungs']}
b={k:r['difficulty'] for k,r in R.items()}
obs={}
for m,e in C['models'].items():
  if e.get('borrowed_from') or not e.get('rungs'): continue
  for r in e['rungs']:
    if r['how']=='fitted' and 0.3<r['points']<9.7:
      p=r['points']/10; obs.setdefault(m,{})[r['key']]=math.log(p/(1-p))
a={k:0.05 for k in b}; th={m:150.0 for m in obs}
for it in range(200):
  for m,d in obs.items():
    num=sum(a[j]*(y+a[j]*b[j]) for j,y in d.items()); den=sum(a[j]**2 for j in d)
    th[m]=num/den
  for j in b:
    xs=[(th[m]-b[j],d[j]) for m,d in obs.items() if j in d]
    if xs: a[j]=sum(x*y for x,y in xs)/sum(x*x for x,y in xs)
res=[ (y-a[j]*(th[m]-b[j])) for m,d in obs.items() for j,y in d.items()]
print('n',len(res),'rms',math.sqrt(sum(r*r for r in res)/len(res)))
for j in b: print(j,R[j]['chance'],b[j],round(a[j],4))
json.dump({'a':a,'b':b,'theta':th},open('items.json','w'))
