"""Compact immutable evidence bundle. Never includes a signed session URL."""
import pathlib,json,os,time,zipfile,hashlib,traceback
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'compact_preservation_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9');m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'deletions':[],'entries':[]}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
try:
 files={};exe_suffixes=['.py','.cpp','.h','.md','.json','.log','.zip']
 for p in R.rglob('*'):
  rel=p.relative_to(R)
  if p.is_file() and not p.is_symlink() and 'preservation_links' not in rel.parts and 'compact_preservation_v1' not in rel.parts and p.suffix in exe_suffixes and p.stat().st_size<4_000_000:files['metadata_and_source/'+str(rel)]=p
 for name in ['causal_sequence_v1','hidden_sequence_v2']:
  for p in (R/name).glob('*.pt'):files['models/'+name+'/'+p.name]=p
 for name in ['adaptive_native_v1','adaptive_native_v2']:
  root=S/name
  if not root.exists():continue
  for sub in ['g_teacher','g_candidate','h_teacher','h_candidate']:
   for filename in ['input.bin','out.cmx','final_p.u16']:
    p=root/sub/filename
    if p.is_file():files['native/'+name+'/'+sub+'/'+filename]=p
 for sub in ['src','cpp_infer']:
  for p in (S/'adaptive_native_v1/tree'/sub).rglob('*'):
   if p.is_file() and p.suffix in ['.cpp','.h','.hpp'] and p.stat().st_size<3_000_000:files['native_sources/'+sub+'/'+str(p.relative_to(S/'adaptive_native_v1/tree'/sub))]=p
 for filename in ['cmix','dictionary/english.dic','Makefile']:
  p=S/'adaptive_native_v1/tree'/filename
  if p.is_file():files['native_sources/'+filename]=p
 for filename in ['events.tsv','sample.txt','windows.txt','word_events']:
  p=S/'word_events_v1'/filename
  if p.is_file():files['word_events/'+filename]=p
 archive=R/'round9_compact_evidence_v1.zip';save('bundling completed models, native source/binary and compact paired evidence')
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for rel,p in files.items():
   # Freeze a single byte snapshot. Running manifests may change between an
   # independent hash/read pair; source and manifest bytes in this bundle
   # must describe precisely the content actually written.
   frozen=p.read_bytes();digest=hashlib.sha256(frozen).hexdigest();z.writestr(rel,frozen);m['entries'].append({'file':rel,'bytes':len(frozen),'sha256':digest})
  z.writestr('bundle_entry_manifest.json',json.dumps(m['entries'],indent=2))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 m.update(status='COMPLETE_COMPACT_EVIDENCE_BUNDLE',finished=time.time(),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),archive=str(archive),scope='snapshot of files complete at creation; running core/word checkpoints are preserved separately through verified links');save('ZIP CRC and SHA verification complete')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
