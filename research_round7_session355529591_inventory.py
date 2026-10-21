"""Read-only inventory for the user's requested remaining experiments."""
import datetime,json,pathlib,shutil,subprocess
root=pathlib.Path('/kaggle/working/hp_round7')
r={'session':355529591,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'active':'\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'hp_round7' in x or '/cmix_' in x),
   'disk':{k:dict(zip(('total','used','free'),shutil.disk_usage(k))) for k in ('/kaggle/working','/root')},
   'compiler':{k:shutil.which(k) for k in ('g++','clang++-17','clang++','make','ld.lld-17')},
   'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used','--format=csv,noheader'],text=True),
   'working_top':[p.name for p in pathlib.Path('/kaggle/working').iterdir()],'input_top':[p.name for p in pathlib.Path('/kaggle/input').iterdir()],
   'files':{},'manifests':{},'dataset_candidates':[]}
for name in ['preserved/research_sources_and_candidates.tar.gz','preserved/gen/.dict','cmix_round7_lex_codebook',
             'lex_finalbit_trace_v1/cmix_trace','lex_audit/lex_h1_run11.tfwc2',
             *[f'lex_finalbit_2m_v1/{n}/final_p.u16' for n in 'abcd'],
             'preserved/slices/a2m.bin','preserved/slices/b2m.bin','c2m.bin','d2m.bin']:
    p=root/name;r['files'][name]=p.stat().st_size if p.is_file() else None
for name in ['lex_finalbit_2m_v1','constructor_split_v1','constructor_skeleton_v1','constructor_skeleton_v2']:
    p=root/name/'manifest.json'
    if p.is_file():r['manifests'][name]=json.loads(p.read_text()).get('status')
for base in ['/kaggle/working','/kaggle/input','/root/hp']:
    b=pathlib.Path(base)
    if not b.exists():continue
    for p in b.rglob('*'):
        if p.is_file() and (p.name.lower().startswith(('enwik9','phda','wrt','ppmd')) or p.suffix in ('.wrt','.order','.pt','.pth','.tfwc2')):
            r['dataset_candidates'].append({'path':str(p),'bytes':p.stat().st_size})
print(json.dumps(r,indent=2))
