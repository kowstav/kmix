from pathlib import Path
import hashlib,json,os,re,subprocess,time,zipfile

W=Path('/kaggle/working/hp_round13')
W.mkdir(exist_ok=True)
out={'observed':time.time(),'records':{},'sources':{},'pulls':[],'deletions':[]}
for p in Path('/kaggle/working/hp_round12_claude').rglob('manifest.json'):
    out['records'][str(p)]=json.loads(p.read_text())
for p in Path('/kaggle/working/hp_round12_claude/code').glob('*'):
    if p.suffix in ('.py','.cpp','.h'): out['sources'][str(p)]=p.read_text()
for p in Path('/kaggle/working/hp_round12_claude/kernels').glob('*/main.py'):
    out['sources'][str(p)]=p.read_text()
out['cleanup_source']=Path('/kaggle/working/hp_round12_claude/cleanup_verified.py').read_text()
out['scratch_present']={p:Path(p).exists() for p in ['/root/hp_round11/warm_atlas_v2','/root/hp_round11_word_cost_v1','/root/r12_pull','/root/r12_assets','/root/hp_round11_private_assets_v2']}
for slug in ['r12-warm-stream-a','r12-warm-stream-b','r12-warm-stream-c','r10-cpu-bf16-unweighted','r10-cpu-bf16-cut107-half','r10-cpu-bf16-cut1392-zero']:
    ref='chaoscpp/hutter-'+slug
    dest=Path('/root/hp_round13_pulls')/slug
    if dest.exists():
        out['pulls'].append({'ref':ref,'state':'REUSED_EXISTING_PULL','path':str(dest)})
        continue
    dest.mkdir(parents=True)
    r=subprocess.run(['kaggle','kernels','output',ref,'-p',str(dest)],capture_output=True,text=True,timeout=90)
    raw=r.stdout+'\n'+r.stderr
    for key in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
        if os.environ.get(key): raw=raw.replace(os.environ[key],'[REDACTED]')
    out['pulls'].append({'ref':ref,'exit':r.returncode,'output':raw[:1500],'files':[{'name':str(x.relative_to(dest)),'bytes':x.stat().st_size} for x in dest.rglob('*') if x.is_file()]})
    for p in dest.rglob('manifest.json'): out['records'][str(p)]=json.loads(p.read_text())
    for p in dest.rglob('*.log'):
        if p.stat().st_size<150000:
            out['sources'][str(p)]=p.read_text(errors='replace')[-12000:]
record=W/'audit_external_inventory.json'
record.write_text(json.dumps(out,indent=2))
archive=W/'audit_external_evidence_v1.zip'
assert not archive.exists()
entries=[]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    bases=[Path('/kaggle/working/hp_round12_claude'),Path('/root/hp_round13_pulls')]
    for base in bases:
        for p in sorted(base.rglob('*')):
            if not p.is_file() or p.stat().st_size>10000000: continue
            if p.suffix not in ('.json','.jsonl','.py','.cpp','.h','.log','.cmx','.bin'): continue
            name=('r12' if 'claude' in str(base) else 'pulls')+'/'+str(p.relative_to(base))
            data=p.read_bytes(); z.writestr(name,data)
            entries.append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    z.writestr('entries.json',json.dumps(entries,indent=2))
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
print(json.dumps({'record':str(record),'archive':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'entries':len(entries)}))
