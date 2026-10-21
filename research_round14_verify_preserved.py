from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent;out=[]
for record in ('batch_collection_v1','paginated_collection_v2','tail_collection_v1','word_cost_summary_v2'):
    m=json.loads((R/('research_round14_'+record+'.json')).read_text());v=m['compact'];p=R/('research_round14_'+Path(v['path']).name)
    assert p.stat().st_size==v['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
    target=R/'research_round14_batch_evidence';target.mkdir(exist_ok=True)
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None;entries=json.loads(z.read('entries.json'))
        assert len(entries)==v['entries']
        for e in entries:
            b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
            dest=target/('word_costs_v2' if record=='word_cost_summary_v2' else '')/e['path'];assert dest.resolve().is_relative_to(target.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():assert dest.read_bytes()==b
            else:dest.write_bytes(b)
    out.append({'file':p.name,'sha256':v['sha256'],'CRC_and_entries_verified':len(entries)})
(R/'research_round14_preserved_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
