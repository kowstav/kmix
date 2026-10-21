"""Bounded-size downloadable parts for a potentially large recovery ZIP."""
import pathlib,json,time,os,hashlib,traceback
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'compact_download_parts_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/compact_download_parts_v2');S.mkdir(exist_ok=False);m={'status':'WAITING_FOR_EXTENDED_ZIP','pid':os.getpid(),'started':time.time(),'deletions':[],'parts':[]}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
try:
 start=time.time()
 while True:
  p=R/'compact_preservation_v2/manifest.json';j=json.loads(p.read_text())
  if j['status'].startswith('COMPLETE'):break
  if j['status']=='FAIL':raise RuntimeError(j['error'])
  assert time.time()-start<18000;time.sleep(30)
 source=pathlib.Path('/kaggle/working')/j['download_path'];m.update(source_bytes=j['archive_bytes'],source_sha256=j['archive_sha256']);L=R/'preservation_links/artifacts';L.mkdir(parents=True,exist_ok=True);whole=hashlib.sha256();total=0;save('splitting immutable verified ZIP into120MB download parts')
 with source.open('rb') as f:
  index=0
  while True:
   chunk=f.read(120_000_000)
   if not chunk:break
   part=S/(source.name+'.part'+str(index).zfill(3));part.write_bytes(chunk);digest=hashlib.sha256(chunk).hexdigest();link=L/part.name;assert not link.exists();link.symlink_to(part);m['parts'].append({'filename':part.name,'remote_path':str(link.relative_to('/kaggle/working')),'bytes':len(chunk),'sha256':digest});whole.update(chunk);total+=len(chunk);index+=1
 assert total==j['archive_bytes'] and whole.hexdigest()==j['archive_sha256'];m.update(status='COMPLETE_VERIFIED_EXTENDED_ZIP_DOWNLOAD_PARTS',finished=time.time());save('part hashes and concatenated ZIP SHA PASS')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
