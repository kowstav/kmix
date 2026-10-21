from pathlib import Path
import hashlib,json,subprocess,shutil,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_native_cpu_asset_v1');M={'status':'CHECKING_NATIVE_GATE','started':time.time(),'deletions':[],'dataset':'chaoscpp/hutter-r14-native-cpu-assets-v1'}
def save():(W/'native_cpu_asset_v1.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    assert not R.exists() and not (W/'native_cpu_asset_v1.json').exists();R.mkdir();save()
    p=W/'native_cpu_preflight_v1/manifest.json';gate=json.loads(p.read_text());assert gate['status']=='PASS_NEUTRAL_PARITY_AND_SIX_EXACT_INVERSES'
    build=json.loads((W/'native_cpu_build_v2.json').read_text());assert len(build['builds'])==5
    for r in build['builds']:
        p=W/'native_cpu_binaries_v2'/('cmix_'+r['name']);assert sha(p)==r['sha256'];shutil.copyfile(p,R/p.name)
    shutil.copyfile(W/'native_cpu_sources_v2.zip',R/'native_cpu_sources_v2.zip.dat');shutil.copyfile(W/'native_cpu_build_v2.json',R/'build_manifest.json');shutil.copyfile(W/'native_cpu_preflight_v1/manifest.json',R/'preflight_manifest.json')
    files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in R.iterdir() if p.is_file()}
    (R/'r14_native_cpu_assets.json').write_text(json.dumps({'files':files,'source_sha256':build['source_sha256'],'native_preflight_status':gate['status']},indent=2))
    (R/'dataset-metadata.json').write_text(json.dumps({'title':'Hutter r14 native CPU assets v1','id':M['dataset'],'licenses':[{'name':'other'}]}))
    M.update(status='UPLOADING_PRIVATE_CPU_ASSETS',files=files);save()
    p=subprocess.run(['kaggle','datasets','create','-p',str(R)],capture_output=True,text=True,timeout=900)
    url='https://www.kaggle.com/datasets/'+M['dataset'];assert p.returncode==0 and url in p.stdout and 'error' not in p.stdout.lower(),'private asset creation unverified; inspect, do not duplicate'
    bundle=W/'native_cpu_preservation_v2.zip'
    with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED) as z:
        entries=[]
        for p in sorted(R.iterdir()):
            if p.is_file():z.write(p,p.name);entries.append({'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
        z.writestr('entries.json',json.dumps(entries,indent=2))
    M.update(status='COMPLETE_PRIVATE_ASSET_CREATED',url=url,finished=time.time(),compact={'path':str(bundle),'bytes':bundle.stat().st_size,'sha256':sha(bundle),'entries':len(entries)});save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_RETRY',error=repr(e),traceback=traceback.format_exc());save();raise
