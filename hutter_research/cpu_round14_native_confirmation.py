"""Frozen native guard on all eight R13 confirmation regions, four per job."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,multiprocessing as mp,os,resource,shutil,time,traceback
from . import cpu_round13_native as native
from .cpu_round13_jobs import atomic_json,initialize_lane,sha
def pair(i):
    modes=['pinned',2] if i%2==0 else [2,'pinned']
    rows=[native.archive_case(i,m) for m in modes];b={r['mode']:r for r in rows}
    return {'region':i,'cases':rows,'actual_archive_gain_bytes':b['pinned']['archive_bytes']-b[2]['archive_bytes'],
      'warm_logloss_gain_bytes':(b['pinned']['warm_target_bits']-b[2]['warm_target_bits'])/8}
def main(group):
    assets=list(Path('/kaggle/input').rglob('r13_assets.json'));heads=list(Path('/kaggle/input').rglob('r13_native_assets.json'))
    assert len(assets)==len(heads)==1
    native.ASSET=assets[0].parent;native.HEAD=heads[0].parent
    native.ROOT=Path('/root/r14_native_confirmation');native.ROOT.mkdir();native.OUT=Path('/kaggle/working/native-confirmation');native.OUT.mkdir()
    native.DEADLINE=time.monotonic()+10.3*3600
    regions=list(range(8,12)) if group=='a' else list(range(12,16))
    M={'status':'VERIFYING_ASSETS','started':time.time(),'regions':[],'worker_count':4,'indices':regions,
      'frozen_law':'R13 guard_4_fixedshare, mode2 binary SHA752a774c0455c50ac1799ccf029a7daa89499566165b8c492251b4d45841aa8e',
      'confirmation_caveat':'same fixed eight confirmation regions as frozen replay; validates coding, not an additional independent dataset',
      'deletions':[],'paid_usd':0,'GPU':False}
    def save():atomic_json(native.OUT/'manifest.json',M)
    try:
        save()
        for folder,manifest in ((native.ASSET,assets[0]),(native.HEAD,heads[0])):
            for n,r in json.loads(manifest.read_text())['files'].items():assert (folder/n).stat().st_size==r['bytes'] and sha(folder/n)==r['sha256']
        for src,dst in ((native.ASSET/'native_cmix','pinned_cmix'),(native.HEAD/'cmix_head_2','cmix_head_2')):
            shutil.copyfile(src,native.ROOT/dst);(native.ROOT/dst).chmod(0o700)
        assert sha(native.ROOT/'cmix_head_2')=='752a774c0455c50ac1799ccf029a7daa89499566165b8c492251b4d45841aa8e'
        cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4;ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M['status']='FOUR_LANE_NATIVE_CONFIRMATION';save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(pair,i) for i in regions]):M['regions'].append(f.result());save()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_ACTUAL_NATIVE_CONFIRMATION',finished=time.time(),worker_and_descendant_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
