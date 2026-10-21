import json,subprocess,pathlib
d={}
for name,args in [('gpu',['nvidia-smi','--query-gpu=name,memory.total,driver_version,compute_cap','--format=csv,noheader']),('disk',['df','-B1','/kaggle/working','/root'])]:
 p=subprocess.run(args,capture_output=True,text=True);d[name]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
try:
 import torch
 d['torch']={'version':torch.__version__,'cuda':torch.version.cuda,'available':torch.cuda.is_available(),'devices':[{'name':torch.cuda.get_device_name(i),'capability':torch.cuda.get_device_capability(i)} for i in range(torch.cuda.device_count())],'bf16_supported':torch.cuda.is_bf16_supported() if torch.cuda.is_available() else None}
except Exception as e:d['torch_error']=repr(e)
print(json.dumps(d))
