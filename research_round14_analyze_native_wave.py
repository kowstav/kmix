from pathlib import Path
import hashlib,json,math,statistics,time
R=Path(__file__).resolve().parent;D=R/'research_round14_native_wave_evidence';M={'native':{},'article_order':{},'analysis_time':time.time(),'no_population_or_full_history_claim':True}
baselines={}
for p in D.rglob('manifest.json'):
    m=json.loads(p.read_text(encoding='utf-8'))
    if 'arm' not in m:continue
    assert m['status']=='COMPLETE_FOUR_NATIVE_PAIRS' and {r['region'] for r in m['regions']}=={0,2,4,6}
    arm=m['arm'];rows=[]
    for r in sorted(m['regions'],key=lambda x:x['region']):
        by={c['mode']:c for c in r['cases']};n=by['neutral'];c=by[arm]
        assert n['exact_independent_inverse'] and c['exact_independent_inverse'] and n['input_sha256']==c['input_sha256']
        base=(n['archive_sha256'],n['probabilities_sha256'],n['warm_target_bits'])
        assert baselines.setdefault(r['region'],base)==base,'neutral changes across hosts'
        q={'region':r['region'],'actual_gain_B':n['archive_bytes']-c['archive_bytes'],'warm_gain_ideal_B':(n['warm_target_bits']-c['warm_target_bits'])/8,
           'baseline_archive_bytes':n['archive_bytes'],'candidate_archive_bytes':c['archive_bytes'],'baseline_warm_bits':n['warm_target_bits']}
        for phase in ('encode','decode'):
            for label,s in (('baseline',n),('candidate',c)):q[phase+'_'+label+'_CPU_s']=s[phase]['CPU_user_seconds']+s[phase]['CPU_system_seconds']
            q[phase+'_RSS_saved_KiB']=n[phase]['peak_RSS_KiB']-c[phase]['peak_RSS_KiB']
            q[phase+'_CPU_saved_s']=q[phase+'_baseline_CPU_s']-q[phase+'_candidate_CPU_s']
        rows.append(q)
    totals={k:sum(r[k] for r in rows) for k in rows[0] if k!='region'}
    for phase in ('encode','decode'):totals[phase+'_CPU_saved_percent']=100*totals[phase+'_CPU_saved_s']/totals[phase+'_baseline_CPU_s']
    totals['warm_bit_reduction_percent']=totals['warm_gain_ideal_B']*800/totals['baseline_warm_bits']
    M['native'][arm]={'regions':rows,'totals':totals,'CPU_cores_effective':m['worker_CPU_seconds']/(m['finished']-m['started']),'manifest':str(p.relative_to(R)),'manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
p=D/'hutter-r14-article-order-native-v2/article-order-native/manifest.json';m=json.loads(p.read_text(encoding='utf-8'));assert m['status']=='COMPLETE_160_PAID_NATIVE_PPMD_ORDER_CASES'
dev=[r for r in m['regions'] if r['role']=='development'];check=hashlib.sha256(json.dumps(sorted(dev,key=lambda r:r['index']),sort_keys=True).encode()).hexdigest();assert check==m['selection']['development_sha256']
a={'selected':m['selection']['selected_graph'],'frozen':m['selection']['frozen'],'manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cases':sum(len(r['cases']) for r in m['regions']),'roles':{},'CPU_cores_effective':m['worker_CPU_seconds']/(m['finished']-m['started']),'backend':m['backend']}
assert a['cases']==160 and all(c['exact_inverse'] for r in m['regions'] for c in r['cases'])
for role in ('development','confirmation'):
    rs=[r for r in m['regions'] if r['role']==role];d={}
    for level in (8,16):
        sums={name:sum(c['archive_bytes'] for r in rs for c in r['cases'] if c['name']==name and c['PPMd_order']==level) for name in ('original','reverse','random','rare_word_graph','conditional_ppmd_graph')}
        d[str(level)]={'totals':sums,'selected_gain_B':sums['original']-sums[a['selected']]}
    a['roles'][role]={'regions':len(rs),'raw_bytes':sum(r['input_bytes'] for r in rs),'PPMd_orders':d}
a['temporary_scratch_created_and_removed']={k:sum(r['temporary_scratch_created_and_removed'][k] for r in m['regions']) for k in m['regions'][0]['temporary_scratch_created_and_removed']}
M['article_order']=a
(R/'research_round14_native_wave_analysis_v1.json').write_text(json.dumps(M,indent=2),encoding='utf-8')
print(json.dumps({'native':{k:{'totals':v['totals'],'CPU_cores_effective':v['CPU_cores_effective'],'per_region_gain_B':[r['actual_gain_B'] for r in v['regions']]} for k,v in M['native'].items()},'article':a},indent=2))
