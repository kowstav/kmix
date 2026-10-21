"""Matched guard-vs-guard+match-pruning; reuse prior N/M only for byte interaction."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,multiprocessing as mp,os,resource,shutil,time,traceback
from . import cpu_round13_native as n
from .cpu_round13_jobs import atomic_json,initialize_lane,sha

def pair(i):
    modes=['guard_base','guard_match'] if (i//2)%2==0 else ['guard_match','guard_base']
    rows=[n.archive_case(i,m) for m in modes];by={r['mode']:r for r in rows}
    assert len({r['input_sha256'] for r in rows})==1
    return {'region':i,'cases':rows,'guard_marginal_actual_bytes':by['guard_base']['archive_bytes']-by['guard_match']['archive_bytes'],
            'guard_marginal_warm_ideal_bytes':(by['guard_base']['warm_target_bits']-by['guard_match']['warm_target_bits'])/8}

def main(regions=(0,2,4,6),run_label='development'):
    assert len(regions)==4 and len(set(regions))==4 and all(isinstance(i,int) and 0<=i<16 for i in regions)
    assert run_label in ('development','confirmation_a','confirmation_b')
    a=list(Path('/kaggle/input').rglob('r13_assets.json'));b=list(Path('/kaggle/input').rglob('guard_match_assets.json'));assert len(a)==len(b)==1
    n.ASSET=a[0].parent;asset=b[0].parent;n.ROOT=Path('/root/r14_guard_match');n.ROOT.mkdir();n.OUT=Path('/kaggle/working/guard-match');n.OUT.mkdir();n.DEADLINE=time.monotonic()+10.3*3600
    M={'status':'VERIFYING_ASSETS','started':time.time(),'regions':[],'workers':4,'deletions':[],'GPU':False,'paid_usd':0,'run_label':run_label,'registered_regions':list(regions),'scope':'four '+run_label+' regional pairs, guard control versus guard+match-removal; no full-history claim'}
    def save():atomic_json(n.OUT/'manifest.json',M)
    try:
        save();meta=json.loads(b[0].read_text());assert meta['gate']=='PASS_FOUR_NATIVE_COMBINED_INVERSES_AND_PACKED_GUARD_PARITY'
        for manifest in (a[0],b[0]):
            for name,expected in json.loads(manifest.read_text())['files'].items():p=manifest.parent/name;assert p.stat().st_size==expected['bytes'] and sha(p)==expected['sha256']
        for name in ('guard_base','guard_match'):
            p=n.ROOT/('cmix_head_'+name);shutil.copyfile(asset/('cmix_'+name),p);p.chmod(0o700)
        M['asset_manifest_sha256']=sha(b[0]);cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4
        ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M['status']='FOUR_LANE_NATIVE_GUARD_MATCH_PAIRS';save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(pair,i) for i in regions]):M['regions'].append(f.result());save()
        after=resource.getrusage(resource.RUSAGE_CHILDREN);M.update(status='COMPLETE_FOUR_NATIVE_GUARD_MATCH_PAIRS',finished=time.time(),worker_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
