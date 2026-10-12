import re,json
MAP={'omniscienceAccuracy':'omniscience_accuracy','gdpPdfAllPass':'gdp_pdf','tau2':'tau2_telecom','tauBanking':'tau3_banking','terminalbenchHard':'terminalbench_hard','terminalBench21':'terminalbench_v21','scicode':'scicode','lcr':'aa_lcr','ifbench':'ifbench','hle':'hle','gpqa':'gpqa_diamond','critpt':'critpt','livecodebench':'livecodebench','aime25':'aime25','mlcrOverall':'mlcr','automationBenchPartialScore':'automationbench','rubricPassRate':'briefcase_rubric'}
def raw(path,slug):
  h=open(path).read().replace('\\"','"')
  m=re.search(r'\{"id":"[0-9a-f-]{36}","slug":"'+slug+r'","name"',h)
  n=re.search(r'\{"id":"[0-9a-f-]{36}","slug":"',h[m.end():]); seg=h[m.start():m.end()+(n.start() if n else 30000)]
  out={}
  for f,k in MAP.items():
    mm=re.search(r'"'+f+r'":([-0-9.e]+)',seg)
    if mm: out[k]=float(mm.group(1))
  return out
