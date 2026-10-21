"""Collect terminal jobs with complete pagination; leave running jobs alone."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,time,traceback,zipfile,subprocess,requests
from kaggle.api.kaggle_api_extended import KaggleApi,ApiListKernelSessionOutputRequest
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_native_wave_outputs_v1')
M={'status':'CHECKING_EXISTING_JOBS','started':time.time(),'jobs':[],'deletions':[]}
SLUGS=['hutter-r14-native-'+a+'-v1' for a in ('prune-word','prune-match','prune-indirect','output-fp32')]+['hutter-r14-article-order-native-v2']
def save():(W/'native_wave_collection_v1.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    assert not R.exists() and not (W/'native_wave_collection_v1.json').exists();R.mkdir();save()
    api=KaggleApi();api.authenticate()
    for slug in SLUGS:
        ref='chaoscpp/'+slug;res=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=30)
        state=next((s for s in ('COMPLETE','ERROR','CANCELLED','RUNNING','QUEUED') if 'KernelWorkerStatus.'+s in res.stdout),'UNKNOWN')
        row={'ref':ref,'observed':time.time(),'state':state,'exit':res.returncode,'files':[]};M['jobs'].append(row);save()
        assert res.returncode==0 and state!='UNKNOWN','status not verified; no duplicate launch'
        if state not in ('COMPLETE','ERROR','CANCELLED'):continue
        d=R/slug;d.mkdir();seen=set();todo=[];pages=0;token=None
        with api.build_kaggle_client() as client:
            while True:
                req=ApiListKernelSessionOutputRequest();req.user_name='chaoscpp';req.kernel_slug=slug;req.page_size=500;req.page_token=token
                result=client.kernels.kernels_api_client.list_kernel_session_output(req);pages+=1
                for f in result.files or []:
                    name=f.file_name;assert name not in seen;seen.add(name)
                    p=(d/name).resolve();assert p.is_relative_to(d.resolve())
                    if p.suffix in ('.json','.log','.cmx','.hporder','.txt','.py'):todo.append((f.url,p))
                nxt=result.next_page_token
                if not nxt:break
                assert nxt!=token;token=nxt
        def download(item):
            url,p=item;q=requests.get(url,timeout=120);q.raise_for_status();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(q.content)
            return {'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}
        with ThreadPoolExecutor(4) as pool:row['files']=list(pool.map(download,todo))
        row.update(listed_files=len(seen),pages=pages,omitted_noncompact_files=len(seen)-len(todo))
        manifests=list(d.rglob('manifest.json'));assert len(manifests)==1,(slug,len(manifests))
        row['experiment_status']=json.loads(manifests[0].read_text())['status'];row['manifest_path']=str(manifests[0]);save()
    p=W/'native_wave_compact_v1.zip';entries=[]
    with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for row in M['jobs']:
            for e in row['files']:f=R/e['path'];assert sha(f)==e['sha256'];z.write(f,e['path']);entries.append(e)
        z.writestr('entries.json',json.dumps(entries,indent=2))
    M.update(status='COMPLETE_TERMINAL_JOB_SNAPSHOT',finished=time.time(),compact={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'entries':len(entries)});save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
