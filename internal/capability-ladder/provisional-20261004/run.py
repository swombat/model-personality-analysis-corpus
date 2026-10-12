import sys; sys.argv=['x']
exec(open('score.py').read().split("# validate")[0])
from aa import raw
C2=C
for path,slug,site in [('mimo-v2-5-pro.html','mimo-v2-5-0424','mimo-v2-5'),('qwen3-8-27b.html','qwen3-8-27b-medium','qwen3-8-27b'),('mimo-v2-5-pro.html','mimo-v2-5-pro',None),('gpt-6-1-sol.html','gpt-6-1-sol-high',None),('gpt-6-sol.html','gpt-6-sol-high','gpt-6-sol')]:
  try: r=raw(path,slug)
  except Exception as e: print(slug,'missing',e); continue
  meas={k:cc(k,v) for k,v in r.items()}
  t,L,rows=score(meas)
  print(slug,'theta',t,'ladder',L,'measured',len(meas),'| site',site and C2['models'][site]['ladder'], site and C2['models'][site]['measured_rungs'])
