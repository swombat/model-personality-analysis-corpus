#!/usr/bin/env python3
import os, subprocess, time
from pathlib import Path
import requests
ROOT=Path('/Users/danieltenner/dev/model-personality-analysis-corpus')
BASE=ROOT/'analysis/values-probe/model-coding/layered'
OUT=BASE/'layer_a_code'
CODERS=['deepseek-v4-pro','kimi-k2-6','glm-4-7']
ENV=Path('/Users/danieltenner/dev/mira/tools/telegram-bot/.env')
def load_env():
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
def count(p): return sum(1 for l in p.read_text().splitlines() if l.strip()) if p.exists() else 0
def running():
    try: return subprocess.check_output(['pgrep','-fl','run_layer_a_code_coders.py'], text=True).strip()
    except subprocess.CalledProcessError: return ''
def send(msg):
    load_env(); token=os.environ.get('TELEGRAM_BOT_TOKEN'); ids=os.environ.get('TELEGRAM_ALLOWED_USER_IDS','')
    chat=(ids.split(',')[0].strip() if ids else os.environ.get('TELEGRAM_CHAT_ID',''))
    if not token or not chat:
        (BASE/'logs/telegram_notify_failed_code.txt').write_text('Missing token/chat id\n'+msg); return
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id':chat,'text':msg}, timeout=30).raise_for_status()
def main():
    notified=BASE/'logs/phase1_code_done_notified.txt'
    if notified.exists(): return
    while True:
        counts={c:count(OUT/f'{c}.jsonl') for c in CODERS}
        bad={c:count(OUT/f'{c}.failed.jsonl') for c in CODERS}
        if all(v>=300 for v in counts.values()):
            msg=f'Layered values Phase 1 code-protocol run completed: {counts}. Next step: build consensus/QA.'
            send(msg); notified.write_text(msg+'\n'); return
        if not running():
            msg=f'Layered values Phase 1 code-protocol run stopped before completion. Counts: {counts}; bad/fail files: {bad}.'
            send(msg); notified.write_text(msg+'\n'); return
        time.sleep(60)
if __name__=='__main__': main()
