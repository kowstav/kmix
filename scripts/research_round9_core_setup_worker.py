import os
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['OMP_NUM_THREADS']='2'
import pathlib,subprocess,json,time,traceback,sys,hashlib
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'core_setup_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'start':time.time(),'scope':'recover original core runtime and inspect checkpoint; training and native parity not yet passed','deletions':[],'spending_usd':0}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
try:
 site=pathlib.Path('/root/hp_round9/runtime_site_v1');site.mkdir(exist_ok=False)
 save('installing isolated pinned original-core dependencies')
 p=subprocess.run([sys.executable,'-m','pip','install','--no-deps','--target',str(site),'fla-core==0.5.1','jaxtyping==0.3.11','wadler-lindig==0.1.3'],stdout=(D/'dependency_install.log').open('w'),stderr=subprocess.STDOUT,timeout=240);assert p.returncode==0
 sys.path.insert(0,str(site));repo=pathlib.Path('/root/hp_round9/restored/src/fx2-cmix-transformer-v1');sys.path.insert(0,str(repo))
 import torch
 torch.set_num_threads(2);m['gpu']=torch.cuda.get_device_name(0);m['torch_version']=torch.__version__
 import pysrc.model
 ck=repo/'models/6m-q4-fp32.tch';sd=torch.load(ck,map_location='cpu',weights_only=True)
 m['checkpoint_sha256']=hashlib.sha256(ck.read_bytes()).hexdigest();m['parameters']=[{'name':k,'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in sd.items()]
 m['status']='COMPLETE_ORIGINAL_CORE_RUNTIME_READY';m['finish']=time.time();save('original model imports and checkpoint inspection passed; next worker may now train')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
