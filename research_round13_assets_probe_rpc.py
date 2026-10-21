from pathlib import Path
import importlib.util,json,os,subprocess
W=Path('/kaggle/working')
paths=[W/'hp_round7/preserved/data/enwik9.zip',W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt',Path('/root/r12_assets'),Path('/root/r12_assets_c')]
out={'paths':{str(p):{'exists':p.exists(),'bytes':p.stat().st_size if p.is_file() else None} for p in paths},
     'modules':{m:importlib.util.find_spec(m) is not None for m in ('pyppmd','zstandard','torch','numpy')},
     'topology':{i:Path(f'/sys/devices/system/cpu/cpu{i}/topology/thread_siblings_list').read_text().strip() for i in os.sched_getaffinity(0)},
     'census':json.loads((W/'hp_round11/word_coverage_v1/manifest.json').read_text())}
r=subprocess.run(['kaggle','kernels','list','--mine','--csv'],capture_output=True,text=True,timeout=20)
out['owner_inventory']=r.stdout[:9000]
print(json.dumps(out))
