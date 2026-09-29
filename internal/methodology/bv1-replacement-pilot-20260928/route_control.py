import concurrent.futures,json,os,time
from pathlib import Path
import requests
p=Path(__file__).resolve().parent
base=json.loads((p/'responses/deepseek_control/S55_LONG_24.json').read_text())['request']
def go(cap):
 out=p/f'digitalocean-long24-cap{cap}.json'
 if out.exists():return
 payload={**base,'max_tokens':cap,'provider':{'only':['DigitalOcean'],'allow_fallbacks':False}}
 started=time.monotonic();r=requests.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY']},json=payload,timeout=(20,180))
 d={'request':payload,'http_status':r.status_code,'response':r.json(),'seconds':time.monotonic()-started};out.write_text(json.dumps(d,indent=2)+'\n');print(cap,r.status_code,d['response'].get('provider'),[(x.get('finish_reason'),len(x.get('message',{}).get('content') or '')) for x in d['response'].get('choices',[])],d['seconds'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(go,[2200,8192]))
