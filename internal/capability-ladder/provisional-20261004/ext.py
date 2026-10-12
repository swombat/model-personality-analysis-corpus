import re,json,sys
F=['omniscienceAccuracy','gdpPdfAllPass','tau2','tauBanking','terminalbenchHard','terminalBench21','terminalBench40','scicode','lcr','ifbench','hle','gpqa','critpt','livecodebench','aime25','mmmuPro','mlcrOverall','intelligenceIndex']
def recs(path,base):
    h=open(path).read().replace('\\"','"')
    out={}
    for m in re.finditer(r'\{"id":"[0-9a-f-]{36}","slug":"('+base+r'(?:-[a-z]+)?)","name"',h):
        seg=h[m.start():m.start()+6000]
        d={}
        for f in F:
            mm=re.search(r'"'+f+r'":(null|[-0-9.e]+)',seg)
            d[f]=None if not mm or mm.group(1)=='null' else float(mm.group(1))
        out.setdefault(m.group(1),d)
    return out
for p,b in [('gpt-6-1-sol.html','gpt-6-1-sol'),('gpt-6-sol.html','gpt-6-sol')]:
    for k,v in recs(p,b).items(): print(k,{a:(round(x,3) if x is not None else None) for a,x in v.items() if x is not None})
