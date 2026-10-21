from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, os, re, shutil, subprocess, time

def safe(s):
    for k in ('KAGGLE_API_TOKEN', 'KAGGLE_KEY'):
        if os.environ.get(k): s = s.replace(os.environ[k], '[REDACTED]')
    return re.sub(r'(Authorization\s*[:=]\s*)[^\n]+', r'\1[REDACTED]', s, flags=re.I)[:3000]

out = {'observed_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
       'session': 356010973, 'tools': {k: shutil.which(k) for k in ('kaggle','clang++-17','g++','make')},
       'cpu': os.cpu_count(), 'affinity': sorted(os.sched_getaffinity(0)),
       'free': {p: shutil.disk_usage(p).free for p in ('/root','/kaggle/working')}}
out['processes'] = subprocess.check_output(['ps','-eo','pid,ppid,etime,time,%cpu,%mem,comm','--sort=-%cpu'], text=True).splitlines()[:20]
out['records'] = {}
for root in ('/kaggle/working/hp_round11','/kaggle/working/hp_round12_claude'):
    p = Path(root)
    out['records'][root] = [{'path':str(x), 'size': x.stat().st_size} for x in p.rglob('*') if x.is_file() and (x.name in ('manifest.json','cleanup_verified.py','cleanup_ledger.json') or x.suffix in ('.cpp','.h','.py'))][:140] if p.exists() else []
out['manifests'] = {}
for p in Path('/kaggle/working/hp_round11').glob('*/manifest.json'):
    try: out['manifests'][str(p)] = json.loads(p.read_text())
    except Exception as e: out['manifests'][str(p)] = str(e)
refs = ['chaoscpp/hutter-r12-warm-stream-'+x for x in ('a','b','c')]
refs += ['chaoscpp/hutter-r10-cpu-'+x for x in ('bf16-cut107-half','bf16-cut1392-zero','bf16-unweighted','component-ppmd')]
def status(ref):
    r = subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=20)
    return {'ref':ref, 'exit':r.returncode, 'stdout':safe(r.stdout),'stderr':safe(r.stderr)}
with ThreadPoolExecutor(max_workers=4) as pool: out['notebooks'] = list(pool.map(status, refs))
print(json.dumps(out))
