from pathlib import Path
import json
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_batch_outputs')
print((W/'tail_collection_v1.json').read_text())
for p in (R/'hutter-r14-article-order-ppmd-v1').rglob('*'):
    if p.is_file() and p.suffix in ('.log','.json'):print(p.name,p.read_text(errors='replace')[-8000:])
p=R/'hutter-r14-native-confirmation-a-v1/native-confirmation/manifest.json'
if p.exists():
    m=json.loads(p.read_text());print('NATIVE_A',json.dumps({**{k:v for k,v in m.items() if k!='regions'},'regions':[{'region':r['region'],'archive_gain':r['actual_archive_gain_bytes'],'warm_gain':r['warm_logloss_gain_bytes']} for r in m['regions']]}))
