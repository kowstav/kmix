from pathlib import Path
import json,shutil,subprocess,zipfile,hashlib
W=Path('/kaggle/working/hp_round14');out={'manifests':{},'root_paths':{}}
for n in ('native_cpu_build_v2.json','native_cpu_build_v1.json','ppmd_real_diagnostic_v1.json','ppmd_repair_probe_v1.json','word_costs_v2/manifest.json','tail_collection_v1.json'):
    p=W/n
    if p.exists():
        m=json.loads(p.read_text());out['manifests'][n]={k:v for k,v in m.items() if k not in ('cases','shards','jobs')}
        out['manifests'][n]['cases_or_shards']=len(m.get('cases',m.get('shards',[])))
for n in ('/root/r14_batch_outputs','/root/r14_native_cpu','/root/r14_ppmd_real','/root/r14_code_v2'):out['root_paths'][n]=Path(n).exists()
out['binaries']=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (W/'native_cpu_binaries_v2').glob('*')]
out['free']={p:shutil.disk_usage(p).free for p in ('/root','/kaggle/working')}
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,comm','--sort=-%cpu'],text=True).splitlines()[:10]
print(json.dumps(out))
