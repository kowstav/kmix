from pathlib import Path
import json,os,shutil,subprocess,time
W=Path('/kaggle/working/hp_round14')
out={'session':356740330,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'tools':{n:shutil.which(n) for n in ('kaggle','clang++-17','ld.lld-17','g++','7z')},'working_free':shutil.disk_usage('/kaggle/working').free,'manifests':{}}
for name in ('native_dispatch_v3.json','order_native_submission_v4.json','native_cpu_preflight_v1/manifest.json','ppmd_native_probe_v3.json'):
    p=W/name
    if p.exists():out['manifests'][name]=json.loads(p.read_text()).get('status')
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,comm','--sort=-%cpu'],text=True).splitlines()[:10]
print(json.dumps(out))
