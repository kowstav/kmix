
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import hashlib,json,statistics,time
R=project_root(__file__)
A=project_path('research_round14_confirmation_compact_a-20261009-1734_evidence', base=R)
C=project_path('research_round14_confirmation_compact_combo-20261009-1734_evidence', base=R)
D=project_path('research_round14_native_wave_evidence', base=R)
result={'time':time.time(),'scope':'four of eight confirmation regions plus four development interaction regions; no full-history/package claim','confirmation_a':{}}
old={}
for p in (project_path('research_round14_batch_evidence', base=R)).glob('hutter-r14-native-confirmation-*/native-confirmation/manifest.json'):
    m=json.loads(p.read_text())
    for r in m['regions']:
        for c in r['cases']:
            if c['mode']=='pinned':old[c['region']]=c
def summary(m,baseline,candidate):
    rows=[]
    for reg in sorted(m['regions'],key=lambda r:r['region']):
        by={c['mode']:c for c in reg['cases']};b,c=by[baseline],by[candidate]
        assert b['exact_independent_inverse'] and c['exact_independent_inverse'] and b['input_sha256']==c['input_sha256']
        row={'region':reg['region'],'actual_gain_B':b['archive_bytes']-c['archive_bytes'],'warm_gain_ideal_B':(b['warm_target_bits']-c['warm_target_bits'])/8}
        for phase in ('encode','decode'):
            for label,case in [('baseline',b),('candidate',c)]:row[phase+'_'+label+'_CPU_s']=case[phase]['CPU_user_seconds']+case[phase]['CPU_system_seconds']
            row[phase+'_RSS_saved_KiB']=b[phase]['peak_RSS_KiB']-c[phase]['peak_RSS_KiB']
        rows.append(row)
    s={'regions':rows,'actual_gain_B':sum(r['actual_gain_B'] for r in rows),'warm_gain_ideal_B':sum(r['warm_gain_ideal_B'] for r in rows),'effective_cores':m['worker_CPU_seconds']/(m['finished']-m['started'])}
    for phase in ('encode','decode'):
        b=sum(r[phase+'_baseline_CPU_s'] for r in rows);c=sum(r[phase+'_candidate_CPU_s'] for r in rows)
        s[phase+'_CPU_reduction_percent']=100*(b-c)/b
        s[phase+'_RSS_saved_KiB_mean']=statistics.mean(r[phase+'_RSS_saved_KiB'] for r in rows)
    return s
for p in A.rglob('manifest.json'):
    m=json.loads(p.read_text());assert m['status']=='COMPLETE_FOUR_NATIVE_PAIRS'
    assert {r['region'] for r in m['regions']}=={8,10,12,14}
    for reg in m['regions']:
        neutral=next(c for c in reg['cases'] if c['mode']=='neutral');reference=old[reg['region']]
        assert all(neutral[k]==reference[k] for k in ['archive_sha256','probabilities_sha256','input_sha256','warm_target_bits'])
    s=summary(m,'neutral',m['arm']);s['manifest_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();result['confirmation_a'][m['arm']]=s
p=next(C.rglob('manifest.json'));m=json.loads(p.read_text());assert m['status']=='COMPLETE_FOUR_NATIVE_GUARD_MATCH_PAIRS'
s=summary(m,'guard_base','guard_match')
prior=json.loads(next((D/'hutter-r14-native-prune-match-v1').rglob('manifest.json')).read_text())
byprior={r['region']:{c['mode']:c for c in r['cases']} for r in prior['regions']}
for row,reg in zip(s['regions'], sorted(m['regions'],key=lambda r:r['region'])):
    by={c['mode']:c for c in reg['cases']};n,pruned=byprior[row['region']]['neutral'],byprior[row['region']]['prune_match'];g,gm=by['guard_base'],by['guard_match']
    assert len({c['input_sha256'] for c in [n,pruned,g,gm]})==1
    row['interaction_actual_B']=g['archive_bytes']+pruned['archive_bytes']-n['archive_bytes']-gm['archive_bytes']
    row['interaction_warm_ideal_B']=(g['warm_target_bits']+pruned['warm_target_bits']-n['warm_target_bits']-gm['warm_target_bits'])/8
    row['joint_vs_neutral_actual_B']=n['archive_bytes']-gm['archive_bytes']
    row['joint_vs_neutral_warm_ideal_B']=(n['warm_target_bits']-gm['warm_target_bits'])/8
for k in ['interaction_actual_B','interaction_warm_ideal_B','joint_vs_neutral_actual_B','joint_vs_neutral_warm_ideal_B']:s[k]=sum(r[k] for r in s['regions'])
s['manifest_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();result['guard_match_development']=s
(project_path('research_round14_confirm_a_joint_analysis_v1.json', base=R)).write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
