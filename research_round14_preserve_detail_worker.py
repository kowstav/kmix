from pathlib import Path
import hashlib,json,time,traceback,zipfile
W=Path('/kaggle/working');R=W/'hp_round14';P=Path('/root/hp_round14_pulls')
M={'status':'VERIFYING_DUPLICATES','started':time.time(),'deletions':[],'bundles':[]}
def save():(R/'detail_preservation.json').write_text(json.dumps(M,indent=2))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4<<20),b''):h.update(b)
    return h.hexdigest()
try:
    assert not (R/'detail_preservation.json').exists();save()
    duplicates=sorted((W/'hp_round8').glob('native_inline_*_v1/*_candidate_decode/hidden.q8'))
    for p in duplicates:
        if p.parent.parent.name not in ('native_inline_wide_v1','native_inline_residual_v1'):continue
        original=p.parent.with_name(p.parent.name.replace('_candidate_decode','_candidate'))/'hidden.q8'
        assert p.resolve().is_relative_to((W/'hp_round8').resolve()) and original.resolve().is_relative_to((W/'hp_round8').resolve())
        if not original.exists() or original.stat().st_size!=p.stat().st_size:continue
        digest=sha(p)
        if sha(original)!=digest:continue
        row={'path':str(p),'bytes':p.stat().st_size,'sha256':digest,'identical_preserved_original':str(original),
             'reason':'byte-identical duplicate decoder observer trace; original source/model/data and encode-side trace preserved'}
        M['deletions'].append({**row,'deletion_completed':False});save();p.unlink();M['deletions'][-1]['deletion_completed']=True;save()
    groups={}
    for role in ('development','confirmation'):
        groups['warm_costs_'+role]=sorted((P/f'hutter-r13-warm-{role}-v1'/('warm-'+role)).glob('*.cost.f32.gz'))
        assert len(groups['warm_costs_'+role])==8
    native=W/'hp_round13/native_binaries_v1';groups['native_sources_and_binaries']=list(native.glob('cmix_head_*'))+[W/'hp_round13/native_integration_sources_v1.zip']
    storage=P/'hutter-r13-weight-storage-regeneration-v1/weight-storage-regeneration'
    groups['best_regenerated_model']=[storage/'nibble_gzip.hpwt']
    for label,files in groups.items():
        entries=[];target=R/(label+'.zip')
        with zipfile.ZipFile(target,'x',zipfile.ZIP_STORED) as z:
            for p in files:
                assert p.exists();n=p.name;z.write(p,n);entries.append({'path':n,'bytes':p.stat().st_size,'sha256':sha(p)})
            z.writestr('entries.json',json.dumps(entries,indent=2))
        M['bundles'].append({'label':label,'path':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'entries':entries});save()
    M.update(status='COMPLETE_DETAIL_BUNDLES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
