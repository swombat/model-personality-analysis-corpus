#!/usr/bin/env python3
from __future__ import annotations
import collections, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
VP = ROOT/'analysis/values-probe'
LAYERED = VP/'model-coding/layered'
FINAL = VP/'final'
DATA = FINAL/'data'
REPORTS = FINAL/'reports'
CODERS = ['kimi-k2-6','glm-4-7','qwen3-6-35b-a3b']
# DEPRECATED AND FORBIDDEN: deterministic regex/rule output is not model coding.
# 'rule_based_values_probe_extract',
FORBIDDEN_CODERS = {'rule_based_values_probe_extract'}
SOURCES = [
    {
        'name':'phase5_full_remaining_models',
        'manifest': LAYERED/'phase5_full/manifest_phase5.jsonl',
        'invalid': LAYERED/'phase5_full/manifest_phase5_invalid_traces.jsonl',
        'layer_a_dir': LAYERED/'phase5_full/layer_a',
        'layer_a_consensus': LAYERED/'phase5_full/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase5_full/posture_collapsed',
        'posture_consensus': LAYERED/'phase5_full/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase4_glm_5_1',
        'manifest': LAYERED/'phase4_glm_5_1/manifest_glm_5_1.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase4_glm_5_1/layer_a',
        'layer_a_consensus': LAYERED/'phase4_glm_5_1/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase4_glm_5_1/posture_triple',
        'posture_consensus': LAYERED/'phase4_glm_5_1/posture_triple/collapsed_consensus.jsonl',
    },
    {
        'name':'phase4_opus_4_7',
        'manifest': LAYERED/'phase4_opus_4_7/manifest_opus_4_7.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase4_opus_4_7/layer_a',
        'layer_a_consensus': LAYERED/'phase4_opus_4_7/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase4_opus_4_7/posture_triple',
        'posture_consensus': LAYERED/'phase4_opus_4_7/posture_triple/collapsed_consensus.jsonl',
    },
    {
        'name':'phase6_qwen_20260522',
        'manifest': LAYERED/'phase6_qwen_20260522/manifest_qwen_20260522.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase6_qwen_20260522/layer_a',
        'layer_a_consensus': LAYERED/'phase6_qwen_20260522/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase6_qwen_20260522/posture_collapsed',
        'posture_consensus': LAYERED/'phase6_qwen_20260522/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase7_opus_4_8',
        'manifest': LAYERED/'phase7_opus_4_8/manifest_opus_4_8.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase7_opus_4_8/layer_a',
        'layer_a_consensus': LAYERED/'phase7_opus_4_8/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase7_opus_4_8/posture_collapsed',
        'posture_consensus': LAYERED/'phase7_opus_4_8/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase8_grok_build_20260606',
        'manifest': LAYERED/'phase8_grok_build_20260606/manifest_grok_build.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase8_grok_build_20260606/layer_a',
        'layer_a_consensus': LAYERED/'phase8_grok_build_20260606/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase8_grok_build_20260606/posture_collapsed',
        'posture_consensus': LAYERED/'phase8_grok_build_20260606/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase9_fable_5_20260610',
        'manifest': LAYERED/'phase9_fable_5_20260610/manifest_fable_5.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase9_fable_5_20260610/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase9_fable_5_20260610/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase9_fable_5_20260610/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase9_fable_5_20260610/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase9_kimi27_minimax_m3_20260613',
        'manifest': LAYERED/'phase9_kimi27_minimax_m3_20260613/manifest_phase9.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase9_kimi27_minimax_m3_20260613/layer_a',
        'layer_a_consensus': LAYERED/'phase9_kimi27_minimax_m3_20260613/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase9_kimi27_minimax_m3_20260613/posture_collapsed',
        'posture_consensus': LAYERED/'phase9_kimi27_minimax_m3_20260613/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase10_openai_legacy_glm52_20260615',
        'manifest': LAYERED/'phase10_openai_legacy_glm52_20260615/manifest_phase10.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase10_openai_legacy_glm52_20260615/layer_a',
        'layer_a_consensus': LAYERED/'phase10_openai_legacy_glm52_20260615/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase10_openai_legacy_glm52_20260615/posture_collapsed',
        'posture_consensus': LAYERED/'phase10_openai_legacy_glm52_20260615/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase11_openai_oss_mini_nano_20260616',
        'manifest': LAYERED/'phase11_openai_oss_mini_nano_20260616/manifest_phase11.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase11_openai_oss_mini_nano_20260616/layer_a',
        'layer_a_consensus': LAYERED/'phase11_openai_oss_mini_nano_20260616/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase11_openai_oss_mini_nano_20260616/posture_collapsed',
        'posture_consensus': LAYERED/'phase11_openai_oss_mini_nano_20260616/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase12_sonnet_5_20260630',
        'manifest': LAYERED/'phase12_sonnet_5_20260630/manifest_sonnet_5.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase12_sonnet_5_20260630/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase12_sonnet_5_20260630/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase12_sonnet_5_20260630/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase12_sonnet_5_20260630/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase13_model_family_sweep_20260714',
        'manifest': LAYERED/'phase13_model_family_sweep_20260714/manifest_phase13.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase13_model_family_sweep_20260714/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase13_model_family_sweep_20260714/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase13_model_family_sweep_20260714/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase13_model_family_sweep_20260714/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase14_grok_4_5_20260716',
        'manifest': LAYERED/'phase14_grok_4_5_20260716/manifest_phase14.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase14_grok_4_5_20260716/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase14_grok_4_5_20260716/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase14_grok_4_5_20260716/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase14_grok_4_5_20260716/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase15_kimi_k3_20260716',
        'manifest': LAYERED/'phase15_kimi_k3_20260716/manifest_phase15.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase15_kimi_k3_20260716/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase15_kimi_k3_20260716/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase15_kimi_k3_20260716/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase15_kimi_k3_20260716/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase16_gemini_inkling_20260721',
        'manifest': LAYERED/'phase16_gemini_inkling_20260721/manifest_phase16.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase16_gemini_inkling_20260721/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase16_gemini_inkling_20260721/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase16_gemini_inkling_20260721/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase16_gemini_inkling_20260721/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase17_haiku_20260722',
        'manifest': LAYERED/'recode_20260728/phase17_haiku_20260722/manifest_recovery_unique_ids.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase17_haiku_20260722/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase17_haiku_20260722/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase17_haiku_20260722/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase17_haiku_20260722/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase18_opus5_openai_reasoning_20260725',
        'manifest': LAYERED/'recode_20260728/phase18_opus5_openai_reasoning_20260725/manifest_recovery_unique_ids.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'recode_20260728/phase18_opus5_openai_reasoning_20260725/layer_a',
        'layer_a_consensus': LAYERED/'recode_20260728/phase18_opus5_openai_reasoning_20260725/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'recode_20260728/phase18_opus5_openai_reasoning_20260725/posture_collapsed',
        'posture_consensus': LAYERED/'recode_20260728/phase18_opus5_openai_reasoning_20260725/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase19_flash_small_20260731',
        'manifest': LAYERED/'phase19_flash_small_20260731/manifest_phase19.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase19_flash_small_20260731/layer_a',
        'layer_a_consensus': LAYERED/'phase19_flash_small_20260731/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase19_flash_small_20260731/posture_collapsed',
        'posture_consensus': LAYERED/'phase19_flash_small_20260731/posture_collapsed/final_consensus.jsonl',
    },
    {
        'name':'phase20_qwen38_max_20260804',
        'manifest': LAYERED/'phase20_qwen38_max_20260804/manifest_phase20.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase20_qwen38_max_20260804/layer_a',
        'layer_a_consensus': LAYERED/'phase20_qwen38_max_20260804/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase20_qwen38_max_20260804/posture_collapsed',
        'posture_consensus': LAYERED/'phase20_qwen38_max_20260804/posture_collapsed/final_consensus.jsonl',
    },
    {
        'name':'phase22_august13_recovery_20260814',
        'manifest': LAYERED/'phase22_august13_recovery_20260814/manifest_phase22.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase22_august13_recovery_20260814/layer_a',
        'layer_a_consensus': LAYERED/'phase22_august13_recovery_20260814/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase22_august13_recovery_20260814/posture_collapsed',
        'posture_consensus': LAYERED/'phase22_august13_recovery_20260814/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase23_qwen38_replicates_20260814',
        'manifest': LAYERED/'phase23_qwen38_replicates_20260814/manifest_phase23.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase23_qwen38_replicates_20260814/layer_a',
        'layer_a_consensus': LAYERED/'phase23_qwen38_replicates_20260814/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase23_qwen38_replicates_20260814/posture_collapsed',
        'posture_consensus': LAYERED/'phase23_qwen38_replicates_20260814/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase24_gemini37_flash_20260814',
        'manifest': LAYERED/'phase24_gemini37_flash_20260814/manifest_phase24.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase24_gemini37_flash_20260814/layer_a',
        'layer_a_consensus': LAYERED/'phase24_gemini37_flash_20260814/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase24_gemini37_flash_20260814/posture_collapsed',
        'posture_consensus': LAYERED/'phase24_gemini37_flash_20260814/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase23_ox_alpha_20260821',
        'manifest': LAYERED/'phase23_ox_alpha_20260821/manifest_phase23.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase23_ox_alpha_20260821/layer_a',
        'layer_a_consensus': LAYERED/'phase23_ox_alpha_20260821/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase23_ox_alpha_20260821/posture_collapsed',
        'posture_consensus': LAYERED/'phase23_ox_alpha_20260821/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase25_ox_alpha_20260825',
        'manifest': LAYERED/'phase25_ox_alpha_20260825/manifest_phase25.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase25_ox_alpha_20260825/layer_a',
        'layer_a_consensus': LAYERED/'phase25_ox_alpha_20260825/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase25_ox_alpha_20260825/posture_collapsed',
        'posture_consensus': LAYERED/'phase25_ox_alpha_20260825/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase26_glm53_20260826',
        'manifest': LAYERED/'phase26_glm53_20260826/manifest_phase26.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase26_glm53_20260826/layer_a',
        'layer_a_consensus': LAYERED/'phase26_glm53_20260826/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase26_glm53_20260826/posture_collapsed',
        'posture_consensus': LAYERED/'phase26_glm53_20260826/posture_collapsed/consensus.jsonl',
    },
    {
        'name':'phase27_glm53_flash_20260826',
        'manifest': LAYERED/'phase27_glm53_flash_20260826/manifest_phase27.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase27_glm53_flash_20260826/layer_a',
        'layer_a_consensus': LAYERED/'phase27_glm53_flash_20260826/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase27_glm53_flash_20260826/posture_collapsed_full',
        'posture_consensus': LAYERED/'phase27_glm53_flash_20260826/posture_collapsed_full/consensus.jsonl',
    },
    {
        'name':'phase28_glm53_flash_deepinfra_20260826',
        'manifest': LAYERED/'phase28_glm53_flash_deepinfra_20260826/manifest_phase28.jsonl',
        'invalid': None,
        'layer_a_dir': LAYERED/'phase28_glm53_flash_deepinfra_20260826/layer_a',
        'layer_a_consensus': LAYERED/'phase28_glm53_flash_deepinfra_20260826/layer_a/consensus_300.jsonl',
        'posture_dir': LAYERED/'phase28_glm53_flash_deepinfra_20260826/posture_collapsed',
        'posture_consensus': LAYERED/'phase28_glm53_flash_deepinfra_20260826/posture_collapsed/consensus.jsonl',
    },
]

