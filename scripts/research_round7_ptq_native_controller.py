import pathlib,subprocess,os,json,time,hashlib
import numpy as np
out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'ptq_round7';pre=out/'preserved';hp=pathlib.Path('/root/hp/ptq_round7')
hp.mkdir(parents=True,exist_ok=False);binary=out/'cmix_round7_v5';binary.chmod(0o755)
for _ in range(720):
    if all((out/(n+'_word_newmention_v1_screen.json')).exists() for n in 'abcd'):break
    log=out/'word_newmention_controller.log'
    if log.exists() and 'Traceback' in log.read_text():raise RuntimeError('New-mention controller failed')
    for n in 'abcd':
        log=out/(n+'_word_newmention_v1.log')
        if log.exists() and 'Traceback' in log.read_text():raise RuntimeError('New-mention screen failed: '+n)
    time.sleep(5)
else:raise RuntimeError('Waiting screens did not finish')
baselines={};results=[]
for model in ['baseline','mlp_down_unit0','mlp_unit0','all_unit2_zero']:
    if model!='baseline':
        for _ in range(720):
            p=dest/'codec_results.json'
            if p.exists() and any(r['name']==model for r in json.loads(p.read_text())):break
            if 'Traceback' in (out/'ptq_codec.log').read_text():raise RuntimeError('PTQ export failed')
            time.sleep(2)
        else:raise RuntimeError('PTQ export timeout')
    weights=out/'candidate_bf16.fx2tfwc5' if model=='baseline' else dest/(model+'.fx2tfwc5')
    jobs=[]
    for n in 'ab':
        raw=(pre/f'slices/{n}2m.bin').read_bytes()[:32768];inp=hp/(n+'_input.bin');inp.write_bytes(raw)
        run=hp/(model+'_'+n);run.mkdir(exist_ok=False);(run/'.dict').symlink_to(pre/'gen/.dict')
        env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(pre/'data/vocab.bm'),'LAB_DICT':str(pre/'gen/.dict'),'LAB_KEEP_PPMD':'1','LAB_COST':str(run/'cost.f32')}
        for key in ['LAB_FINAL_P','LAB_FINALMIX','LAB_UNIFORM_NN','LAB_SX']:env.pop(key,None)
        log=(dest/(model+'_'+n+'.log')).open('w');started=time.monotonic()
        p=subprocess.Popen([str(binary),'-n','--transformer',str(weights),str(inp),'out.cmx'],cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
        jobs.append((n,p,log,run,started));print(json.dumps({'started_native_ptq':model,'slice':n,'pid':p.pid}),flush=True)
    for n,p,log,run,started in jobs:
        rc=p.wait();log.close()
        if rc:raise RuntimeError('Native PTQ failed '+model+' '+n)
        costs=np.fromfile(run/'cost.f32','<f4').astype(np.float64)
        if len(costs)!=32768:raise RuntimeError('Incomplete native costs')
        ideal=float(costs.sum()/8.)
        if model=='baseline':baselines[n]=ideal
        row={'model':model,'slice':n,'input_bytes':32768,'native_archive_bytes':(run/'out.cmx').stat().st_size,'ideal_bytes':ideal,'baseline_ideal_bytes':baselines[n],'delta_ideal_bytes':ideal-baselines[n],'weights_bytes':weights.stat().st_size,'saving_weight_bytes_two_copies':2*((out/'candidate_bf16.fx2tfwc5').stat().st_size-weights.stat().st_size),'wall_seconds':time.monotonic()-started,'measurement':'cold matched native neural inference on a32768-byte prefix; projected extrapolation is not a qualifying score'}
        row['hypothetical_full_stream_net_saving_BYTES_NOT_VALIDATED']=row['saving_weight_bytes_two_copies']-row['delta_ideal_bytes']*586459020/32768
        results.append(row);(dest/'native_results.json').write_text(json.dumps(results,indent=2));print(json.dumps(row),flush=True)
print('PTQ_NATIVE_CONTROLS_COMPLETE',flush=True)
