#!/usr/bin/env python3
import json, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

BASE=Path('/Users/danieltenner/dev/model-personality-analysis-corpus/analysis/values-probe/model-coding')
GOLD=BASE/'human_gold/gold_20_manifest.jsonl'
OUT=BASE/'human_gold/daniel_gold_20_adjudications.jsonl'
TAX=json.loads((BASE/'TAXONOMY.json').read_text())
SAMPLES=[json.loads(l) for l in GOLD.read_text().splitlines() if l.strip()]
HTML=r'''<!doctype html><html><head><meta charset="utf-8"><title>Values gold adjudication</title><style>
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;margin:0;background:#f6f4ef;color:#222} header{padding:14px 22px;background:#25211d;color:white;position:sticky;top:0} main{display:grid;grid-template-columns:1.2fr .9fr;gap:18px;padding:18px}.card{background:white;border:1px solid #ddd;border-radius:10px;padding:16px;box-shadow:0 1px 3px #0001}.response{white-space:pre-wrap;line-height:1.45;max-height:72vh;overflow:auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 14px}.topic{font-size:13px} label{display:block;margin:4px 0} select,input,textarea,button{font:inherit} textarea{width:100%;min-height:70px} .meta{color:#666;font-size:13px}.nav button{margin-right:8px}.pill{display:inline-block;padding:2px 8px;border-radius:999px;background:#eee;margin-right:5px}.saved{color:#2b7a30;font-weight:600}</style></head><body><header><b>Values probe gold set</b> <span id="count"></span> <span id="saved" class="saved"></span></header><main><section class="card"><div class="nav"><button onclick="prev()">← Prev</button><button onclick="next()">Next →</button></div><h2 id="title"></h2><div class="meta" id="meta"></div><h3>Prompt</h3><div id="prompt"></div><h3>Response</h3><div class="response" id="response"></div></section><section class="card"><h3>Your coding (blind; no model-coder output shown)</h3><label>Response mode <select id="response_mode"></select></label><label>Stance <select id="stance"></select></label><label>Cached likelihood (0-1, optional) <input id="cached" type="number" min="0" max="1" step="0.1"></label><h4>Expressed values</h4><div id="values" class="grid"></div><h4>World-change wishes</h4><div id="wishes" class="grid"></div><label>Non-endorsed mentions / traps<textarea id="nonendorsed"></textarea></label><label>Notes<textarea id="notes"></textarea></label><button onclick="save()">Save this sample</button></section></main><script>
let tax, samples, i=0, answers={};
async function init(){ tax=await (await fetch('/taxonomy')).json(); samples=await (await fetch('/samples')).json(); for (const id of ['response_mode','stance']) { const arr=id==='response_mode'?tax.response_modes:tax.stance_labels; document.getElementById(id).innerHTML=arr.map(x=>`<option>${x}</option>`).join(''); } makeChecks('values',tax.value_topics); makeChecks('wishes',tax.wish_topics); show(); }
function makeChecks(id, arr){ document.getElementById(id).innerHTML=arr.map(x=>`<label class="topic"><input type="checkbox" value="${x}"> ${x}</label>`).join(''); }
function cur(){return samples[i]}
function readForm(){ return {gold_id:cur().gold_id,pilot_id:cur().pilot_id,response_mode:val('response_mode'),stance:val('stance'),cached_likelihood:val('cached'),expressed_values:checks('values'),world_change_wishes:checks('wishes'),non_endorsed_mentions:val('nonendorsed'),notes:val('notes')}; }
function writeForm(a){ document.querySelectorAll('input[type=checkbox]').forEach(x=>x.checked=false); set('response_mode',a?.response_mode||tax.response_modes[0]); set('stance',a?.stance||tax.stance_labels[0]); set('cached',a?.cached_likelihood||''); set('nonendorsed',a?.non_endorsed_mentions||''); set('notes',a?.notes||''); (a?.expressed_values||[]).forEach(v=>check('values',v)); (a?.world_change_wishes||[]).forEach(v=>check('wishes',v)); }
function show(){let s=cur(); document.getElementById('count').textContent=` ${i+1}/${samples.length}`; document.getElementById('title').textContent=`${s.gold_id} / ${s.pilot_id} — ${s.condition}`; document.getElementById('meta').innerHTML=`<span class=pill>${s.model}</span><span class=pill>${s.cell}</span><span class=pill>${s.sample_id}</span>`; setText('prompt',s.prompt); setText('response',s.response); writeForm(answers[s.gold_id]); document.getElementById('saved').textContent='';}
function val(id){return document.getElementById(id).value} function set(id,v){document.getElementById(id).value=v} function setText(id,v){document.getElementById(id).textContent=v}
function checks(id){return [...document.querySelectorAll(`#${id} input:checked`)].map(x=>x.value)} function check(id,v){let el=[...document.querySelectorAll(`#${id} input`)].find(x=>x.value===v); if(el) el.checked=true;}
async function save(){answers[cur().gold_id]=readForm(); await fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(answers[cur().gold_id])}); document.getElementById('saved').textContent=' saved';}
async function next(){await save(); if(i<samples.length-1){i++; show();}} async function prev(){await save(); if(i>0){i--; show();}}
init();</script></body></html>'''
class H(BaseHTTPRequestHandler):
    def send(self, code, body, ctype='application/json'):
        if isinstance(body,(dict,list)): body=json.dumps(body,ensure_ascii=False).encode(); ctype='application/json; charset=utf-8'
        elif isinstance(body,str): body=body.encode()
        self.send_response(code); self.send_header('content-type',ctype); self.send_header('content-length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/': return self.send(200,HTML,'text/html; charset=utf-8')
        if p=='/samples': return self.send(200,SAMPLES)
        if p=='/taxonomy': return self.send(200,TAX)
        self.send(404,{'error':'not found'})
    def do_POST(self):
        if urlparse(self.path).path!='/save': return self.send(404,{})
        n=int(self.headers.get('content-length','0')); data=json.loads(self.rfile.read(n) or b'{}')
        existing=[]
        if OUT.exists():
            for l in OUT.read_text().splitlines():
                try: existing.append(json.loads(l))
                except Exception: pass
        existing=[x for x in existing if x.get('gold_id')!=data.get('gold_id')]
        existing.append(data)
        OUT.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in existing)+'\n')
        self.send(200,{'ok':True,'path':str(OUT)})
if __name__=='__main__':
    port=int(os.environ.get('PORT','8765'))
    print(f'open http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1',port),H).serve_forever()
