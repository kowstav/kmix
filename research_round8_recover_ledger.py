import hashlib, json
from pathlib import Path
R = Path(__file__).resolve().parent
D = R / 'research_round8_recovered_round1'
D.mkdir(exist_ok=True)
src = json.loads((R/'research_round8_session_readiness.json').read_text())
rows=[]
for row in src['early_reports']:
    p=D/Path(row['path']).name
    blob=row['text'].encode()
    if p.exists():
        assert p.read_bytes()==blob, 'Do not overwrite different recovered evidence'
    else: p.write_bytes(blob)
    try: obj=json.loads(row['text'])
    except json.JSONDecodeError: obj=None
    info={'remote':row['path'],'local':str(p),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(), 'root_type':type(obj).__name__}
    if isinstance(obj,dict): info['keys']=list(obj)
    if isinstance(obj,list):
        info['rows']=len(obj)
        info['first_row_keys']=list(obj[0]) if obj and isinstance(obj[0],dict) else []
    rows.append(info)
(D/'manifest.json').write_text(json.dumps({'recovered_date':'2026-10-06','session':355655943,'files':rows,'deletions':[]},indent=2))
print(json.dumps(rows,indent=2))
