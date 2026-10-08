import importlib.util,json,glob,sys,os
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
OLD=load('old',sys.argv[1]);NEW=load('new',sys.argv[2])
O='/home/agent/work/mpac/analysis/freeflow/personality-eval-bv1/arms/bv1-luna-v1-20260929/outputs'
TR='/home/agent/work/model-personality-corpus-v2/data/traces_freeflow'
n=0;ch=[];ok_old=ok_new=0
for f in sorted(glob.glob(O+'/*/*.md')):
    label=f.split('/')[-2]; sid=os.path.basename(f)[:-3]
    src=json.load(open(f'{TR}/freeflow_{label}/{sid}.json'))['result']; o=open(f).read()
    a=OLD.valid_output(o,src);b=NEW.valid_output(o,src);n+=1;ok_old+=a[0];ok_new+=b[0]
    if a!=b: ch.append((f,a,b))
print('final outputs:',n,'valid old:',ok_old,'valid new:',ok_new,'changed:',len(ch),ch)
