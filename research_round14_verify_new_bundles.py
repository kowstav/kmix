from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent
specs=[('confirmation_compact_a-20261009-1734','f8fd582c89e2bf2ec14df2bbda7d807bf7ebb806dfcc70f55a7a3c4d473431ba'),('confirmation_compact_combo-20261009-1734','0e2dc3cd4aaedbd6817035bd291828b7eae5245688552d3e8b404a0c87e2cc87'),('live_gate_receipts_356823832_v1','857490a73dbbc5766f0da93e98139d904f9e14edbb435b1d7aa64ec65fa97f39')]
for name,expected in specs:
    p=R/('research_round14_'+name+'.zip');assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
    dest=R/('research_round14_'+name+'_evidence');dest.mkdir(exist_ok=True)
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        entries=json.loads(z.read('entries.json'))
        for e in entries:
            b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
            out=(dest/e['path']).resolve();assert out.is_relative_to(dest.resolve());out.parent.mkdir(parents=True,exist_ok=True)
            if out.exists():assert out.read_bytes()==b
            else:out.write_bytes(b)
    print(json.dumps({'bundle':p.name,'verified_entries':len(entries),'sha256':expected}))
