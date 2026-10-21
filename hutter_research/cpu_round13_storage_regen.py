"""Fair lossless storage sweep retaining verified native RoPE regeneration."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,multiprocessing as mp,os,resource,subprocess,time,traceback
from . import native_weights,tensor_io,weight_storage,cpu_round13_jobs as lanes
TENSORS=ROOT=OUT=None
REFERENCE=None

def one(task):
    layout,codec=task;start=time.monotonic();u=resource.getrusage(resource.RUSAGE_SELF)
    blob=weight_storage.encode(TENSORS,layout,codec,regenerate=True);restored=weight_storage.decode(blob)
    for name,(dt,a) in TENSORS.items():assert restored[name][0]==dt and restored[name][1].tobytes()==a.tobytes() and restored[name][1].shape==a.shape
    label=layout+'_'+codec;p=OUT/(label+'.hpwt');p.write_bytes(blob)
    native=ROOT/(label+'.tfw');tensor_io.write_tensor_file(native,[(k,*v) for k,v in sorted(restored.items())]);dump=ROOT/(label+'.dump.tfw')
    r=subprocess.run([str(ROOT/'weights_dump'),str(native),str(dump)],capture_output=True,text=True);assert r.returncode==0 and lanes.sha(dump)==REFERENCE
    a=resource.getrusage(resource.RUSAGE_SELF);row={'layout':layout,'codec':codec,'model_bytes':len(blob),'sha256':lanes.sha(p),
        'CPU_lane':lanes.LANE_CPU,'worker_pid':os.getpid(),'wall_seconds':time.monotonic()-start,
        'worker_CPU_seconds':a.ru_utime+a.ru_stime-u.ru_utime-u.ru_stime,'peak_RSS_KiB':a.ru_maxrss,
        'native_all_435_tensor_identity':True,'native_reference_sha256':REFERENCE,
        'saving_per_copy_before_decoder_code':2978039-len(blob),'regeneration_verified_before_omission':True,
        'production_decoder_not_qualified':True}
    lanes.atomic_json(OUT/(label+'.json'),row);return row

def main():
    global TENSORS,ROOT,OUT,REFERENCE
    assets=list(Path('/kaggle/input').rglob('r13_assets.json'));assert len(assets)==1;asset=assets[0].parent
    ROOT=Path('/root/r13_storage_regen');ROOT.mkdir();OUT=Path('/kaggle/working/weight-storage-regeneration');OUT.mkdir()
    M={'id':'R13-weight-storage-regeneration-v1','status':'VERIFYING','started':time.time(),'worker_count':4,'cases':[],
       'deletions':[],'paid_usd':0,'GPU':False,'scope':'finite lossless exact stored-values layouts with native generation; deployment code/resources still must be paid'}
    def save():lanes.atomic_json(OUT/'manifest.json',M)
    try:
        save();meta=json.loads(assets[0].read_text())
        for name,row in meta['files'].items():assert lanes.sha(asset/name)==row['sha256']
        # Load once before fork; retain original dtype/storage values and share
        # the read-only arrays. Heavy tasks run first to reduce the final tail.
        TENSORS=native_weights.read_tensor_file_v3(asset/'original.tfwc3');assert len(TENSORS)==435
        code=Path(__file__).parent/'native_reader'
        r=subprocess.run(['g++','-O2','-std=c++17','-ffp-contract=off','-I',str(code),str(code/'dump.cpp'),str(code/'weights_io.cpp'),str(code/'weights_io_compressed.cpp'),'-o',str(ROOT/'weights_dump')],capture_output=True,text=True);assert r.returncode==0,r.stderr[-2000:]
        p=ROOT/'reference.tfw';r=subprocess.run([str(ROOT/'weights_dump'),str(asset/'original.tfwc3'),str(p)],capture_output=True,text=True);assert r.returncode==0
        REFERENCE=lanes.sha(p);assert REFERENCE=='0e3ee73140eadd68fa5e28758be06c5d68204d057b5d138f413a79223bbc7f44'
        M.update(status='RUNNING_FOUR_LANE_REGENERATION_ARMS',native_reference_sha256=REFERENCE);save()
        cpus=sorted(os.sched_getaffinity(0));assert len(cpus)>=4;cpus=cpus[:4];context=mp.get_context('fork');queue=context.Queue()
        for cpu in cpus:queue.put(cpu)
        tasks=[(l,c) for c in ('lzma','zstd','gzip') for l in weight_storage.LAYOUTS];before=resource.getrusage(resource.RUSAGE_CHILDREN)
        with ProcessPoolExecutor(max_workers=4,mp_context=context,initializer=lanes.initialize_lane,initargs=(queue,)) as pool:
            for f in as_completed([pool.submit(one,t) for t in tasks]):M['cases'].append(f.result());save()
        a=resource.getrusage(resource.RUSAGE_CHILDREN);M.update(status='COMPLETE_FOUR_LANE_REGENERATION_ARMS',finished=time.time(),
          all_worker_and_descendant_CPU_seconds=a.ru_utime+a.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
