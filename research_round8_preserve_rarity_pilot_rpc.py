import hashlib,json,pathlib,zipfile
D=pathlib.Path('/kaggle/working/hp_round8/rarity_residual_pilot_v1');m=json.loads((D/'manifest.json').read_text());assert m['status']=='COMPLETE_PARTIAL_DICTIONARY_MASK_RESIDUAL_TRAINING'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=D/'rarity_residual_pilot_checkpoints.zip'
if not out.exists():
 entries=[]
 for row in m['rungs']:
  for field,hashfield in [('parameter_file','parameter_sha256'),('optimizer_resume_file','optimizer_resume_sha256')]:
   p=D/row[field];assert p.parent==D and sha(p)==row[hashfield];entries.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
 assert len(entries)==72 and len({v['file'] for v in entries})==72
 (D/'checkpoint_evidence_manifest.json').write_text(json.dumps({'entries':entries,'scope':'all36rungs, inference parameters and optimizer resume state; original core unchanged'},indent=2))
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for row in entries:z.write(D/row['file'],row['file'])
  z.write(D/'checkpoint_evidence_manifest.json','checkpoint_evidence_manifest.json')
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'preserved_without_deletion':True}))
