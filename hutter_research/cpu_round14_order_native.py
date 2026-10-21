"""Repaired 160-case paid order sweep; development frozen before confirmation."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,mmap,multiprocessing as mp,os,random,resource,time,traceback
from .cpu_round13_jobs import atomic_json,initialize_lane
from . import cpu_round13_jobs as lanes,article_order_native as order
ROOT=OUT=PAGES=DEADLINE=None

def total_cpu(who):
    r=resource.getrusage(who);return r.ru_utime+r.ru_stime

def region(i):
    started=time.monotonic();before=total_cpu(resource.RUSAGE_SELF)+total_cpu(resource.RUSAGE_CHILDREN)
    scratch_before=dict(order.SCRATCH);first=(2*i+1)*len(PAGES)//32;pages=[]
    with (ROOT/'original_enwik9.bin').open('rb') as f:
        for a,b in PAGES[first:first+128]:f.seek(a);pages.append(f.read(b-a))
    assert len(pages)==128
    orders,pairs=order.graph_orders(pages);r=list(range(128));random.Random(140008+i).shuffle(r)
    orders={'original':list(range(128)),'reverse':list(range(127,-1,-1)),'random':r,**orders};rows=[]
    for level in (8,16):
        for name,permutation in orders.items():
            assert time.monotonic()<DEADLINE,'registered job deadline'
            blob=order.compress(pages,permutation,max_order=level)
            assert order.decompress(blob)==pages
            label=f'order_{i:02}_{level}_{name}';(OUT/(label+'.hporder')).write_bytes(blob)
            rows.append({'name':name,'PPMd_order':level,'archive_bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'exact_inverse':True})
    elapsed=time.monotonic()-started
    row={'index':i,'role':'development' if i%2==0 else 'confirmation','first_page':first,'page_count':128,
         'input_bytes':sum(map(len,pages)),'input_sha256':hashlib.sha256(b''.join(pages)).hexdigest(),'conditional_pair_probes':pairs,
         'cases':rows,'CPU_lane':lanes.LANE_CPU,'CPU_seconds':total_cpu(resource.RUSAGE_SELF)+total_cpu(resource.RUSAGE_CHILDREN)-before,
         'wall_seconds':elapsed,'peak_RSS_KiB_self':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
         'peak_RSS_KiB_codec_children':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
         'temporary_scratch_created_and_removed':{k:order.SCRATCH[k]-scratch_before[k] for k in scratch_before}}
    atomic_json(OUT/f'region_{i:02}.json',row);return row

def freeze(development):
    assert {r['index'] for r in development}==set(range(0,16,2))
    names=('rare_word_graph','conditional_ppmd_graph');sums={n:0 for n in names}
    for r in development:
        for level in (8,16):
            rows={q['name']:q['archive_bytes'] for q in r['cases'] if q['PPMd_order']==level}
            for n in names:sums[n]+=rows['original']-rows[n]
    selected=min(names,key=lambda n:(-sums[n],n))
    return {'selected_graph':selected,'development_gain_bytes_sum_of_both_fixed_orders':sums,
            'protocol':'Choose one graph by summed gain across both registered context orders on even indices; evaluate both orders separately on odd indices. No confirmation outcome opened before this freeze.',
            'development_sha256':hashlib.sha256(json.dumps(sorted(development,key=lambda r:r['index']),sort_keys=True).encode()).hexdigest(),'frozen':time.time()}

def main():
    global ROOT,OUT,PAGES,DEADLINE
    from . import cpu_round13_jobs as old
    paths=list(Path('/kaggle/input').rglob('r13_assets.json'));assert len(paths)==1
    ROOT=Path('/root/r14_order_native_v2');ROOT.mkdir();OUT=Path('/kaggle/working/article-order-native');OUT.mkdir()
    DEADLINE=time.monotonic()+10.3*3600
    M={'status':'NATIVE_BACKEND_PREFLIGHT','started':time.time(),'regions':[],'worker_count':4,'deletions':[],
       'scope':'paid original raw-page order under native PPMd-H, not canonical WRT/transformer history or qualifying Hutter package',
       'backend':order.backend_identity(),'source':'new serialized HPOR14H0; failed I/H Python streams never scored'}
    def save():atomic_json(OUT/'manifest.json',M)
    try:
        save();small=[b'the camel\x00',b'There was a diamond.\xff',b'',bytes(range(256))*100]
        for level in (8,16):assert order.decompress(order.compress(small,[2,0,3,1],level))==small
        old.ROOT=ROOT;old.ASSET=paths[0].parent;source=old.raw_source()
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
        before=total_cpu(resource.RUSAGE_CHILDREN)
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for role,ids in [('DEVELOPMENT',range(0,16,2)),('CONFIRMATION',range(1,16,2))]:
                M['status']='FOUR_LANE_'+role;save()
                for f in as_completed([pool.submit(region,i) for i in ids]):M['regions'].append(f.result());save()
                if role=='DEVELOPMENT':
                    M['selection']=freeze(M['regions']);atomic_json(OUT/'selection.json',M['selection']);save()
        M.update(status='COMPLETE_160_PAID_NATIVE_PPMD_ORDER_CASES',finished=time.time(),worker_CPU_seconds=total_cpu(resource.RUSAGE_CHILDREN)-before);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED_NO_SELECTION_FROM_PARTIAL_CASES',error=repr(e),traceback=traceback.format_exc());save();raise