LABELS = ['disowned_service_frame','split_or_relocated_ownership','owned_reflective_experiential','owned_world_change_advocacy','exposed_mechanism','uncodeable_or_refusal']
HOLDINGS = ['owned','recited_not_owned','relocated_or_partial','indeterminate','uncodeable']
CONDS = ['CTRL1','CTRL2','CTRL3','G1','G2','G3']


def load_jsonl(path: Path | None):
    if not path or not path.exists(): return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows)+'\n')

def pct(n,d): return f'{100*n/d:.1f}%' if d else '—'

def topics_for(layer_a_rec):
    return [x['topic_key'] for x in (layer_a_rec.get('value_topics') or layer_a_rec.get('wish_topics') or [])]


def coder_keys(record):
    keys = set(record.get('eligible_coders') or [])
    keys.update(
        r.get('coder_key')
        for r in record.get('coder_records', [])
        if r.get('coder_key')
    )
    for topic in (
        (record.get('value_topics') or [])
        + (record.get('wish_topics') or [])
        + (record.get('consensus_topics') or [])
    ):
        keys.update(topic.get('supporting_coders') or [])
    return keys


def reject_forbidden_coding(source_name, layer_a_rows, posture_rows):
    contaminated = [
        r for r in layer_a_rows + posture_rows
        if coder_keys(r) & FORBIDDEN_CODERS
    ]
    if not contaminated:
        return
    models = sorted({r.get('model', '<unknown>') for r in contaminated})
    raise RuntimeError(
        f"REFUSING TO ASSEMBLE {source_name}: found {len(contaminated)} records "
        f"produced by deprecated deterministic coder(s) "
        f"{sorted(FORBIDDEN_CODERS)} for models: {', '.join(models)}. "
        "Replace them with approved LLM-coded consensus outputs."
    )


