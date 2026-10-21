"""Paid conditional-bag descendants, 32 independently located raw regions."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import gzip,hashlib,json,multiprocessing as mp,os,random,resource,time,traceback
from .cpu_round13_jobs import atomic_json,initialize_lane,sha
from . import cpu_round13_jobs as lanes
from .constructor_codec import encode,decode,inspect_sizes
ROOT=OUT=ASSET=None
ARMS=[('markov',4),('coarse_right',4),('bag',0)]+[(f'bag_{s}{b}',a) for s in ('markov','right','wrong','left') for b in (0,1) for a in (1,4)]
def offsets():
    rng=random.Random(1400831);spans=[((2*i+1)*1000000000//32,1048576) for i in range(16)];result=[]
    for i in range(32):
        lo=i*1000000000//32;hi=(i+1)*1000000000//32-1048576
        while True:
            x=rng.randint(lo,hi)
            if all(x+1048576<=y or y+n<=x for y,n in spans):break
        spans.append((x,1048576));result.append(x)
    return result
def case(task):
    i,offset,mode,alpha=task;start=time.monotonic();u=resource.getrusage(resource.RUSAGE_SELF)
    with (ROOT/'original_enwik9.bin').open('rb') as f:f.seek(offset);raw=f.read(1048576)
    blob=encode(raw,mode,alpha);assert decode(blob)==raw
    label=f'constructor_{i:02}_{mode}_{alpha}';(OUT/(label+'.hpctor')).write_bytes(blob)
    import zstandard as zstd
    a=resource.getrusage(resource.RUSAGE_SELF)
    row={'index':i,'offset':offset,'input_bytes':len(raw),'input_sha256':hashlib.sha256(raw).hexdigest(),
      'mode':mode,'alpha':alpha,'role':'development' if i%2==0 else 'confirmation','archive_bytes':len(blob),
      'archive_sha256':hashlib.sha256(blob).hexdigest(),'gzip_bytes':len(gzip.compress(raw,mtime=0)),
      'zstd_bytes':len(zstd.ZstdCompressor(level=9).compress(raw)),'channels':inspect_sizes(blob),
      'exact_inverse':True,'CPU_lane':lanes.LANE_CPU,'CPU_seconds':a.ru_utime+a.ru_stime-u.ru_utime-u.ru_stime,
      'wall_seconds':time.monotonic()-start,'peak_RSS_KiB':a.ru_maxrss}
    atomic_json(OUT/(label+'.json'),row);return row
def main(role):
    global ROOT,OUT,ASSET
    from . import cpu_round13_jobs as old
    paths=list(Path('/kaggle/input').rglob('r13_assets.json'));assert len(paths)==1;ASSET=paths[0].parent
    ROOT=Path('/root/r14_constructor_'+role);ROOT.mkdir();OUT=Path('/kaggle/working/constructor-'+role);OUT.mkdir()
    old.ROOT=ROOT;old.ASSET=ASSET;source=old.raw_source()
    M={'status':'PREFLIGHT','started':time.time(),'role':role,'cases':[],'workers':4,'arms':ARMS,'offsets':offsets(),
      'raw_source_sha256':sha(source),'limits':'paid raw-text proxy; not native stream or best possible architecture','deletions':[]}
    def save():atomic_json(OUT/'manifest.json',M)
    try:
        save();cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4
        for mode,alpha in ARMS:assert decode(encode(b'There was a camel. The the AND it.\x00\xff',mode,alpha))==b'There was a camel. The the AND it.\x00\xff'
        ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        tasks=[(i,x,m,a) for i,x in enumerate(offsets()) if i%2==(role=='confirmation') for m,a in ARMS]
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M.update(status='FOUR_LANE_RUNNING',case_count=len(tasks));save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(case,t) for t in tasks]):M['cases'].append(f.result());save()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_ALL_PAID_INVERSES',finished=time.time(),worker_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
