from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time,traceback,zipfile
W=Path('/kaggle/working/hp_round13');OUT=W/'additional_dispatch_v1.json';S=Path('/root/hp_round13_additional_assets_v1')
M={'status':'PREPARING_PRIVATE_NATIVE_ASSETS','pid':os.getpid(),'started':time.time(),'jobs':[],
   'dataset':'chaoscpp/hutter-r13-native-final-head-assets-v1','deletions':[],'paid_usd':0,'GPU':False}
def save():OUT.write_text(json.dumps(M,indent=2))
def call(args,timeout):
    r=subprocess.run(['kaggle',*args],capture_output=True,text=True,timeout=timeout)
    return r.returncode,r.stdout,r.stderr
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
try:
    assert not OUT.exists() and not S.exists();S.mkdir();save()
    build=json.loads((W/'native_build_v1.json').read_text());assert build['status']=='COMPLETE_LAB_BINARIES_AWAITING_PARITY_PREFLIGHT'
    for row in build['builds']:
        p=W/'native_binaries_v1'/f"cmix_head_{row['mode']}";assert sha(p)==row['sha256'];shutil.copyfile(p,S/p.name)
    shutil.copyfile(W/'native_integration_sources_v1.zip',S/'native_integration_sources_v1.zip')
    files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in S.iterdir()}
    (S/'r13_native_assets.json').write_text(json.dumps({'files':files,'build':build,
       'mandatory_gate':'four parallel 16 KiB independent native decodes and pinned/neutral equality before regional experiments',
       'prior_live_preflight':'timed out on pinned reference before any candidate; preserved separately'},indent=2))
    (S/'dataset-metadata.json').write_text(json.dumps({'title':'Hutter r13 native final head assets v1','id':M['dataset'],'licenses':[{'name':'other'}]}))
    code,output,error=call(['datasets','create','-p',str(S)],600);url='https://www.kaggle.com/datasets/'+M['dataset']
    assert code==0 and url in output and 'error' not in output.lower(),'dataset creation unverified; no automatic retry'
    M.update(status='WAITING_PRIVATE_NATIVE_ASSET_READY',dataset_url=url,asset_files=files);save()
    ready=False
    for delay in (0,10,20,30,60,60):
        if delay:time.sleep(delay)
        code,text,error=call(['datasets','status',M['dataset']],30);assert code==0
        if re.search(r'\b(ready|complete)\b',text,re.I):ready=True;break
    assert ready,'private dataset not ready; no job submitted'
    batch=Path('/root/hp_round13_additional_kernels_v1');batch.mkdir()
    with zipfile.ZipFile(W/'kernels_v2.zip') as z:
        for name in z.namelist():
            p=(batch/name).resolve();assert p.is_relative_to(batch.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
    sys.path.insert(0,'/root/hp_round13_preflight');from hutter_research.dispatch_contracts import parse_successful_push
    M['status']='SUBMITTING_TWO_FOUR_LANE_CPU_JOBS';save()
    for job in ('weight-storage-regeneration','native-final-head'):
        p=batch/job;meta=json.loads((p/'kernel-metadata.json').read_text());ref=meta['id']
        assert meta['is_private'] and not meta['enable_gpu'] and not meta['enable_tpu'] and not meta['enable_internet']
        code,text,error=call(['kernels','list','--mine','--search',ref.split('/')[1],'--csv'],30);assert code==0 and ref not in text
        code,text,error=call(['kernels','push','-p',str(p)],240)
        row={'requested_ref':ref,'CLI_exit':code,'worker_count':4,'source_sha256':sha(p/'main.py')}
        try:row['verified_push']=parse_successful_push(text,'chaoscpp') if code==0 else None
        except ValueError:row['verified_push']=None
        M['jobs'].append(row);save();assert row['verified_push'],'API rejected/unverified; no quota bypass'
    M.update(status='COMPLETE_TWO_ADDITIONAL_VERIFIED_PUSHES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_AUTOMATIC_RETRY',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
