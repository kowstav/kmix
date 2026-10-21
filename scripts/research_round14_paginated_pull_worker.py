from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,time,traceback,zipfile,requests,subprocess
from kaggle.api.kaggle_api_extended import KaggleApi,ApiListKernelSessionOutputRequest
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_batch_outputs')
M={'status':'PAGINATED_RECOVERY','started':time.time(),'jobs':[],'deletions':[]}
def save():(W/'paginated_collection_v2.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def recover(role):
    slug='hutter-r14-constructor-'+role+'-v1';d=R/slug;api=KaggleApi();api.authenticate();token=None;pages=0;seen=set();todo=[]
    with api.build_kaggle_client() as client:
        while True:
            req=ApiListKernelSessionOutputRequest();req.user_name='chaoscpp';req.kernel_slug=slug;req.page_size=500;req.page_token=token
            resp=client.kernels.kernels_api_client.list_kernel_session_output(req);pages+=1
            for item in resp.files or []:
                n=item.file_name;assert n not in seen;seen.add(n);p=(d/n).resolve();assert p.is_relative_to(d.resolve())
                if not p.exists():todo.append((item.url,p))
            nxt=resp.next_page_token
            if not nxt:break
            assert nxt!=token;token=nxt
    def download(pair):
        url,p=pair;r=requests.get(url,timeout=90);r.raise_for_status();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(r.content)
        return {'path':str(p.relative_to(d)),'bytes':p.stat().st_size,'sha256':sha(p)}
    with ThreadPoolExecutor(8) as pool:downloaded=list(pool.map(download,todo))
    paths=list(d.rglob('manifest.json'));assert len(paths)==1
    return {'slug':slug,'pages':pages,'listed_files':len(seen),'new_files':downloaded,'manifest_path':str(paths[0]),'manifest_sha256':sha(paths[0])}
try:
    assert not (W/'paginated_collection_v2.json').exists();save()
    for role in ('development','confirmation'):M['jobs'].append(recover(role));save()
    entries=[];p=W/'paginated_constructor_supplement_v2.zip'
    with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for r in M['jobs']:
            for e in r['new_files']:
                f=R/r['slug']/e['path'];n=r['slug']+'/'+e['path'];z.write(f,n);entries.append(dict(e,path=n))
        z.writestr('entries.json',json.dumps(entries,indent=2))
    M.update(status='COMPLETE_ALL_PAGES',finished=time.time(),compact={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'entries':len(entries)});save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
