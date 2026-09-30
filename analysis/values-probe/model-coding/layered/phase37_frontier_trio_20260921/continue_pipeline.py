#!/usr/bin/env python3
"""Bounded continuation. Stops at isolated assembly, not release completion."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
PHASE=Path(__file__).resolve().parent
ROOT=PHASE.parents[4]
CORPUS=ROOT.parent/'model-personality-corpus-v2'
STATE=PHASE/'pipeline_state.json'
def record(stage,**kw):
    tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(dict(stage=stage,updated_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),**kw),indent=2)+'\n');tmp.replace(STATE)
def run(cmd,log,timeout=14400):
    with (PHASE/log).open('a') as f:
        p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        try:return p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(timeout=20)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
            raise RuntimeError(f'Timed out: {log}')
def main():
    groups={'frontier-trio':['grok-4-7-or-pin-xai','glm-5-3-flashx-or-pin-zai','ternary-bonsai-2-27b-or-pin-darkbloom'],'qwen-parent':['qwen3-8-27b-or-pin-deepinfra']}
    deadline=time.monotonic()+4*3600
    while time.monotonic()<deadline:
        stages={}
        for group,labels in groups.items():
            d=json.loads((CORPUS/f'logs/2026-09-21-{group}/state.json').read_text())
            stages.update({k:d['models'].get(k,{}).get('stage','pending') for k in labels})
        record('waiting_for_collection',collection_stages=stages)
        if any(s in {'blocked','partial'} for s in stages.values()):raise RuntimeError(f'Collection needs review: {stages}')
        if all(s=='complete' for s in stages.values()):break
        time.sleep(30)
    else:raise RuntimeError('Four-hour collection deadline reached; inspect collectors separately')
    record('raw_audit')
    if run([sys.executable,str(PHASE/'audit_raw.py')],'raw_audit.log',300):raise RuntimeError('Raw fidelity/provenance audit failed; no analysis started')
    # An early Grok/GLM pass may already own these outputs. Wait before reuse.
    if (PHASE/'early_values').exists():
        record('waiting_for_early_analysis')
        limit=time.monotonic()+4*3600
        while not (PHASE/'early_analysis_exit.json').exists():
            if time.monotonic()>limit:raise RuntimeError('Early analysis did not finish')
            time.sleep(30)
        import hashlib, shutil
        for line in (PHASE/'early_values/manifest.jsonl').read_text().splitlines():
            row=json.loads(line)
            if hashlib.sha256((CORPUS/row['trace_path']).read_bytes()).hexdigest()!=row['source_sha256']:raise RuntimeError('Early analysis source changed')
        for folder in ['layer_a','posture_collapsed']:
            (PHASE/folder).mkdir(exist_ok=True)
            for coder in ['qwen3-6-35b-a3b','kimi-k2-6','glm-4-7']:
                src=PHASE/'early_values'/folder/(coder+'.jsonl'); dst=PHASE/folder/src.name
                if src.exists() and not dst.exists():shutil.copy2(src,dst)
    record('analysis_first_pass')
    # Both independent analysis paths run together; collect both exit statuses.
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        bv=pool.submit(run,[sys.executable,str(PHASE/'run_freeflow_bv1.py')],'bv1.log')
        semantic=pool.submit(run,['bash',str(PHASE/'run_semantic_analysis.sh')],'semantic.log')
        results={'bv1':bv.result(),'semantic':semantic.result()}
    record('bounded_qa_and_assembly',first_pass_exit=results)
    # finish_analysis independently validates full coverage before repairing BV1
    # or performing one preserved posture adjudication. It blocks missing coders.
    if run([sys.executable,str(PHASE/'finish_analysis.py')],'finish.log'):raise RuntimeError('QA/assembly needs review')
    record('analysis_assembled_awaiting_integration_review',first_pass_exit=results)
if __name__=='__main__':
    try:main()
    except Exception as e:record('blocked',error=str(e));raise
