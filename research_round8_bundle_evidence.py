import datetime,hashlib,json,pathlib,subprocess,zipfile
R=pathlib.Path('/kaggle/working/hp_round8');dst=R/'round8_evidence_20261006_complete.zip'
active=[x for x in subprocess.run(['ps','-eo','pid,args'],capture_output=True,text=True).stdout.splitlines() if 'research_round8_' in x and ('worker.py' in x or '/replay' in x or '/export' in x)]
assert not active,active
files=[];excluded=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or p==dst or '__pycache__' in p.parts:continue
 rel=p.relative_to(R).as_posix()
 keep=p.suffix in {'.py','.cpp','.h','.md','.json','.log','.txt','.marginals'} or p.name in {'replay','export','selected_vectors.npy','semantic_k8.u16'}
 if keep:
  b=p.read_bytes();assert b'jupyter-proxy.kaggle.net' not in b,('credential-like URL in artifact',rel);files.append((p,rel,b))
 else:excluded.append({'file':rel,'bytes':p.stat().st_size,'reason':'bulk source/reproducible feature or probability stream; manifest provenance/hashes retained'})
ledger={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'session':355655943,'scope':'complete bounded round8 research batch; no qualifying compressor/archive','paid_rental_usd':0,'deletions':[],'files':[{'file':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for _,rel,b in files],'excluded_but_preserved_remote':excluded,'active_workers':active}
with zipfile.ZipFile(dst,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for _,rel,b in files:archive.writestr(rel,b)
 archive.writestr('EVIDENCE_MANIFEST.json',json.dumps(ledger,indent=2))
result={'zip_path':str(dst),'zip_bytes':dst.stat().st_size,'zip_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'files':len(files),'bulk_files_preserved_remote':len(excluded),'all_jobs_complete':True}
(R/'round8_evidence_bundle_manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
