import re,json,sys
def rec(f,slug):
  h=open(f).read().replace('\\"','"')
  out=[]
  for m in re.finditer(r'\{"id":"[0-9a-f-]{36}","slug":"'+slug+'","name"',h):
    n=re.search(r'\{"id":"[0-9a-f-]{36}","slug":"',h[m.end():])
    seg=h[m.start():m.end()+(n.start() if n else 30000)]
    ev=dict(re.findall(r'\{"slug":"([\w-]+)","score":([-0-9.e]+)',seg))
    rp=re.search(r'"rubricPassRate":([0-9.e-]+)',seg)
    out.append((len(seg),ev,rp and rp.group(1)))
  return out
for f,s in [(sys.argv[1],x) for x in sys.argv[2:]]:
  for L,ev,rp in rec(f,s): print(s,L,'rubric',rp, {k:round(float(v),3) for k,v in ev.items()})
