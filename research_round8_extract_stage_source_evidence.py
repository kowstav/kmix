import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'research_round8_native_evidence/stage_observer_source';D.mkdir(exist_ok=False);archive=R/'research_round8_stage_observer_source_evidence.zip'
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None;m=json.loads(z.read('source_evidence_manifest.json'))
 for row in m['entries']:
  p=(D/row['file']).resolve();assert p.is_relative_to(D.resolve());b=z.read(row['file']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 (D/'source_evidence_manifest.json').write_text(json.dumps(m,indent=2))
print(json.dumps({'status':'PASS','files':len(m['entries']),'all_SHA256_and_CRC':'PASS','zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
