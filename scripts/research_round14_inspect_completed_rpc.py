from pathlib import Path
import json,subprocess
R=Path('/root/r14_batch_outputs');out={}
for slug,kind in [('hutter-r14-group-weight-storage-v1','group-storage'),('hutter-r14-native-confirmation-b-v1','native-confirmation')]:
    p=R/slug/kind/'manifest.json'
    if p.exists():
        m=json.loads(p.read_text());out[kind]={k:v for k,v in m.items() if k not in ('groups','cases')}
        out[kind]['groups_tested']=len(m.get('groups',[]))
        out[kind]['cases']=m.get('cases',[])
for role in ('development','confirmation'):
    d=R/('hutter-r14-constructor-'+role+'-v1')
    out['constructor_'+role]={'top_files':[str(p.relative_to(d)) for p in d.iterdir()], 'logs':{str(p.relative_to(d)):p.read_text(errors='replace')[-7000:] for p in d.rglob('*.log')}}
print(json.dumps(out))
