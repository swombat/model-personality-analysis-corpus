#!/usr/bin/env python3
import json, os, subprocess, time
from pathlib import Path
import requests
ROOT=Path('/Users/danieltenner/dev/model-personality-analysis-corpus')
BASE=ROOT/'analysis/values-probe/model-coding/layered'
OUT=BASE/'layer_a'
CODERS=['deepseek-v4-pro','kimi-k2-6','glm-4-7']
MIRA=Path('/Users/danieltenner/dev/mira')
ENV=MIRA/'tools/telegram-bot/.env'
def load_env():
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
def count(path):
    return sum(1 for l in path.read_text().splitlines() if l.strip()) if path.exists() else 0
def running():
    try:
        out=subprocess.check_output(['pgrep','-fl','run_layer_a_coders.py'], text=True)
        return out.strip()
    except subprocess.CalledProcessError:
        return ''
def send(msg):
    load_env(); token=os.environ.get('TELEGRAM_BOT_TOKEN'); ids=os.environ.get('TELEGRAM_ALLOWED_USER_IDS','')
    chat=(ids.split(',')[0].strip() if ids else os.environ.get('TELEGRAM_CHAT_ID',''))
    if not token or not chat:
        (BASE/'logs/telegram_notify_failed.txt').write_text('Missing token/chat id\n'+msg)
        return
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id':chat,'text':msg}, timeout=30).raise_for_status()
def main():
    notified=BASE/'logs/phase1_done_notified.txt'
    if notified.exists(): return
    while True:
        counts={c:count(OUT/f'{c}.jsonl') for c in CODERS}
        fails={c:count(OUT/f'{c}.failed.jsonl') for c in CODERS}
        if all(v>=300 for v in counts.values()):
            subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', str(BASE/'build_layer_a_consensus.py')], cwd=str(ROOT), check=True)
            msg='Layered values Phase 1 initial work is done: Layer A coder outputs are 300/300 for DeepSeek, Kimi, and GLM; consensus_300.jsonl and qa_report.md have been generated.'
            send(msg); notified.write_text(msg+'\n'); return
        if not running() and any(v<300 for v in counts.values()):
            msg=f'Layered values Phase 1 is blocked/stopped before completion. Counts: {counts}; failures: {fails}. Please check logs.'
            send(msg); notified.write_text(msg+'\n'); return
        time.sleep(60)
if __name__=='__main__': main()