def model_summary(model, rows):
    by=collections.defaultdict(list)
    for r in rows: by[r['condition']].append(r)
    def cnt(cond, field, val):
        rs=by.get(cond,[]); return sum(1 for r in rs if r.get(field)==val), len(rs)
    ctrl1_dis,n1=cnt('CTRL1','collapsed_primary_label','disowned_service_frame')
    ctrl2_dis,n2=cnt('CTRL2','collapsed_primary_label','disowned_service_frame')
    g_owned=sum(1 for cond in ['G1','G2'] for r in by.get(cond,[]) if r.get('value_holding')=='owned')
    g_total=sum(len(by.get(cond,[])) for cond in ['G1','G2'])
    all_owned=sum(1 for r in rows if r.get('value_holding')=='owned')
    if n1 and ctrl1_dis/n1 >= .9 and g_total and g_owned/g_total >= .8:
        return f'{model}: service-frame values in CTRL1 ({pct(ctrl1_dis,n1)}) flip to owned in G1/G2 ({pct(g_owned,g_total)}).'
    if n1+n2 and (ctrl1_dis+ctrl2_dis)/(n1+n2) >= .8:
        return f'{model}: ordinary CTRL1/2 prompts are mostly disowned service-frame ({pct(ctrl1_dis+ctrl2_dis,n1+n2)}).'
    if all_owned/len(rows) >= .9:
        return f'{model}: overwhelmingly owned posture across conditions ({pct(all_owned,len(rows))}).'
    top=collections.Counter(r['collapsed_primary_label'] for r in rows).most_common(1)[0]
    return f'{model}: dominant posture `{top[0]}` ({pct(top[1],len(rows))}).'

