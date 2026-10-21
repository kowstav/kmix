from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,mmap,multiprocessing as mp,os,random,resource,time,traceback
from .cpu_round13_jobs import atomic_json,initialize_lane,sha
from . import cpu_round13_jobs as lanes,article_order_ppmd as order
ROOT=OUT=None;PAGES=None
def region(i):
    start=time.monotonic();u=resource.getrusage(resource.RUSAGE_SELF);first=(2*i+1)*len(PAGES)//32
    indices=list(range(first,first+128));pages=[]
    with (ROOT/'original_enwik9.bin').open('rb') as f:
        for j in indices:
            a,b=PAGES[j];f.seek(a);pages.append(f.read(b-a))
    orders,pairs=order.graph_orders(pages);rng=random.Random(140008+i);r=list(range(128));rng.shuffle(r)
    orders={'original':list(range(128)),'reverse':list(range(127,-1,-1)),'random':r,**orders};rows=[]
    # Order-8 vs order-16 tests whether graph gains survive a stronger context.
    for level in (8,16):
        for name,permutation in orders.items():
            blob=order.compress(pages,permutation,max_order=level);assert order.decompress(blob)==pages
            label=f'order_{i:02}_{level}_{name}';(OUT/(label+'.hporder')).write_bytes(blob)
            rows.append({'name':name,'PPMd_order':level,'archive_bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'exact_inverse':True})
    a=resource.getrusage(resource.RUSAGE_SELF)
    row={'index':i,'role':'development' if i%2==0 else 'confirmation','first_page':first,'page_count':128,
      'input_bytes':sum(map(len,pages)),'input_sha256':hashlib.sha256(b''.join(pages)).hexdigest(),'conditional_pair_probes':pairs,
      'cases':rows,'CPU_lane':lanes.LANE_CPU,'CPU_seconds':a.ru_utime+a.ru_stime-u.ru_utime-u.ru_stime,
      'wall_seconds':time.monotonic()-start,'peak_RSS_KiB':a.ru_maxrss}
    atomic_json(OUT/f'region_{i:02}.json',row);return row
def main():
    global ROOT,OUT,PAGES
    import pyppmd
    from . import cpu_round13_jobs as old
    paths=list(Path('/kaggle/input').rglob('r13_assets.json'));assert len(paths)==1
    ROOT=Path('/root/r14_order');ROOT.mkdir();OUT=Path('/kaggle/working/article-order');OUT.mkdir()
    old.ROOT=ROOT;old.ASSET=paths[0].parent;source=old.raw_source()
    M={'status':'PREFLIGHT','started':time.time(),'regions':[],'worker_count':4,'deletions':[],
       'scope':'paid original raw-page order under PPMd-I, not canonical WRT/transformer history or qualifying Hutter package',
       'pyppmd_version':getattr(pyppmd,'__version__','unknown'),'selection':'freeze one graph from development indices before inspecting confirmation'}
    def save():atomic_json(OUT/'manifest.json',M)
    try:
        save();small=[b'the camel\x00',b'There was a diamond.\xff',b'']
        assert order.decompress(order.compress(small,[2,0,1]))==small
        PAGES=[]
        with source.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
            position=m.find(b'<page>')
            while position>=0:
                end=m.find(b'</page>',position)
                if end<0:break
                end+=7;PAGES.append((position,end));position=m.find(b'<page>',end)
        assert len(PAGES)==243425
        cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4;ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M['status']='FOUR_LANE_ORDER_EXPERIMENT';save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(region,i) for i in range(16)]):M['regions'].append(f.result());save()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_160_PAID_ORDER_CASES',finished=time.time(),worker_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
