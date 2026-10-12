import json,copy,sys
sys.argv=['x']
exec(open('score.py').read().split("# validate")[0])
from aa import raw
G='/home/agent/work/mpac/website/src/generated/'
CL=json.load(open(G+'capability-ladder.json'))
SRC_BASE="Artificial Analysis per-benchmark results (public model pages), fitted by the Model Capability Ladder pipeline; permission requested 2026-09-05"
def provisional(path,slug,matched,variant,note):
  r=raw(path,slug); meas={k:cc(k,v) for k,v in r.items()}
  t,L,rows=score(meas)
  for row in rows: row['source_date']='2026-10-04' if row['how']=='measured' else None
  return {"ladder":L,"ladder_max":220,"match_confidence":"exact","matched_model":matched,"measured_rungs":len(meas),"n_rungs":22,
          "point_variant":variant,"provisional_note":note,"rungs":rows,
          "source":SRC_BASE.replace("fitted by the Model Capability Ladder pipeline","provisionally fitted against the 2026-09-29 ladder's rung parameters (full refit pending)"),
          "status":"scored"}
NOTE=("Provisional. Measured from Artificial Analysis's public page on 2026-10-04 and fitted against the rung difficulties "
      "and slopes of the 2026-09-29 ladder, without the full refit. That shortcut reproduces the published ladder to within "
      "0.9 points on average across 148 scored models, and tends to read 0.6 points low. The next full pipeline run replaces it.")
CL['models']['gpt-6-1-sol']=provisional('gpt-6-1-sol.html','gpt-6-1-sol-high','GPT-6.1 Sol','high',NOTE)
CL['models']['mimo-v2-5-pro']=provisional('mimo-v2-5-pro.html','mimo-v2-5-pro','MiMo-V2.5-Pro (Reasoning)','default',NOTE)
q=copy.deepcopy(CL['models']['qwen3-8-27b']); CL['models']['qwen3-8-27b-medium']=q  # AA's Combined point for Qwen3.8 27B IS medium effort
CL['models']=dict(sorted(CL['models'].items()))
json.dump(CL,open(G+'capability-ladder.json','w'),indent=2,ensure_ascii=True,sort_keys=True); open(G+'capability-ladder.json','a').write('\n')
RD=json.load(open(G+'model-release-dates.json')); RS=json.load(open(G+'model-release-date-sources.json'))
RD.update({"mimo-v2-5-pro":"2026-04-22","qwen3-8-27b-medium":"2026-08-14","ternary-bonsai-2-27b-medium":"2026-09-18"})
RS.update({
 "mimo-v2-5-pro":"OpenRouter model record created 2026-04-22 (xiaomi/mimo-v2.5-pro, canonical xiaomi/mimo-v2.5-pro-20260422); matches Artificial Analysis's MiMo-V2.5-Pro release date. Recorded 2026-10-04.",
 "qwen3-8-27b-medium":"Same weights as qwen3-8-27b: OpenRouter model record created 2026-08-14 (qwen/qwen3.8-27b). The medium-reasoning capture is a separate condition, not a separate release. Recorded 2026-10-04.",
 "ternary-bonsai-2-27b-medium":"OpenRouter model record created 2026-09-18 (prism-ml/ternary-bonsai-2-27b, canonical prism-ml/ternary-bonsai-2-27b-20260918). This is the date the route appeared on OpenRouter; no lab announcement checked. Recorded 2026-10-04."})
for f,d in [('model-release-dates.json',RD),('model-release-date-sources.json',RS)]:
  json.dump(d,open(G+f,'w'),indent=2,ensure_ascii=False); open(G+f,'a').write('\n')
M=json.load(open(G+'models.json'))
for x in M:
  k=x['model']
  if k in RD and not x.get('release_date'): x['release_date']=RD[k]
  if k in ('gpt-6-1-sol','mimo-v2-5-pro','qwen3-8-27b-medium'): x['capability']=json.loads(json.dumps(CL['models'][k],sort_keys=True))
json.dump(M,open(G+'models.json','w'),indent=2,ensure_ascii=False)
for k in ('gpt-6-1-sol','mimo-v2-5-pro','qwen3-8-27b-medium'): print(k,CL['models'][k]['ladder'],CL['models'][k]['measured_rungs'])
