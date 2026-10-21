import pathlib,subprocess,os,time,json
import numpy as np
hp=pathlib.Path('/root/hp');out=pathlib.Path('/kaggle/working/hp_round7')
for _ in range(480):
    if 'CALIBRATION_SCREENS_COMPLETE' in (out/'trace_controller.log').read_text():break
    time.sleep(5)
else:raise RuntimeError('Trace experiments did not finish')
results=[]
for mode in [0,1]:
    jobs=[]
    for name in ['c','d']:
        run=out/f'sx_control_{mode}_{name}';run.mkdir(exist_ok=False)
        (run/'.dict').symlink_to(hp/'gen/.dict')
        env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(hp/'data/vocab.bm'),'LAB_DICT':str(hp/'gen/.dict'),'LAB_COST':str(run/'cost.f32'),'LAB_KEEP_PPMD':'1','LAB_SX':str(mode)}
        for key in ['LAB_FINALMIX','LAB_UNIFORM_NN']:env.pop(key,None)
        cmd=[str(hp/'round7_sx_control/cmix'),'-n','--transformer',str(hp/'gen/.tfweights'),'--load-transformer-probs',str(hp/f'slices/{name}2m.probs.f16'),str(hp/f'slices/{name}2m.bin'),'out.cmx']
        log=(run/'run.log').open('w');p=subprocess.Popen(cmd,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
        jobs.append((name,p,log));print(json.dumps({'sx_control_started':name,'mode':mode,'pid':p.pid}),flush=True)
    for name,p,log in jobs:
        rc=p.wait();log.close()
        if rc:raise RuntimeError('Topology control failed')
        run=out/f'sx_control_{mode}_{name}'
        costs=np.fromfile(run/'cost.f32','<f4').astype(np.float64)
        base=np.fromfile(out/f'baseline_{name}/cost.f32','<f4').astype(np.float64)
        if len(costs)!=len(base):raise RuntimeError('Incomplete topology cost')
        row={'slice':name,'expert_enabled':bool(mode),'native_bytes':(run/'out.cmx').stat().st_size,'baseline_native_bytes':(out/f'baseline_{name}/out.cmx').stat().st_size,'saving_native_bytes':(out/f'baseline_{name}/out.cmx').stat().st_size-(run/'out.cmx').stat().st_size,'saving_ideal_bytes':float((base-costs).sum()/8.),'baseline_ideal_bytes':float(base.sum()/8.)}
        results.append(row);(out/'sx_topology_controls.json').write_text(json.dumps(results,indent=2))
        print(json.dumps(row),flush=True)
print('SX_TOPOLOGY_CONTROLS_COMPLETE',flush=True)
