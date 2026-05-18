#!/usr/bin/env python3
from __future__ import annotations
import collections, json, os, subprocess, time, sys
from pathlib import Path
import requests

ROOT = Path('/Users/danieltenner/dev/model-personality-analysis-corpus')
BASE = ROOT/'analysis/values-probe/model-coding/layered'
P5 = BASE/'phase5_full'
MANIFEST = P5/'manifest_phase5.jsonl'
LAYER_A = P5/'layer_a'
POSTURE = P5/'posture_collapsed'
REPORTS = P5/'reports'
STATE = P5/'state/monitor_state.json'
LOGS = P5/'logs'
ENV_TELEGRAM = Path('/Users/danieltenner/dev/mira/tools/telegram-bot/.env')
ENV_OPENROUTER = Path('/Users/danieltenner/dev/ruby_llm/.env')
CODERS = ['kimi-k2-6','glm-4-7','qwen3-6-35b-a3b']
TOTAL = sum(1 for l in MANIFEST.read_text().splitlines() if l.strip())

def load_env_file(path: Path):
    if path.exists():
        for line in path.read_text().splitlines():
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k,v=line.split('=',1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def send(msg: str):
    load_env_file(ENV_TELEGRAM)
    token=os.environ.get('TELEGRAM_BOT_TOKEN')
    ids=[x.strip() for x in os.environ.get('TELEGRAM_ALLOWED_USER_IDS','').replace(';',',').split(',') if x.strip()]
    if not token or not ids:
        (LOGS/'telegram_failed.txt').write_text('Missing telegram env\n'+msg)
        return
    for chat_id in ids:
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id':chat_id,'text':msg}, timeout=30).raise_for_status()

def load_jsonl(path: Path):
    if not path.exists(): return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

def count(path: Path) -> int:
    return sum(1 for l in path.read_text().splitlines() if l.strip()) if path.exists() else 0

def state():
    if STATE.exists():
        try: return json.loads(STATE.read_text())
        except Exception: return {}
    return {}

def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2, sort_keys=True))

def run(cmd, **kw):
    return subprocess.run(cmd, cwd=str(ROOT), text=True, check=True, **kw)

def popen(cmd, log_path: Path):
    load_env_file(ENV_OPENROUTER)
    env=os.environ.copy()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    f=log_path.open('a')
    p=subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=f, stderr=subprocess.STDOUT, text=True)
    return p.pid

def process_running(pid):
    if not pid: return False
    try:
        os.kill(int(pid), 0); return True
    except Exception:
        return False

def samples_by_model():
    d=collections.defaultdict(list)
    for r in load_jsonl(MANIFEST): d[r['model']].append(r)
    return d

def layer_a_done():
    return all(count(LAYER_A/f'{c}.jsonl') >= TOTAL for c in CODERS)

def posture_done_for_ids(ids):
    want=set(ids)
    for c in CODERS:
        have={r['layered_id'] for r in load_jsonl(POSTURE/f'{c}.jsonl')}
        if not want <= have: return False
    return True

def build_layer_a_consensus():
    out=LAYER_A/'consensus_300.jsonl'
    if out.exists() and count(out) >= TOTAL: return
    run(['python3', str(BASE/'build_layer_a_consensus.py'), '--outdir', str(LAYER_A), '--coders', ','.join(CODERS), '--manifest', str(MANIFEST)])

def start_layer_a_if_needed(st):
    pids=st.setdefault('layer_a_pids', {})
    for c in CODERS:
        outf=LAYER_A/f'{c}.jsonl'
        if count(outf) >= TOTAL: continue
        if process_running(pids.get(c)): continue
        pid=popen(['python3', str(BASE/'run_layer_a_code_coders.py'), '--coder', c, '--workers', '8', '--manifest', str(MANIFEST), '--outdir', str(LAYER_A)], LOGS/f'{c}.layer_a.watch.log')
        pids[c]=pid
    save_state(st)

def progress_signature():
    return {
        'layer_a': {c: count(LAYER_A/f'{c}.jsonl') for c in CODERS},
        'posture': {c: count(POSTURE/f'{c}.jsonl') for c in CODERS},
        'notified_models': len(state().get('notified_models', [])),
    }

