from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,multiprocessing as mp,os,re,resource,subprocess,time,traceback
from . import weight_storage as w,native_weights,tensor_io,group_weight_storage as g
from .cpu_round13_jobs import atomic_json,initialize_lane,sha
from . import cpu_round13_jobs as lanes
TENSORS=ROOT=OUT=None
def select(task):
    partition,key,names=task;t={n:TENSORS[n] for n in names};start=time.monotonic();u=resource.getrusage(resource.RUSAGE_SELF)
    best=None;rows=[]
    for layout in w.LAYOUTS:
        for codec in w.CODECS:
            blob=w.encode(t,layout,codec);rows.append({'layout':layout,'codec':codec,'bytes':len(blob)})
            candidate=(len(blob),layout,codec)
            if best is None or candidate<best[0]:best=(candidate,blob)
    assert w.tensor_digest(w.decode(best[1]))==w.tensor_digest(t)
    label=hashlib.sha256((partition+'|'+key).encode()).hexdigest()[:24]
    (ROOT/(label+'.hpwt')).write_bytes(best[1]);a=resource.getrusage(resource.RUSAGE_SELF)
    row={'partition':partition,'key':key,'names':names,'label':label,'alternatives':rows,'selected':best[0],
      'archive_sha256':hashlib.sha256(best[1]).hexdigest(),'CPU_lane':lanes.LANE_CPU,
      'CPU_seconds':a.ru_utime+a.ru_stime-u.ru_utime-u.ru_stime,'wall_seconds':time.monotonic()-start}
    atomic_json(OUT/(label+'.json'),row);return row
def main():
    global ROOT,OUT,TENSORS
    paths=list(Path('/kaggle/input').rglob('r13_assets.json'));assert len(paths)==1;asset=paths[0].parent
    ROOT=Path('/root/r14_group_storage');ROOT.mkdir();OUT=Path('/kaggle/working/group-storage');OUT.mkdir()
    M={'status':'LOADING','started':time.time(),'groups':[],'containers':[],'worker_count':4,'deletions':[]}
    def save():atomic_json(OUT/'manifest.json',M)
    try:
        save();assert sha(asset/'original.tfwc3')=='948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'
        all_tensors=native_weights.read_tensor_file_v3(asset/'original.tfwc3');schema,_=w.representation(all_tensors,'plain',True)
        deferred=[r for r in schema if r[3] in ('rope_sin','rope_cos')];excluded={r[0] for r in deferred}
        TENSORS={n:v for n,v in all_tensors.items() if n not in excluded};tasks=[]
        for partition in ('whole','dtype','layer','tensor'):
            groups={}
            for name,(dt,array) in TENSORS.items():
                if partition=='whole':key='all'
                elif partition=='dtype':key=str(dt)
                elif partition=='tensor':key=name
                else:
                    match=re.search(r'(?:layers?|blocks?)\.(\d+)\.',name);key='block_'+match[1] if match else 'other_'+str(dt)
                groups.setdefault(key,[]).append(name)
            tasks.extend((partition,k,sorted(v)) for k,v in sorted(groups.items()))
        code=Path(__file__).parent/'native_reader';binary=ROOT/'weights_dump'
        r=subprocess.run(['g++','-O2','-std=c++17','-ffp-contract=off','-I',str(code),str(code/'dump.cpp'),str(code/'weights_io.cpp'),str(code/'weights_io_compressed.cpp'),'-o',str(binary)],capture_output=True,text=True)
        assert r.returncode==0,r.stderr[-2000:]
        tasks.sort(key=lambda t:-sum(TENSORS[n][1].nbytes for n in t[2]))
        cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4;ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M.update(status='FOUR_LANE_GROUP_SELECTION',group_count=len(tasks));save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(select,t) for t in tasks]):M['groups'].append(f.result());save()
        for partition in ('whole','dtype','layer','tensor'):
            rows=sorted([r for r in M['groups'] if r['partition']==partition],key=lambda r:r['key'])
            groups=[(ROOT/(r['label']+'.hpwt')).read_bytes() for r in rows]
            blob=g.pack(groups,deferred,w.tensor_digest(all_tensors));restored=g.unpack(blob)
            assert w.tensor_digest(restored)==w.tensor_digest(all_tensors)
            p=OUT/(partition+'.hpwg');p.write_bytes(blob)
            intermediate=ROOT/(partition+'.tfw');dump=ROOT/(partition+'.dump')
            tensor_io.write_tensor_file(intermediate,[(k,*v) for k,v in sorted(restored.items())])
            r=subprocess.run([str(binary),str(intermediate),str(dump)],capture_output=True,text=True);assert r.returncode==0
            assert sha(dump)=='0e3ee73140eadd68fa5e28758be06c5d68204d057b5d138f413a79223bbc7f44'
            M['containers'].append({'partition':partition,'groups':len(groups),'bytes':len(blob),'sha256':sha(p),'original_bytes':2978039,
               'saving_per_copy_before_code':2978039-len(blob),'all_435_native_tensors_identical':True});save()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_FINITE_GROUP_OPTIMA',finished=time.time(),worker_and_descendant_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
           scope='independent minimum blob within 18 declared alternatives per fixed group; global architecture/decoder packaging not qualified');save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
