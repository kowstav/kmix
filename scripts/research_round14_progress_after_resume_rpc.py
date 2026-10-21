from pathlib import Path
import json,subprocess,time
W=Path('/kaggle/working/hp_round14');out={'observed_at':time.time()}
for n in ('batch_collection_v1.json','word_costs_v2/manifest.json'):
    m=json.loads((W/n).read_text());out[n]={k:v for k,v in m.items() if k not in ('shards','pulls')}
    out[n]['shards']=len(m.get('shards',[]));out[n]['pulls']=[{'ref':r['ref'],'exit':r['exit'],'files':len(r['files'])} for r in m.get('pulls',[])]
out['present_manifests']=[str(p) for p in Path('/root/r14_batch_outputs').glob('**/manifest.json')]
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,psr,comm','--sort=-%cpu'],text=True).splitlines()[:14]
p=subprocess.run(['kaggle','kernels','output','--help'],capture_output=True,text=True,timeout=20);out['output_help']=p.stdout[-2500:]
print(json.dumps(out))
