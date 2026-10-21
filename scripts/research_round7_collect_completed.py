import hashlib,json,pathlib,zipfile
r=pathlib.Path('/kaggle/working/hp_round7');out=r/'completed_20261005T1912.zip';assert not out.exists()
dirs=['remaining_experts_v1','root_eof_v3','numeric_programs_v2','macro_packets_v1','tiny_residual_v1','full_stream_regen_v2','full_inverse_v2','exact_prior_storage_v1','exact_prior_transforms_v1']
sources=['research_round7_calibration_native_v2_worker.py','research_round7_calibration_native_v3_worker.py','research_round7_calibration_native_v4_worker.py','research_round7_full_inverse_v2_worker.py','research_round7_word_root_causal_v3.py']
index=[]
with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n in dirs:
  d=r/n;m=json.loads((d/'manifest.json').read_text());assert m['status'] not in ['RUNNING','FAIL'],(n,m['status'])
  for p in sorted(d.glob('*')):
   if p.is_file() and p.suffix in ['.json','.u32','.txt'] and p.stat().st_size<3000000:
    b=p.read_bytes();name=str(p.relative_to(r));z.writestr(name,b);index.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  log=r/(n+'_controller.log')
  if log.is_file():z.writestr(n+'/controller_tail.txt',log.read_text()[-4000:])
 for s in sources:
  p=r/s;assert p.is_file();b=p.read_bytes();z.writestr('sources/'+s,b);index.append({'path':'sources/'+s,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 for n in ['calibration_native_v1','calibration_native_v2','calibration_native_v3','full_inverse_v1','full_stream_regen_v1','numeric_programs_v1']:
  p=r/n/'manifest.json'
  if p.is_file():z.writestr('failed/'+n+'_manifest.json',p.read_bytes())
 z.writestr('index.json',json.dumps(index,indent=2))
print(json.dumps({'archive':out.name,'bytes':out.stat().st_size,'files':len(index),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