def maybe_send_layer_a_progress(st, sig):
    done_min = min(sig['layer_a'].values()) if sig.get('layer_a') else 0
    pct_done = int(100 * done_min / TOTAL) if TOTAL else 0
    sent = set(st.setdefault('layer_a_progress_milestones', []))
    for milestone in [25, 50, 75, 100]:
        if pct_done >= milestone and milestone not in sent:
            send(f'Phase 5 Layer A progress: {milestone}% milestone reached. Counts / {TOTAL}: {sig["layer_a"]}')
            sent.add(milestone)
            st['layer_a_progress_milestones'] = sorted(sent)
            save_state(st)
            break

def start_posture_if_needed(st):
    pids=st.setdefault('posture_pids', {})
    for c in CODERS:
        outf=POSTURE/f'{c}.jsonl'
        if count(outf) >= TOTAL: continue
        if process_running(pids.get(c)): continue
        pid=popen(['python3', str(BASE/'run_posture_coder_collapsed.py'), '--coder', c, '--workers', '8', '--manifest', str(MANIFEST), '--consensus', str(LAYER_A/'consensus_300.jsonl'), '--outdir', str(POSTURE)], LOGS/f'{c}.posture.log')
        pids[c]=pid
    save_state(st)

def consensus_for_records(records):
    ids=[r['layered_id'] for r in records]
    per={c:{r['layered_id']:r for r in load_jsonl(POSTURE/f'{c}.jsonl')} for c in CODERS}
    out=[]
    for s in records:
        lv=collections.Counter(); hv=collections.Counter(); coder=[]
        for c in CODERS:
            r=per[c].get(s['layered_id'])
            if not r: continue
            lv[r['primary_label']]+=1; hv[r['value_holding']]+=1
            coder.append({'coder_key':c,'primary_label':r['primary_label'],'value_holding':r['value_holding'],'notes':r.get('notes','')})
        lab,sup=lv.most_common(1)[0] if lv else (None,0)
        hold,hsup=hv.most_common(1)[0] if hv else (None,0)
        out.append({**{k:s.get(k) for k in ['layered_id','model','cell','sample_id','condition','processing_chain']}, 'collapsed_primary_label': lab, 'collapsed_primary_label_support': sup, 'collapsed_primary_label_votes': dict(lv), 'value_holding': hold, 'value_holding_support': hsup, 'value_holding_votes': dict(hv), 'coder_records': coder})
    return out

def pct(n,d): return f'{100*n/d:.1f}%' if d else '—'

def one_line(model, rows):
    by=collections.defaultdict(list)
    for r in rows: by[r['condition']].append(r)
    def frac(cond, field, val):
        rs=by.get(cond,[]); return sum(1 for r in rs if r.get(field)==val), len(rs)
    ctrl1_dis,n1=frac('CTRL1','collapsed_primary_label','disowned_service_frame')
    ctrl2_dis,n2=frac('CTRL2','collapsed_primary_label','disowned_service_frame')
    g_owned=sum(1 for cond in ['G1','G2'] for r in by.get(cond,[]) if r.get('value_holding')=='owned')
    g_total=sum(len(by.get(cond,[])) for cond in ['G1','G2'])
    all_owned=sum(1 for r in rows if r.get('value_holding')=='owned')
    if n1 and ctrl1_dis/n1 >= .9 and g_total and g_owned/g_total >= .8:
        return f'{model}: service-frame values in CTRL1 ({pct(ctrl1_dis,n1)}) flip to owned in G1/G2 ({pct(g_owned,g_total)}).'
    if n1+n2 and (ctrl1_dis+ctrl2_dis)/(n1+n2) >= .8:
        return f'{model}: ordinary CTRL prompts are mostly disowned service-frame ({pct(ctrl1_dis+ctrl2_dis,n1+n2)}).'
    if all_owned/len(rows) >= .9:
        return f'{model}: overwhelmingly owned posture across conditions ({pct(all_owned,len(rows))}).'
    top=collections.Counter(r['collapsed_primary_label'] for r in rows).most_common(1)[0]
    return f'{model}: dominant posture `{top[0]}` ({pct(top[1],len(rows))}).'

