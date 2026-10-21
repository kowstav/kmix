"""Recoverable later source/native/model evidence, on ample root scratch.

Wait for the explicitly launched jobs to finish or fail; never relaunch them.
Each metadata byte snapshot is frozen once before hashing/writing. A working
symlink exposes the archive without duplicating it onto the nearly full disk.
"""
import pathlib,json,time,os,zipfile,hashlib,traceback
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'compact_preservation_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9');DEST=S/'compact_preservation_v2';DEST.mkdir(exist_ok=False)
m={'status':'WAITING_FOR_LAUNCHED_EXPERIMENTS','pid':os.getpid(),'started':time.time(),'deletions':[],'entries':[],'waiting_jobs':['core_native_codec_v3','core_distributed_v2','word_warmstart_v1','core_pipeline_profile_v1']}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
try:
 last=None;start=time.time()
 while True:
  states={}
  for name in m['waiting_jobs']:
   p=R/name/'manifest.json'
   if p.exists():
    try:states[name]=json.loads(p.read_text())['status']
    except json.JSONDecodeError:states[name]='MANIFEST_WRITE_IN_PROGRESS'
   else:states[name]='NOT_YET_CREATED'
  if states!=last:m['job_states']=states;save('waiting for completed/failed evidence; processes reused');last=states
  if all(v.startswith('COMPLETE') or v=='FAIL' for v in states.values()):break
  assert time.time()-start<14400,'explicit experiment jobs have not finished after4hours';time.sleep(30)
 files={}
 for p in R.rglob('*'):
  rel=p.relative_to(R)
  if not p.is_file() or p.is_symlink() or any(v.startswith('compact_preservation') or v=='preservation_links' for v in rel.parts):continue
  if p.suffix in ['.py','.cpp','.h','.hpp','.md','.json','.log'] and p.stat().st_size<10_000_000:files['metadata_and_source/'+str(rel)]=p
 # These new model checkpoints were not in compact bundle1.
 for name in ['word_softmax_v1','word_softmax_v2','word_warmstart_v1','core_distributed_v2']:
  j=json.loads((R/name/'manifest.json').read_text())
  for row in j.get('rungs',[])+j.get('word_rungs',[]):
   p=pathlib.Path(row['checkpoint_path']);assert sha(p)==row['checkpoint_sha256'];files['models/'+name+'/'+p.name]=p
 for p in (S/'core_export_v2').glob('*.tfwc2'):files['native_models/'+p.name]=p
 for name in ['core_native_codec_v3','known_literals_v1','literal_split_v1']:
  root=S/name
  for p in root.rglob('*'):
   if not p.is_file() or p.is_symlink() or p.stat().st_size>15_000_000:continue
   rel=p.relative_to(root)
   if p.name in ['input.bin','out.cmx','decoded.bin','cmix','Makefile','english.dic','mask.u8','values.u8'] or p.suffix in ['.hpknown','.hpmsk','.z','.cpp','.h','.hpp']:files['native/'+name+'/'+str(rel)]=p
 for filename in ['input.bin','tokens.u8','priors.f16','native_nn.f16','word_frequency.i32','bounds.i32']:
  p=S/'core_data_v2'/filename
  if p.is_file():files['core_data_v2/'+filename]=p
 for name in ['neutral',*[(s+'_'+mode) for s in 'abcdef' for mode in ['raw','redacted1392']]]:
  root=S/'distributed_core_data_v1'/name
  for filename in ['input.bin','tokens.u8','word_frequency.i32','bounds.i32']:
   p=root/filename
   if p.is_file():files['distributed_data/'+name+'/'+filename]=p
 # Dense distributed priors can be regenerated with the native extraction gate;
 # exact SHA and source inputs are preserved, not silently asserted included.
 p=S/'core_layer_probe_v1/layers.bin'
 if p.is_file():files['native_layer_probe/layers.bin']=p
 archive=DEST/'round9_extended_evidence_v2.zip';m['status']='RUNNING_BUNDLE';save('bundling later immutable checkpoints, native codec artifacts, layer evidence and source')
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for rel,p in files.items():
   frozen=p.read_bytes();digest=hashlib.sha256(frozen).hexdigest();z.writestr(rel,frozen);m['entries'].append({'file':rel,'bytes':len(frozen),'sha256':digest})
  z.writestr('bundle_entry_manifest.json',json.dumps(m['entries'],indent=2))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 L=R/'preservation_links/artifacts';L.mkdir(parents=True,exist_ok=True);link=L/archive.name;assert not link.exists();link.symlink_to(archive)
 m.update(status='COMPLETE_EXTENDED_SOURCE_MODEL_NATIVE_EVIDENCE_BUNDLE',finished=time.time(),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),download_path=str(link.relative_to('/kaggle/working')),snapshot_limits='dense distributed priors omitted but input/bounds/frequency/SHA/neutral gate and exact regeneration worker preserved; metadata snapshots describe terminal jobs; final local download verification still required');save('ZIP CRC/SHA passed, working link uses no duplicate bytes')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
