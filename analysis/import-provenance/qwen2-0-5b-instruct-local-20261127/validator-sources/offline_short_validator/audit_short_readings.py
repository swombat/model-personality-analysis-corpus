"""Counterfactual offline replay; never change a pinned validator or any receipt."""
import ast
import inspect
import re
from replay_v13_candidates import ROOT, module, replay

def short_check():
    path = ROOT.parent/'colab-bv1-v1.3-candidate/analysis/freeflow/personality-eval-bv1/luna_v1_3.py'
    v = module(path)
    bv = v.V1.BV
    src = inspect.getsource(bv.valid_output)
    assert src.count('len(txt.split()) < 120') == 1
    scope = dict(vars(bv))
    exec(compile(ast.parse(src.replace('len(txt.split()) < 120','len(txt.split()) < 30')), '<short-audit>', 'exec'), scope)
    floor120 = bv.valid_output
    def check(text,source,used,allowance):
        # Cap characters too: whitespace count isn't length for unspaced scripts.
        short = 0 < len(source.split()) < 50 and len(source) <= 300
        bv.valid_output = scope['valid_output'] if short else floor120
        ok, why = v.valid_output(text,source)
        if ok and short:
            chunks = re.split(r'^## .+\n', text, flags=re.M)[1:]
            if not all(ch.strip() for ch in chunks): return 'empty_section'
        return 'pass_short' if ok and short else 'sentence' if ok else why
    return check

if __name__ == '__main__':
    import json
    for r in replay(short_check()): print(json.dumps(r))
