#!/usr/bin/env python3
"""Watch/restart Layer A code-protocol coders until 300/300 each.

This is deliberately conservative: it restarts missing workers, and also
restarts a coder if its output count has not advanced for STALL_SECONDS.
"""
import json, os, signal, subprocess, time
from pathlib import Path
import requests
ROOT=Path('/Users/danieltenner/dev/model-personality-analysis-corpus')
BASE=ROOT/'analysis/values-probe/model-coding/layered'
OUT=BASE/'layer_a_code'
LOGS=BASE/'logs'
CODERS=['deepseek-v4-pro','kimi-k2-6','glm-4-7']
PYTHON='/Library/Frameworks/Python.framework/Versions/3.11/bin/python3'
ENV_KEYS=Path('/Users/danieltenner/dev/model-personality-corpus-v2/keys.env')
TG_ENV=Path('/Users/danieltenner/dev/mira/tools/telegram-bot/.env')
STATE=LOGS/'phase1_code_watch_state.json'
STALL_SECONDS=15*60
def count(p): return sum(1 for l in p.read_text().splitlines() if l.strip()) if p.exists() else 0
def load_dotenv(path):
    if path.exists():
        for line in path.read_text().splitlines():
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line or line.startswith('export '): continue
            k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
def running_for(coder):
    try: out=subprocess.check_output(['pgrep','-fl',f'run_layer_a_code_coders.py --coder {coder}'], text=True)
    except subprocess.CalledProcessError: return False
    return bool(out.strip())
def pids_for(coder):
    try:
        out=subprocess.check_output(['pgrep','-f',f'run_layer_a_code_coders.py --coder {coder}'], text=True)
    except subprocess.CalledProcessError:
        return []
    return [int(x) for x in out.split() if x.strip().isdigit()]
def stop(coder):
    for pid in pids_for(coder):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    time.sleep(2)
    for pid in pids_for(coder):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
def start(coder):
    # Use bash to source keys.env exactly as other corpus scripts do.
    LOGS.mkdir(parents=True, exist_ok=True)
    log=LOGS/f'{coder}.layer_a_code.watch.log'
    cmd=f"set -a; source {ENV_KEYS} >/dev/null 2>&1 || true; set +a; cd {ROOT}; {PYTHON} -u analysis/values-probe/model-coding/layered/run_layer_a_code_coders.py --coder {coder} --workers 3"
    with log.open('a') as fh:
        fh.write(f'\n--- restart {time.strftime("%Y-%m-%d %H:%M:%S")} ---\n'); fh.flush()
        p=subprocess.Popen(['bash','-lc',cmd], stdout=fh, stderr=subprocess.STDOUT)
    (LOGS/f'{coder}.layer_a_code.watch.pid').write_text(str(p.pid)+'\n')
def send(msg):
    load_dotenv(TG_ENV); token=os.environ.get('TELEGRAM_BOT_TOKEN'); ids=os.environ.get('TELEGRAM_ALLOWED_USER_IDS','')
    chat=(ids.split(',')[0].strip() if ids else os.environ.get('TELEGRAM_CHAT_ID',''))
    if not token or not chat:
        (LOGS/'telegram_notify_failed_code_watch.txt').write_text('Missing token/chat id\n'+msg); return
    requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id':chat,'text':msg}, timeout=30).raise_for_status()
def main():
    done_file=LOGS/'phase1_code_watch_done.txt'
    counts={c:count(OUT/f'{c}.jsonl') for c in CODERS}
    if all(v>=300 for v in counts.values()):
        if not done_file.exists():
            send(f'Layered values Phase 1 code-protocol run completed: {counts}.')
            done_file.write_text(str(counts)+'\n')
        return
    now=time.time()
    state_missing=not STATE.exists()
    try:
        state=json.loads(STATE.read_text())
    except Exception:
        state={'coders':{}}
    changed=state_missing
    for c in CODERS:
        n=counts[c]
        rec=state.setdefault('coders',{}).setdefault(c, {'count': n, 'last_progress': now})
        if n > rec.get('count', -1):
            rec['count']=n
            rec['last_progress']=now
            changed=True
        if n<300 and not running_for(c):
            start(c)
            rec['last_restart']=now
            rec['restart_reason']='not_running'
            changed=True
        elif n<300 and now-rec.get('last_progress', now) > STALL_SECONDS:
            stop(c)
            start(c)
            rec['last_restart']=now
            rec['restart_reason']=f'stalled_{STALL_SECONDS}s'
            rec['last_progress']=now
            changed=True
    if changed:
        STATE.write_text(json.dumps(state, indent=2, sort_keys=True)+'\n')
    # Write heartbeat every tick.
    counts2={c:count(OUT/f'{c}.jsonl') for c in CODERS}
    (LOGS/'phase1_code_watch_heartbeat.txt').write_text(f'{time.strftime("%Y-%m-%d %H:%M:%S")} counts={counts2}\n')
if __name__=='__main__': main()