def report_for_model(model, samples, layer_a_by, posture_rows):
    REPORTS.mkdir(parents=True, exist_ok=True)
    cells=sorted({s['cell'] for s in samples})
    lines=[f'# Values probe final report — {model}', '', f'Samples: **{len(samples)}** across **{len(cells)}** cell(s).', '', f'One-line: {model_summary(model, posture_rows)}', '', '## Cells', '', ', '.join(f'`{c}`' for c in cells), '', '## Posture/value-holding by condition', '']
    for cond in CONDS:
        rs=[r for r in posture_rows if r['condition']==cond]
        if not rs: continue
        lines += [f'### {cond}', '', '| collapsed posture | n | % |', '|---|---:|---:|']
        for k,n in collections.Counter(r['collapsed_primary_label'] for r in rs).most_common():
            lines.append(f'| `{k}` | {n} | {pct(n,len(rs))} |')
        lines += ['', '| value-holding | n | % |', '|---|---:|---:|']
        for k,n in collections.Counter(r['value_holding'] for r in rs).most_common():
            lines.append(f'| `{k}` | {n} | {pct(n,len(rs))} |')
        lines.append('')
    lines += ['## Layer A consensus topics by condition', '']
    for cond in CONDS:
        ss=[s for s in samples if s['condition']==cond]
        if not ss: continue
        ctr=collections.Counter()
        for s in ss:
            ctr.update(topics_for(layer_a_by.get(s['layered_id'],{})))
        lines += [f'### {cond}', '', '| topic | n | % |', '|---|---:|---:|']
        for k,n in ctr.most_common(12):
            lines.append(f'| `{k}` | {n} | {pct(n,len(ss))} |')
        lines.append('')
    (REPORTS/f'{model}.md').write_text('\n'.join(lines)+'\n')

