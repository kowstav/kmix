import pathlib,subprocess,os,time,json
import numpy as np
out=pathlib.Path('/kaggle/working/hp_round7')
hp=pathlib.Path('/root/hp')
subprocess.run(['clang++-17','-O3','-std=c++17',str(out/'research_round7_calibration_screen.cpp'),'-o',str(out/'calibration_screen')],check=True)
# Avoid multiplying the baseline's memory and disk footprints while it runs.
for _ in range(240):
    if 'CONFIRMATION_BASELINES_COMPLETE' in (out/'confirmation_controller.log').read_text():break
    time.sleep(5)
else:raise RuntimeError('Confirmation baselines did not finish')
jobs=[]
for name in ['a','b']:
    run=out/('trace_'+name);run.mkdir(exist_ok=False)
    (run/'.dict').symlink_to(hp/'gen/.dict')
    env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(hp/'data/vocab.bm'),'LAB_DICT':str(hp/'gen/.dict'),'LAB_COST':str(run/'cost.f32'),'LAB_KEEP_PPMD':'1','LAB_BITTRACE':str(run/'final_p.u16')}
    for key in ['LAB_FINALMIX','LAB_SX','LAB_UNIFORM_NN']:env.pop(key,None)
    cmd=[str(hp/'round7_trace/cmix'),'-n','--transformer',str(hp/'gen/.tfweights'),'--load-transformer-probs',str(hp/f'slices/{name}2m.probs.f16'),str(hp/f'slices/{name}2m.bin'),'out.cmx']
    log=(run/'run.log').open('w')
    p=subprocess.Popen(cmd,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
    jobs.append((name,p,log));print(json.dumps({'trace_started':name,'pid':p.pid}),flush=True)
for name,p,log in jobs:
    rc=p.wait();log.close()
    if rc:raise RuntimeError('Trace compressor failed: '+name)
    run=out/('trace_'+name)
    cost=np.fromfile(run/'cost.f32','<f4').astype(np.float64)
    old=np.fromfile(hp/f'runs/lex_{name}/cost.f32','<f4').astype(np.float64)
    if len(cost)!=len(old):raise RuntimeError('Trace cost alignment failure')
    trace=np.fromfile(run/'final_p.u16','<u2')/65536.
    raw=np.fromfile(hp/f'slices/{name}2m.bin','u1')
    bits=np.unpackbits(raw)
    if len(trace)!=len(bits):raise RuntimeError('Bit trace alignment failure')
    audit={'native_bytes':(run/'out.cmx').stat().st_size,'old_cost_difference_ideal_bytes':float((cost-old).sum()/8.),'old_cost_max_abs_difference_bits':float(np.max(np.abs(cost-old))),'trace_cost_vs_dump_bits':float(np.sum(-np.log2(np.where(bits,trace,1-trace)))-cost.sum())}
    (out/(name+'_trace_audit.json')).write_text(json.dumps(audit,indent=2))
    print(json.dumps({'trace_finished':name,'audit':audit}),flush=True)
    subprocess.run([str(out/'calibration_screen'),str(hp/f'slices/{name}2m.bin'),str(run/'final_p.u16'),str(out/(name+'_calibration_screen.json'))],check=True)
print('CALIBRATION_SCREENS_COMPLETE',flush=True)
