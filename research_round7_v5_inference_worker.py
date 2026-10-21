import pathlib,subprocess,os,json,hashlib,time
hp=pathlib.Path('/root/hp');out=pathlib.Path('/kaggle/working/hp_round7')
for _ in range(300):
    if 'V5_NATIVE_COMPLETE' in (out/'v5_native_retry.log').read_text():break
    time.sleep(1)
else:raise RuntimeError('Native codec verification timeout')
raw=(hp/'slices/a2m.bin').read_bytes()[:8192];inp=out/'v5_inference_input.bin';inp.write_bytes(raw)
jobs=[]
for name,root,weights in [('old',hp/'round7_lab',hp/'cand_final2/run/comp_tfweights'),('v5',hp/'round7_v5',out/'candidate_bf16.fx2tfwc5')]:
    run=hp/('v5_inference_'+name);run.mkdir(exist_ok=False);(run/'.dict').symlink_to(hp/'gen/.dict')
    env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(hp/'data/vocab.bm'),'LAB_DICT':str(hp/'gen/.dict'),'LAB_KEEP_PPMD':'1'}
    for key in ['LAB_COST','LAB_FINAL_P','LAB_FINALMIX','LAB_UNIFORM_NN','LAB_SX']:env.pop(key,None)
    cmd=[str(root/'cmix'),'-n','--transformer',str(weights),'--save-transformer-probs','actual_native_nn.f16',str(inp),'out.cmx']
    log=(out/('v5_inference_'+name+'.log')).open('w');started=time.monotonic();p=subprocess.Popen(cmd,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
    jobs.append((name,p,log,run,started));print(json.dumps({'inference_started':name,'pid':p.pid}),flush=True)
rows=[]
for name,p,log,run,started in jobs:
    rc=p.wait();log.close()
    if rc:raise RuntimeError('Native inference failed: '+name)
    rows.append({'name':name,'archive_bytes':(run/'out.cmx').stat().st_size,'archive_sha256':hashlib.sha256((run/'out.cmx').read_bytes()).hexdigest(),'neural_distribution_bytes':(run/'actual_native_nn.f16').stat().st_size,'neural_distribution_sha256':hashlib.sha256((run/'actual_native_nn.f16').read_bytes()).hexdigest(),'wall_seconds':time.monotonic()-started})
if rows[0]['archive_sha256']!=rows[1]['archive_sha256'] or rows[0]['neural_distribution_sha256']!=rows[1]['neural_distribution_sha256']:raise RuntimeError('Codec changed native probability stream or archive')
result={'input_bytes':len(raw),'input_sha256':hashlib.sha256(raw).hexdigest(),'measurement':'native C++ neural inference, cold WRT prefix, candidate BF16 weights; no replayed GPU probabilities','neural_distributions_identical':True,'native_archives_identical':True,'rows':rows}
(out/'v5_native_inference.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
print('V5_NATIVE_INFERENCE_COMPLETE',flush=True)
