from pathlib import Path
import json,time,hashlib
R=Path('/root/r14_batch_outputs');W=Path('/kaggle/working/hp_round14')
p=R/'hutter-r14-constructor-development-v1/constructor-development/manifest.json';m=json.loads(p.read_text())
assert m['status']=='COMPLETE_ALL_PAID_INVERSES' and len(m['cases'])==304
sums={};groups={}
for r in m['cases']:
    assert r['exact_inverse'] and r['role']=='development' and r['index']%2==0
    k=f"{r['mode']}:{r['alpha']}";sums[k]=sums.get(k,0)+r['archive_bytes'];groups.setdefault(k,[]).append(r['index'])
assert len(sums)==19 and all(len(set(v))==16 for v in groups.values())
ordered=sorted(sums,key=lambda k:(sums[k],k));bestbag=next(k for k in ordered if k.startswith('bag_'))
out={'selected_at':time.time(),'development_manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
     'selection_rule':'minimum complete paid archive across all 16 development regions; choose overall arm and best conditional bag separately',
     'eligible':sorted(sums),'development_bytes':sums,'selected_overall':ordered[0],'selected_conditional_bag':bestbag,
     'confirmation_opened':False,'status':'FROZEN_BEFORE_CONFIRMATION'}
dest=W/'constructor_selection_v1.json';assert not dest.exists();dest.write_text(json.dumps(out,indent=2));print(json.dumps(out))
