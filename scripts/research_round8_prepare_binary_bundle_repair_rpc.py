import hashlib,json,pathlib
R=pathlib.Path('/kaggle/working/hp_round8');rows=[]
for name,expected in [('round8_native_extension_20261006_complete.zip','b338507e574640ab2ce64fb564d1e1594eceaf36271b2133eb358a2a745ba713'),('round8_evidence_20261006_complete.zip','b322344131ac6e16a0824a491968b793bc34a6a348227dfe03f41acb0d0568df')]:
 p=R/name
 if not p.exists():rows.append({'name':name,'binary_upload_needed':True,'missing':True});continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 row={'name':name,'bytes':p.stat().st_size,'sha256':h.hexdigest(),'binary_upload_needed':h.hexdigest()!=expected}
 if row['binary_upload_needed']:
  dst=R/(name+'.failed_text_upload.bin');assert p.resolve().is_relative_to(R.resolve()) and dst.resolve().is_relative_to(R.resolve()) and not dst.exists();p.rename(dst);row['failed_copy_preserved_as']=dst.name
 rows.append(row)
(R/'binary_bundle_upload_repair_manifest.json').write_text(json.dumps({'rows':rows,'deletions':[],'reason':'text upload cannot preserve binary ZIP bytes; originals and local validated bundles unchanged'},indent=2));print(json.dumps(rows))
