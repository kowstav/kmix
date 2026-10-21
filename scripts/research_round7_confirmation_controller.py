import pathlib, subprocess, os, time, json, shutil
import numpy as np
out=pathlib.Path('/kaggle/working/hp_round7')
validation=out/'baseline_validation'
validation.mkdir(exist_ok=False)
(validation/'.dict').symlink_to('/root/hp/gen/.dict')
n=200000
(validation/'prefix.bin').write_bytes(pathlib.Path('/root/hp/slices/a2m.bin').read_bytes()[:n])
with open('/root/hp/slices/a2m.probs.f16','rb') as source:
    (validation/'prefix.probs.f16').write_bytes(source.read(n*205*2))
venv={**os.environ,'LAB_RAW':'1','LAB_VOCAB':'/root/hp/data/vocab.bm','LAB_DICT':'/root/hp/gen/.dict','LAB_COST':str(validation/'cost.f32'),'LAB_KEEP_PPMD':'1'}
for key in ['LAB_FINALMIX','LAB_SX','LAB_UNIFORM_NN']:
    venv.pop(key,None)
with (validation/'run.log').open('w') as log:
    rc=subprocess.run(['/root/hp/lexT/cmix','-n','--transformer','/root/hp/gen/.tfweights','--load-transformer-probs',str(validation/'prefix.probs.f16'),str(validation/'prefix.bin'),'out.cmx'],cwd=validation,env=venv,stdout=log,stderr=subprocess.STDOUT).returncode
if rc: raise RuntimeError('Restored baseline validation failed')
old=np.fromfile('/root/hp/runs/lex_a/cost.f32','<f4')[:n].astype(np.float64)
new=np.fromfile(validation/'cost.f32','<f4').astype(np.float64)
if len(new)!=n: raise RuntimeError('Validation cost dump incomplete')
v={'bytes':n,'cost_entries_equal':bool(np.array_equal(new,old)),'difference_ideal_bytes':float((new-old).sum()/8),'max_absolute_cost_difference_bits':float(np.max(np.abs(new-old))),'native_bytes':(validation/'out.cmx').stat().st_size}
(out/'baseline_validation.json').write_text(json.dumps(v,indent=2))
print(json.dumps({'baseline_validation':v}),flush=True)
if abs(v['difference_ideal_bytes'])>4: raise RuntimeError('Restored baseline exceeds comparison tolerance')
jobs=[]
for name in ['c','d']:
    prefix=out/(name+'2m')
    for _ in range(180):
        if (out/(name+'_probs.log')).exists() and 'wrote ' in (out/(name+'_probs.log')).read_text(errors='replace') and pathlib.Path(str(prefix)+'.probs.f16').stat().st_size==820000000:
            break
        time.sleep(10)
    else: raise RuntimeError('Prediction generation did not finish: '+name)
    run=out/('baseline_'+name)
    run.mkdir(exist_ok=False)
    (run/'.dict').symlink_to('/root/hp/gen/.dict')
    env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':'/root/hp/data/vocab.bm','LAB_DICT':'/root/hp/gen/.dict','LAB_COST':str(run/'cost.f32'),'LAB_KEEP_PPMD':'1'}
    for key in ['LAB_FINALMIX','LAB_SX','LAB_UNIFORM_NN']:
        env.pop(key,None)
    cmd=['/root/hp/lexT/cmix','-n','--transformer','/root/hp/gen/.tfweights','--load-transformer-probs',str(prefix)+'.probs.f16',str(prefix)+'.bin','out.cmx']
    log=(run/'run.log').open('w')
    p=subprocess.Popen(cmd,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
    jobs.append((name,p,log))
    print(json.dumps({'baseline_launched':name,'pid':p.pid,'directory':str(run)}),flush=True)
for name,p,log in jobs:
    rc=p.wait(); log.close()
    print(json.dumps({'baseline_complete':name,'returncode':rc,'output_bytes':(out/('baseline_'+name)/'out.cmx').stat().st_size}),flush=True)
    if rc: raise RuntimeError('Baseline failed: '+name)
print('CONFIRMATION_BASELINES_COMPLETE',flush=True)
