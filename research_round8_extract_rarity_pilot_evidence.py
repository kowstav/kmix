import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;archive=R/'research_round8_rarity_residual_checkpoints.zip';D=R/'research_round8_native_evidence/rarity_residual_models';D.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 m=json.loads(z.read('checkpoint_evidence_manifest.json'));assert len(m['entries'])==72
 for row in m['entries']:
  target=(D/row['file']).resolve();assert target.parent==D.resolve() and row['file']==Path(row['file']).name
  b=z.read(row['file']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'];target.write_bytes(b)
 (D/'checkpoint_evidence_manifest.json').write_text(json.dumps(m,indent=2))
print(json.dumps({'status':'PASS','files':72,'every_model_optimizer_SHA256':'PASS','CRC':'PASS','source_zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