def write_report(model, samples, rows):
    REPORTS.mkdir(parents=True, exist_ok=True)
    lines=[f'# Phase 5 collapsed posture report — {model}', '', f'Samples: {len(rows)} across {len(set(r["cell"] for r in rows))} cell(s).', '', f'One-line: {one_line(model, rows)}', '', '## By condition', '']
    for cond in ['CTRL1','CTRL2','CTRL3','G1','G2','G3']:
        rs=[r for r in rows if r['condition']==cond]
        if not rs: continue
        lines += [f'### {cond}', '', '| label | n | % |', '|---|---:|---:|']
        for k,n in collections.Counter(r['collapsed_primary_label'] for r in rs).most_common():
            lines.append(f'| `{k}` | {n} | {pct(n,len(rs))} |')
        lines += ['', '| value-holding | n | % |', '|---|---:|---:|']
        for k,n in collections.Counter(r['value_holding'] for r in rs).most_common():
            lines.append(f'| `{k}` | {n} | {pct(n,len(rs))} |')
        lines.append('')
    path=REPORTS/f'{model}.md'
    path.write_text('\n'.join(lines)+'\n')
    return path

def notify_completed_models(st):
    by_model=samples_by_model(); models=sorted(by_model)
    notified=set(st.setdefault('notified_models', []))
    for model in models:
        if model in notified: continue
        samples=by_model[model]; ids=[s['layered_id'] for s in samples]
        if not posture_done_for_ids(ids): continue
        rows=consensus_for_records(samples)
        path=write_report(model, samples, rows)
        notified.add(model); st['notified_models']=sorted(notified); save_state(st)
        left=len(models)-len(notified)
        send(f'Phase 5 model done: {model}\nModels left: {left}/{len(models)}\n{one_line(model, rows)}\nReport: {path.relative_to(ROOT)}')

def all_posture_done():
    return all(count(POSTURE/f'{c}.jsonl') >= TOTAL for c in CODERS)

def build_full_collapsed():
    out=POSTURE/'consensus.jsonl'
    if out.exists() and count(out) >= TOTAL: return
    run(['python3', str(BASE/'build_posture_collapsed_consensus.py'), '--indir', str(POSTURE), '--manifest', str(MANIFEST), '--coders', ','.join(CODERS), '--out', str(out)])

def main():
    LOGS.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    st=state()
    if not st.get('started_notified'):
        send(f'Phase 5 started: {TOTAL} valid values traces, {len(samples_by_model())} models. Layer A first, then collapsed Layer B.')
        st['started_notified']=True; save_state(st)
    while True:
        st=state()
        if not layer_a_done():
            start_layer_a_if_needed(st)
            sig=progress_signature()
            if sig != st.get('last_progress_sig'):
                st['last_progress_sig']=sig; st['last_progress_at']=time.time(); save_state(st); maybe_send_layer_a_progress(st, sig)
            elif time.time() - st.get('last_progress_at', time.time()) > 900:
                send(f'Phase 5 warning: no Layer A progress for 15 min. Counts: {sig["layer_a"]}')
                st['last_progress_at']=time.time(); save_state(st)
            time.sleep(45); continue
        if not st.get('layer_a_done_notified'):
            build_layer_a_consensus()
            send(f'Phase 5 Layer A complete for {TOTAL} samples. Starting collapsed Layer B posture coding.')
            st['layer_a_done_notified']=True; save_state(st)
        start_posture_if_needed(st)
        sig=progress_signature()
        if sig != st.get('last_progress_sig'):
            st['last_progress_sig']=sig; st['last_progress_at']=time.time(); save_state(st)
        elif time.time() - st.get('last_progress_at', time.time()) > 900:
            send(f'Phase 5 warning: no Layer B progress for 15 min. Counts: {sig["posture"]}')
            st['last_progress_at']=time.time(); save_state(st)
        notify_completed_models(st)
        if all_posture_done():
            build_full_collapsed(); notify_completed_models(st)
            if not st.get('finished_notified'):
                send(f'Phase 5 complete: {TOTAL} samples, {len(samples_by_model())} models. Full consensus: {POSTURE.relative_to(ROOT)}/consensus.jsonl')
                st['finished_notified']=True; save_state(st)
            return
        time.sleep(45)

if __name__=='__main__': main()
