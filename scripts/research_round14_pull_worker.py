from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,os,subprocess,time,traceback,zipfile
R=Path('/root/hp_round14_pulls');R.mkdir(exist_ok=True)
W=Path('/kaggle/working/hp_round14');W.mkdir(exist_ok=True)
M={'status':'RUNNING','started':time.time(),'pulls':[],'deletions':[]}
def save(): (W/'pull_manifest.json').write_text(json.dumps(M,indent=2))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()
def pull(slug):
    d=R/slug;d.mkdir(exist_ok=False)
    p=subprocess.run(['kaggle','kernels','output','chaoscpp/'+slug,'-p',str(d)],capture_output=True,text=True,timeout=1200)
    msg=p.stdout+p.stderr
    for k in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
        if os.environ.get(k):msg=msg.replace(os.environ[k],'[REDACTED]')
    return {'ref':'chaoscpp/'+slug,'exit':p.returncode,'message':msg[-3500:],'path':str(d),
        'files':[{'path':str(q.relative_to(d)),'bytes':q.stat().st_size,'sha256':sha(q)} for q in d.rglob('*') if q.is_file()]}
try:
    save()
    # Delete only an already preserved redundant aggregate, not a source/model.
    p=Path('/kaggle/working/hp_round13/completed_compact_evidence_v1.zip')
    if p.exists():
        h=sha(p);assert h=='1204ea8c3c9fe64da99c08265b30c51cfc0d4b5888014dd29855fd436eb7c7f6'
        assert p.resolve().parent==Path('/kaggle/working/hp_round13').resolve()
        M['deletions'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':h,
          'reason':'redundant aggregate verified locally and all underlying files retained; working disk had 3.5 MB free',
          'local_preserved_copy':'research_round13_completed_compact_evidence_v1.zip'})
        save();p.unlink()
    slugs=['hutter-r13-warm-development-v1','hutter-r13-warm-confirmation-v1','hutter-r13-native-final-head-v2',
           'hutter-r13-weight-storage-regeneration-v1','hutter-r13-full-corpus-factorization-v1']
    with ThreadPoolExecutor(max_workers=5) as pool:
        for f in as_completed([pool.submit(pull,s) for s in slugs]):M['pulls'].append(f.result());save()
    assert all(r['exit']==0 and r['files'] for r in M['pulls'])
    entries=[];zpath=W/'completed_compact_v1.zip'
    with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in sorted(R.rglob('*')):
            if p.is_file() and (p.suffix in ('.json','.jsonl','.log','.cmx','.txt') or p.name.endswith('_cost.f32.gz')):
                n=str(p.relative_to(R));z.write(p,n);entries.append({'path':n,'bytes':p.stat().st_size,'sha256':sha(p)})
        z.writestr('entries.json',json.dumps(entries,indent=2))
    M.update(status='COMPLETE_PULLED_AND_COMPACTED',finished=time.time(),compact={'path':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha(zpath),'entries':len(entries)})
    save()
except BaseException as e:
    M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
