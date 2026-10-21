from pathlib import Path
import hashlib,json,time,zipfile
W=Path('/kaggle/working/hp_round13');P=W/'pulls'
grammar=P/'hutter-r13-constructor-descendants-v1'/'constructor-descendants'
storage=P/'hutter-r13-weight-storage-v1'/'weight-storage'
g=json.loads((grammar/'manifest.json').read_text());s=json.loads((storage/'manifest.json').read_text())
assert g['status']==s['status']=='COMPLETE_FOUR_LANE_FINITE_CPU_JOB'
# Freeze the single grammar arm from development totals before opening any
# confirmation outcome in this analysis. Generation itself used fixed arms.
dev=[r for r in g['cases'] if r['role']=='development']
totals={}
for r in dev:totals[(r['mode'],r['alpha'])]=totals.get((r['mode'],r['alpha']),0)+r['archive_bytes']
choice=min(totals,key=lambda k:(totals[k],k))
selection={'selected_at':time.time(),'policy':'minimum paid aggregate development archive bytes; deterministic lexical tie break',
    'development_indices':sorted({r['index'] for r in dev}),'chosen_arm':list(choice),
    'development_totals':[{'mode':k[0],'alpha':k[1],'bytes':v} for k,v in sorted(totals.items())],
    'selection_is_proxy_only':True}
select_path=W/'grammar_selection_v1.json';assert not select_path.exists();select_path.write_text(json.dumps(selection,indent=2))
# Confirmation is opened only after the selection above has been written.
confirm=[r for r in g['cases'] if r['role']=='confirmation' and (r['mode'],r['alpha'])==choice]
best=min(s['cases'],key=lambda r:(r['model_bytes'],r['layout'],r['codec']))
summary={'grammar':{'manifest_status':g['status'],'cases':len(g['cases']),'CPU_lanes':sorted({r['cpu'] for r in g['cases']}),
    'elapsed_seconds':g['finished']-g['started'],'measured_worker_CPU_seconds':sum(r['CPU_seconds'] for r in g['cases']),
    'selection':selection,'selected_confirmation':[{'index':r['index'],'archive_bytes':r['archive_bytes'],
       'gzip_baseline_bytes':r['gzip_baseline_bytes'],'gain_bytes':r['gain_bytes']} for r in confirm],
    'selected_confirmation_gain_bytes':sum(r['gain_bytes'] for r in confirm)},
 'storage':{'manifest_status':s['status'],'cases':len(s['cases']),'CPU_lanes':sorted({r['cpu'] for r in s['cases']}),
    'elapsed_seconds':s['finished']-s['started'],'measured_worker_CPU_seconds':sum(r['CPU_seconds'] for r in s['cases']),
    'best':best,'arms':s['cases']}}
(W/'completed_summary_v1.json').write_text(json.dumps(summary,indent=2))
target=W/'completed_compact_evidence_v1.zip';assert not target.exists()
entries=[]
with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    paths=list(grammar.rglob('*'))+[p for p in storage.rglob('*') if p.suffix=='.json']
    paths += [storage/f"storage_{best['layout']}_{best['codec']}.hpwt",select_path,W/'completed_summary_v1.json']
    for p in paths:
        if not p.is_file():continue
        data=p.read_bytes();name=str(p.relative_to(W));z.writestr(name,data)
        entries.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    z.writestr('entries.json',json.dumps(entries,indent=2))
out={'status':'COMPLETE','archive':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
 'entries':len(entries),'storage_nonselected_models':'retained in private notebook outputs and remote pulls; their JSON/hash records included here','deletions':[]}
(W/'compact_preserve_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
