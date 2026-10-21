import hashlib,json,pathlib,zipfile
D=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1');T=D/'tree';out=D/'stage_observer_source_evidence.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not out.exists():
 files=[]
 for folder in ['src','dictionary']:
  files.extend(p for p in (T/folder).rglob('*') if p.is_file() and p.suffix!='.o')
 files.extend(p for p in T.iterdir() if p.is_file() and (p.name.lower() in ['makefile','license'] or p.name.lower().startswith('readme')))
 files=sorted(set(files));assert len(files)>150 and sum(p.stat().st_size for p in files)<20000000
 entries=[{'file':p.relative_to(T).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for p,row in zip(files,entries):z.write(p,row['file'])
  z.writestr('source_evidence_manifest.json',json.dumps({'entries':entries,'scope':'complete observed C3 source/dictionary, no objects or compiler runtime; wider/narrow interfaces preserved separately'},indent=2))
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'no_deletions':True}))
