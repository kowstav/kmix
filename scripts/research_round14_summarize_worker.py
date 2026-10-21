from pathlib import Path
import hashlib,json,time,traceback
R=Path('/root/hp_round14_pulls');W=Path('/kaggle/working/hp_round14')
def manifest(slug,kind):return json.loads((R/slug/kind/'manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def warm_totals(m):
    assert m['status']=='COMPLETE_FOUR_LANE_FINITE_CPU_JOB' and len(m['cases'])==8
    sums={};regions=[]
    for r in m['cases']:
        assert r['independent_decode_exact'] and r['summary']['identity_mismatch_bits']==r['summary']['memory_zero_mismatch_bits']==0
        ws=r['warm_windows'];assert len(ws)==2 and sum(v['bytes'] for v in ws)==1048576
        g={a:sum((v['baseline_bits']-v['arms'][a])/8 for v in ws) for a in ws[0]['arms']}
        for a,v in g.items():sums[a]=sums.get(a,0)+v
        regions.append({'index':r['region']['index'] if 'index' in r['region'] else r['region'].get('id'),
            'offset':r['region']['offset'],'gains_bytes':g,'baseline_warm_bits':sum(v['baseline_bits'] for v in ws),
            'baseline_minus_cost_bits':r['baseline_minus_cost_bits']})
    return {'aggregate_gain_bytes':sums,'regions':regions,'scored_bytes':8388608,
       'native_bytes':8*3145728,'wall_seconds':m['finished']-m['started'],
       'encode_and_decode_CPU_seconds':sum(sum(r[k]['CPU_user_seconds']+r[k]['CPU_system_seconds'] for k in ('encode','decode')) for r in m['cases']),
       'CPU_note':'consumer CPU excluded; no utilization ratio from incomplete total'}
try:
    D=manifest('hutter-r13-warm-development-v1','warm-development');dev=warm_totals(D)
    eligible=('full_250','full_1000','full_4000','global_250','reduced_250','add_memory_250','guard_4_fixedshare','guard_memory_pair')
    selected=min(eligible,key=lambda a:(-dev['aggregate_gain_bytes'][a],a))
    freeze={'selected_at':time.time(),'eligible':eligible,'selected':selected,'development':dev,
      'rule':'greatest total 2-to-3 MiB warm regional gain across eight development regions; lexical tie break; descriptive replay only',
      'development_manifest_sha256':sha(R/'hutter-r13-warm-development-v1/warm-development/manifest.json'),
      'confirmation_opened_before_freeze':False,'eligibility_clarification':'exclude the identity and matched null/short-memory controls; selection list recorded now before confirmation inspection'}
    p=W/'warm_selection_v1.json';assert not p.exists();p.write_text(json.dumps(freeze,indent=2))
    C=manifest('hutter-r13-warm-confirmation-v1','warm-confirmation');conf=warm_totals(C)
    N=manifest('hutter-r13-native-final-head-v2','native-final-head')
    S=manifest('hutter-r13-weight-storage-regeneration-v1','weight-storage-regeneration')
    F=manifest('hutter-r13-full-corpus-factorization-v1','full-corpus-factorization')
    out={'observed_at':time.time(),'selection':freeze,'confirmation':conf,
      'selected_confirmation_gain_bytes':conf['aggregate_gain_bytes'][selected],
      'native':N,'storage':S,'full':{'status':F['status'],'archives':F.get('full_archives'),
         'cases':len(F.get('cases',[])),'wall_seconds':F.get('finished',0)-F['started'],
         'worker_CPU_seconds':sum(r['CPU_seconds'] for r in F.get('cases',[]))}}
    (W/'summary_v1.json').write_text(json.dumps(out,indent=2))
except BaseException as e:
    (W/'summary_failure_v1.json').write_text(json.dumps({'error':repr(e),'traceback':traceback.format_exc()},indent=2));raise
