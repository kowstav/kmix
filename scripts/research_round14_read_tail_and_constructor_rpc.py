from pathlib import Path
import json,time,shutil
R=Path('/root/r14_batch_outputs');W=Path('/kaggle/working/hp_round14');out={}
s=json.loads((W/'constructor_selection_v1.json').read_text());assert s['status']=='FROZEN_BEFORE_CONFIRMATION'
for role in ('development','confirmation'):
    p=R/f'hutter-r14-constructor-{role}-v1'/('constructor-'+role)/'manifest.json';m=json.loads(p.read_text())
    assert m['status']=='COMPLETE_ALL_PAID_INVERSES' and len(m['cases'])==304
    sums={};baseline={};by={}
    for r in m['cases']:
        assert r['exact_inverse'];k=f"{r['mode']}:{r['alpha']}";sums[k]=sums.get(k,0)+r['archive_bytes'];by.setdefault(k,{})[r['index']]=r['archive_bytes'];baseline[r['index']]={c:r[c+'_bytes'] for c in ('gzip','zstd')}
    out[role]={'status':m['status'],'cases':len(m['cases']),'bytes':sums,'raw_gzip_bytes':sum(r['gzip'] for r in baseline.values()),'raw_zstd_bytes':sum(r['zstd'] for r in baseline.values()),'worker_CPU_seconds':m['worker_CPU_seconds'],'wall_seconds':m['finished']-m['started'],'selected_region_bytes':{k:by[k] for k in [s['selected_overall'],s['selected_conditional_bag'],'markov:4','bag:0']}}
out['selection']=s;(W/'constructor_analysis_v1.json').write_text(json.dumps(out,indent=2));print('CONSTRUCTOR',json.dumps(out))
for n in ('tail_collection_v1.json','word_costs_v2/manifest.json'):
    p=W/n
    if p.exists():
        m=json.loads(p.read_text());print(n,json.dumps({k:v for k,v in m.items() if k not in ('shards',)}))
d=R/'hutter-r14-article-order-ppmd-v1'
for p in d.rglob('*'):
    if p.is_file() and p.suffix in ('.json','.log'):print(str(p.relative_to(d)),p.read_text(errors='replace')[-6500:])
print('compiler', {x:shutil.which(x) for x in ('clang++-17','clang++','ld.lld','g++')})
