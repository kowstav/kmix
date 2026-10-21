from pathlib import Path
import json,zipfile,hashlib
R=Path(__file__).resolve().parent;M=json.loads((R/'research_round14_detail_preservation.json').read_text());out=[]
for r in M['bundles']:
    p=R/('research_round14_'+Path(r['path']).name);raw=p.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        for e in r['entries']:
            b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
    out.append({'file':p.name,'sha256':r['sha256'],'entries_verified':len(r['entries'])})
(R/'research_round14_local_detail_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
