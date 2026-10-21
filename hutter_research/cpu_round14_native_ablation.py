"""Four matched regional pairs for one preflight-qualified CPU intervention."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,multiprocessing as mp,os,resource,shutil,time,traceback
from . import cpu_round13_native as native
from .cpu_round13_jobs import atomic_json,initialize_lane,sha
ARM=None
def pair(i):
    modes=['neutral',ARM] if (i//2)%2==0 else [ARM,'neutral']
    rows=[native.archive_case(i,m) for m in modes];by={r['mode']:r for r in rows}
    out={'region':i,'cases':rows,'actual_archive_gain_bytes':by['neutral']['archive_bytes']-by[ARM]['archive_bytes'],
         'warm_gain_ideal_bytes':(by['neutral']['warm_target_bits']-by[ARM]['warm_target_bits'])/8}
    for phase in ('encode','decode'):
        def cpu(r):return r[phase]['CPU_user_seconds']+r[phase]['CPU_system_seconds']
        out[phase+'_CPU_saved_seconds']=cpu(by['neutral'])-cpu(by[ARM])
    return out
def main(arm,regions=(0,2,4,6),run_label=None):
    global ARM
    assert arm in ('prune_word','prune_match','prune_indirect','output_fp32');ARM=arm
    regions=tuple(regions);assert len(regions)==4 and len(set(regions))==4 and all(0<=i<16 for i in regions)
    suffix='_'+run_label if run_label else ''
    assert run_label is None or run_label in ('confirmation_a','confirmation_b')
    a=list(Path('/kaggle/input').rglob('r13_assets.json'));b=list(Path('/kaggle/input').rglob('r14_native_cpu_assets.json'));assert len(a)==len(b)==1
    native.ASSET=a[0].parent;head=b[0].parent;native.ROOT=Path('/root/r14_native_'+arm+suffix);native.ROOT.mkdir()
    native.OUT=Path('/kaggle/working/native-'+arm+suffix);native.OUT.mkdir();native.DEADLINE=time.monotonic()+10.3*3600
    M={'status':'VERIFYING_ASSETS','started':time.time(),'arm':arm,'regions':[],'region_ids':regions,'run_label':run_label,'workers':4,'deletions':[],'GPU':False,'paid_usd':0,
       'scope':'four 3 MiB regional histories, 2 MiB warmup; laboratory resources, no full-history or production eligibility claim'}
    def save():atomic_json(native.OUT/'manifest.json',M)
    try:
        save();meta=json.loads(b[0].read_text());assert meta['native_preflight_status']=='PASS_NEUTRAL_PARITY_AND_SIX_EXACT_INVERSES'
        for manifest in (a[0],b[0]):
            for n,r in json.loads(manifest.read_text())['files'].items():p=manifest.parent/n;assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
        for name in ('neutral',arm):
            p=native.ROOT/('cmix_head_'+name);shutil.copyfile(head/('cmix_'+name),p);p.chmod(0o700)
        M['source_sha256']=meta['source_sha256'];M['binary_manifest_sha256']=sha(b[0]);cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4
        ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M['status']='FOUR_LANE_NATIVE_REGIONAL_PAIRS';save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(pair,i) for i in regions]):M['regions'].append(f.result());save()
        after=resource.getrusage(resource.RUSAGE_CHILDREN);M.update(status='COMPLETE_FOUR_NATIVE_PAIRS',finished=time.time(),worker_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