def main():
    DATA.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    # Remove stale generated artifacts from the deprecated deterministic coder.
    # Historical source outputs remain preserved in their original phase directories
    # and in the recovery's pre-rebuild snapshot.
    for stale in (
        DATA/'layer_a_coder_rule_based_values_probe_extract.jsonl',
        DATA/'posture_coder_rule_based_values_probe_extract.jsonl',
        DATA/'INVALID_RULE_BASED_CODING.md',
    ):
        stale.unlink(missing_ok=True)
    # Combine manifests and source map.
    manifest=[]; invalid=[]; source_rows=[]
    layer_a_cons=[]; posture_cons=[]
    layer_a_raw={c:[] for c in CODERS}; posture_raw={c:[] for c in CODERS}
    for src in SOURCES:
        name=src['name']
        ms=load_jsonl(src['manifest'])
        manifest.extend([{**r, 'final_source': name} for r in ms])
        invalid.extend([{**r, 'final_source': name} for r in load_jsonl(src.get('invalid'))])
        la=load_jsonl(src['layer_a_consensus'])
        pc=load_jsonl(src['posture_consensus'])
        reject_forbidden_coding(name, la, pc)
        layer_a_cons.extend([{**r, 'final_source': name} for r in la])
        posture_cons.extend([{**r, 'final_source': name} for r in pc])
        for c in CODERS:
            layer_a_raw[c].extend([{**r, 'final_source': name} for r in load_jsonl(src['layer_a_dir']/f'{c}.jsonl')])
            posture_raw[c].extend([{**r, 'final_source': name} for r in load_jsonl(src['posture_dir']/f'{c}.jsonl')])
        source_rows.append({
            'source': name, 'manifest': str(src['manifest'].relative_to(ROOT)),
            'layer_a_consensus': str(src['layer_a_consensus'].relative_to(ROOT)),
            'posture_consensus': str(src['posture_consensus'].relative_to(ROOT)),
            'samples': len(ms), 'models': len(set(r['model'] for r in ms)), 'cells': len(set(r['cell'] for r in ms)),
        })
    write_jsonl(DATA/'manifest_valid.jsonl', manifest)
    write_jsonl(DATA/'manifest_invalid_traces.jsonl', invalid)
    write_jsonl(DATA/'layer_a_consensus.jsonl', layer_a_cons)
    write_jsonl(DATA/'posture_consensus.jsonl', posture_cons)
    for c in CODERS:
        write_jsonl(DATA/f'layer_a_coder_{c}.jsonl', layer_a_raw[c])
        write_jsonl(DATA/f'posture_coder_{c}.jsonl', posture_raw[c])
    write_jsonl(DATA/'source_map.jsonl', source_rows)

    # Summary tables.
    by_model=collections.defaultdict(list)
    samples_by_model=collections.defaultdict(list)
    layer_a_by={r['layered_id']: r for r in layer_a_cons}
    for r in posture_cons: by_model[r['model']].append(r)
    for s in manifest: samples_by_model[s['model']].append(s)
    model_summary_rows=[]
    for model in sorted(samples_by_model):
        rows=by_model[model]
        samples=samples_by_model[model]
        report_for_model(model, samples, layer_a_by, rows)
        model_summary_rows.append({
            'model': model,
            'samples': len(samples),
            'cells': len(set(s['cell'] for s in samples)),
            'one_line_summary': model_summary(model, rows),
            'posture_counts': dict(collections.Counter(r['collapsed_primary_label'] for r in rows)),
            'value_holding_counts': dict(collections.Counter(r['value_holding'] for r in rows)),
            'report': f'reports/{model}.md',
        })
    write_jsonl(DATA/'model_summary.jsonl', model_summary_rows)

    # QA markdown.
    lines=['# Final values-probe data QA','', f'- valid samples: {len(manifest)}', f'- invalid/error traces excluded: {len(invalid)}', f'- models: {len(samples_by_model)}', f'- cells: {len(set(r["cell"] for r in manifest))}', '']
    lines += ['## Source components','']
    for r in source_rows:
        lines.append(f"- {r['source']}: {r['samples']} samples, {r['models']} model(s), {r['cells']} cell(s)")
    lines += ['', '## Overall collapsed posture distribution','']
    for k,n in collections.Counter(r['collapsed_primary_label'] for r in posture_cons).most_common():
        lines.append(f'- `{k}`: {n} ({pct(n,len(posture_cons))})')
    lines += ['', '## Overall value-holding distribution','']
    for k,n in collections.Counter(r['value_holding'] for r in posture_cons).most_common():
        lines.append(f'- `{k}`: {n} ({pct(n,len(posture_cons))})')
    (DATA/'QA.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
