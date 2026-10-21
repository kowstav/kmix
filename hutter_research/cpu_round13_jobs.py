"""Four-worker CPU jobs with immutable assets and separately scoped evidence."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import gzip,hashlib,json,multiprocessing as mp,os,resource,shutil,struct,subprocess,sys,time,traceback,zipfile
import numpy as np

ASSET=None
ROOT=None
OUT=None
DEADLINE=None
LANE_CPU=None

def initialize_lane(queue):
    global LANE_CPU
    LANE_CPU=queue.get(timeout=10)
    os.sched_setaffinity(0,{LANE_CPU})

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while b:=f.read(1<<22):h.update(b)
    return h.hexdigest()

def atomic_json(path,value):
    p=Path(path);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(value,indent=2));q.replace(p)

def run_child(args,cwd,env,label,consumer=None):
    started=time.monotonic()
    with (Path(cwd)/(label+'.log')).open('xb') as log:
        p=subprocess.Popen(args,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT)
        stop=None
        while True:
            pid,status,u=os.wait4(p.pid,os.WNOHANG)
            if pid:
                p.returncode=os.waitstatus_to_exitcode(status);break
            if time.monotonic()>DEADLINE:stop='deadline'
            if consumer is not None and consumer.poll() not in (None,0):stop='consumer failed'
            if stop is not None:p.terminate()
            time.sleep(1)
    row={'exit':p.returncode,'wall_seconds':time.monotonic()-started,'CPU_user_seconds':u.ru_utime,
         'CPU_system_seconds':u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'stop_reason':stop}
    return row

def native_region(task):
    i,_=task;cpu=LANE_CPU
    meta=json.loads((ASSET/'r13_assets.json').read_text());r=meta['regions'][i]
    work=ROOT/f'region_{i:02}';work.mkdir(exist_ok=False)
    shutil.copyfile(ASSET/r['file'],work/'input.bin');(work/'.dict').symlink_to(ASSET/'english.dic')
    binary=ROOT/'cmix';done=work/'encoder.done';result_file=OUT/f'region_{i:02}.json'
    row={'region':r,'cpu':cpu,'worker_pid':os.getpid(),'status':'ENCODING','deletions':[]}
    atomic_json(result_file,row)
    env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))}
    env.update(LAB_RAW='1',LAB_DICT=str(ASSET/'english.dic'),LAB_VOCAB=str(ASSET/'vocab.bm'),LAB_KEEP_TEMP='1',OMP_NUM_THREADS='1')
    traces={'LAB_COST':'cost.f32','LAB_BITTRACE':'final_p.u16','LAB_STAGETRACE':'stage.f32','LAB_HIDDENTRACE':'hidden.q8'}
    observer={k:str(work/v) for k,v in traces.items()}
    with (work/'consumer.log').open('xb') as log:
        c=subprocess.Popen([str(ROOT/'consumer'),str(work/'input.bin'),str(work/'final_p.u16'),str(work/'stage.f32'),
            str(work/'hidden.q8'),str(done),str(OUT/f'region_{i:02}.jsonl'),'524288',str(r['offset'])],stdout=log,stderr=subprocess.STDOUT)
        row['encode']=run_child([str(binary),'-n','--transformer',str(ASSET/'original.tfwc3'),'input.bin','out.cmx'],work,{**env,**observer},'encode',c)
        done.write_text('encoder exited')
        try:code=c.wait(timeout=90)
        except subprocess.TimeoutExpired:c.terminate();code=c.wait(timeout=30)
    row['consumer_exit']=code
    assert row['encode']['exit']==0 and code==0,(row,'consumer or encoder failed')
    n=r['bytes'];sizes={'final_p.u16':16*n,'stage.f32':12+608*n,'hidden.q8':193*n,'cost.f32':4*n}
    for name,size in sizes.items():assert (work/name).stat().st_size==size,name
    records=[json.loads(line) for line in (OUT/f'region_{i:02}.jsonl').read_text().splitlines()]
    summary=records[-1];assert summary['type']=='summary' and summary['bytes']==n
    assert summary['identity_mismatch_bits']==summary['memory_zero_mismatch_bits']==0
    costs=np.fromfile(work/'cost.f32',dtype='<f4').astype('float64')
    row['baseline_minus_cost_bits']=float(summary['baseline_bits']-costs.sum())
    assert abs(row['baseline_minus_cost_bits'])<.001,'native trace alignment failed'
    row['status']='INDEPENDENT_DECODE';atomic_json(result_file,row)
    row['decode']=run_child([str(binary),'-d','--transformer',str(ASSET/'original.tfwc3'),'out.cmx','decoded.bin'],work,env,'decode')
    assert row['decode']['exit']==0 and sha(work/'decoded.bin')==sha(work/'input.bin'),'independent native decode failed'
    shutil.copyfile(work/'out.cmx',OUT/f'region_{i:02}.cmx')
    with (work/'cost.f32').open('rb') as f,gzip.open(OUT/f'region_{i:02}.cost.f32.gz','wb',6) as g:shutil.copyfileobj(f,g)
    row.update(status='COMPLETE_NATIVE_BASELINE_AND_CORRECTED_REPLAY',archive_bytes=(work/'out.cmx').stat().st_size,
      archive_sha256=sha(work/'out.cmx'),input_sha256=sha(work/'input.bin'),independent_decode_exact=True,
      replay_only=True,summary=summary,
      warm_windows=[v for v in records if v.get('type')=='window' and v['history_bytes']>=r['warmup_bytes']],
      no_full_file_state_claim=True)
    atomic_json(result_file,row);return row

def raw_source():
    p=ROOT/'original_enwik9.bin'
    if not p.exists():
        with zipfile.ZipFile(ASSET/'original_enwik9.zip.dat') as z:
            names=[i for i in z.infolist() if i.file_size==1000000000];assert len(names)==1
            with z.open(names[0]) as f,p.open('xb') as g:shutil.copyfileobj(f,g,1<<22)
        assert sha(p)=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
    return p

GRAMMAR_ARMS=[('unigram',0),('markov',4),('coarse_right',1),('coarse_right',4),
              ('coarse_wrong',1),('coarse_wrong',4),('coarse_left',1),('coarse_left',4),('bag',0)]

def grammar_case(task):
    from .constructor_codec import encode,decode,inspect_sizes
    index,mode,alpha,_=task;cpu=LANE_CPU
    source=ROOT/'original_enwik9.bin';offset=(2*index+1)*1000000000//32
    with source.open('rb') as f:f.seek(offset);raw=f.read(1048576)
    start=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF)
    blob=encode(raw,mode,alpha);decoded=decode(blob);assert decoded==raw
    after=resource.getrusage(resource.RUSAGE_SELF)
    label=f'grammar_{index:02}_{mode}_{alpha}';(OUT/(label+'.hpctor')).write_bytes(blob)
    baseline=len(gzip.compress(raw,mtime=0))
    row={'index':index,'offset':offset,'bytes':len(raw),'mode':mode,'alpha':alpha,
       'role':'development' if index%2==0 else 'confirmation','archive_bytes':len(blob),
       'archive_sha256':hashlib.sha256(blob).hexdigest(),'original_sha256':hashlib.sha256(raw).hexdigest(),
       'gzip_baseline_bytes':baseline,'gain_bytes':baseline-len(blob),'channel_bytes':inspect_sizes(blob),
       'exact_independent_inverse':True,'cpu':cpu,'wall_seconds':time.monotonic()-start,
       'CPU_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
       'peak_RSS_KiB':after.ru_maxrss,'proxy':True}
    atomic_json(OUT/(label+'.json'),row);return row

def storage_case(task):
    from . import native_weights,tensor_io,weight_storage
    layout,codec,_=task;cpu=LANE_CPU
    tensors=native_weights.read_tensor_file_v3(ASSET/'original.tfwc3')
    # Native reader promotes free BF16 float tensors exactly; scales remain BF16.
    tensors={k:(2,(a.astype('<u4')<<16).view('<f4')) if dt==1 and not k.endswith('.scale') else (dt,a)
             for k,(dt,a) in tensors.items()}
    assert len(tensors)==435
    started=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF)
    blob=weight_storage.encode(tensors,layout,codec);restored=weight_storage.decode(blob)
    for name,(dt,array) in tensors.items():
        actual_dt,actual=restored[name];assert dt==actual_dt and array.shape==actual.shape and array.tobytes()==actual.tobytes(),name
    label='storage_'+layout+'_'+codec;p=OUT/(label+'.hpwt');p.write_bytes(blob)
    native=ROOT/(label+'.tfw');tensor_io.write_tensor_file(native,[(k,*v) for k,v in sorted(restored.items())])
    # Independent original C++ reader checks every restored value against the
    # canonical sorted native dump of the unmodified compressed source.
    dumped=ROOT/(label+'.dump.tfw')
    result=subprocess.run([str(ROOT/'weights_dump'),str(native),str(dumped)],capture_output=True,text=True)
    assert result.returncode==0 and sha(dumped)==json.loads((ROOT/'native_reference.json').read_text())['sha256']
    after=resource.getrusage(resource.RUSAGE_SELF)
    row={'layout':layout,'codec':codec,'model_bytes':len(blob),'model_sha256':sha(p),'cpu':cpu,
       'saving_per_copy_before_decoder_code':(ASSET/'original.tfwc3').stat().st_size-len(blob),
       'all_435_native_tensors_equal':True,'native_reference_sha256':sha(dumped),
       'wall_seconds':time.monotonic()-started,'CPU_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
       'peak_RSS_KiB':after.ru_maxrss,'deployment_decoder_not_qualified':True}
    atomic_json(OUT/(label+'.json'),row);return row

def full_chunk(task):
    from .constructor_codec import encode,decode
    index,policy,_=task;cpu=LANE_CPU;size=4*1048576
    with (ROOT/'original_enwik9.bin').open('rb') as f:f.seek(index*size);raw=f.read(size)
    start=time.monotonic();u=resource.getrusage(resource.RUSAGE_SELF)
    if policy=='gzip':blob=gzip.compress(raw,mtime=0);restored=gzip.decompress(blob)
    elif policy=='zstd':
        import zstandard as zstd
        blob=zstd.ZstdCompressor(level=9,threads=0).compress(raw);restored=zstd.ZstdDecompressor().decompress(blob)
    else:
        mode,alpha=('markov',4) if policy=='markov' else ('coarse_right',1)
        blob=encode(raw,mode,alpha);restored=decode(blob)
    assert restored==raw
    label=f'full_{policy}_{index:03}';(ROOT/(label+'.part')).write_bytes(blob)
    a=resource.getrusage(resource.RUSAGE_SELF)
    return {'chunk':index,'policy':policy,'input_bytes':len(raw),'archive_bytes':len(blob),
       'input_sha256':hashlib.sha256(raw).hexdigest(),'archive_sha256':hashlib.sha256(blob).hexdigest(),
       'CPU_seconds':a.ru_utime+a.ru_stime-u.ru_utime-u.ru_stime,'wall_seconds':time.monotonic()-start,'cpu':cpu,
       'independent_inverse_exact':True}

def main(job):
    global ASSET,ROOT,OUT,DEADLINE
    found=list(Path('/kaggle/input').rglob('r13_assets.json'));assert len(found)==1,found
    ASSET=found[0].parent;ROOT=Path('/root/hp_r13')/job;ROOT.mkdir(parents=True,exist_ok=False)
    OUT=Path('/kaggle/working')/job;OUT.mkdir(exist_ok=False)
    DEADLINE=time.monotonic()+10.3*3600
    M={'id':'R13-'+job,'status':'VERIFYING_ASSETS','started':time.time(),'GPU':False,'paid_usd':0,'deletions':[],
       'worker_count':4,'cpu_affinity':sorted(os.sched_getaffinity(0)),'cases':[],
       'limits':'Finite experiments; no complete native full-file state or production qualification is claimed.'}
    def save():atomic_json(OUT/'manifest.json',M)
    try:
        save();meta=json.loads(found[0].read_text())
        for name,info in meta['files'].items():assert (ASSET/name).stat().st_size==info['bytes'] and sha(ASSET/name)==info['sha256'],name
        M['all_assets_SHA_verified']=True
        cpus=sorted(os.sched_getaffinity(0));assert len(cpus)>=4,'four authorized worker CPUs unavailable'
        cpus=cpus[:4];context=mp.get_context('fork')
        if job in ('warm-development','warm-confirmation'):
            shutil.copyfile(ASSET/'native_cmix',ROOT/'cmix');(ROOT/'cmix').chmod(0o700)
            code=Path(__file__).parent
            r=subprocess.run(['g++','-O2','-std=c++17','-fno-fast-math','-ffp-contract=off',str(code/'stream_mixer_v3.cpp'),'-o',str(ROOT/'consumer')],capture_output=True,text=True)
            assert r.returncode==0,r.stderr[-3000:]
            indices=range(0,8) if job=='warm-development' else range(8,16)
            tasks=[(i,cpus[k%4]) for k,i in enumerate(indices)];function=native_region
            M['protocol']={'regions':list(indices),'warmup_bytes_per_region':2*1048576,'native_bytes_per_region':3*1048576,
               'arms':12,'confirmation_embargo':'choose a candidate from development before opening confirmation outcomes',
               'regime':'matched regional warm states; these are not true global-history checkpoints'}
        elif job=='constructor-descendants':
            raw_source();tasks=[(i,m,a,cpus[k%4]) for k,(i,m,a) in enumerate((i,m,a) for i in range(16) for m,a in GRAMMAR_ARMS)]
            function=grammar_case;M['protocol']={'groups':16,'group_bytes':1048576,'arms':GRAMMAR_ARMS,'selection':'even groups develop; odd groups confirm; freeze selection before reading confirmation'}
        elif job=='weight-storage':
            from . import native_weights,tensor_io
            code=Path(__file__).parent/'native_reader'
            r=subprocess.run(['g++','-O2','-std=c++17','-ffp-contract=off','-I',str(code),str(code/'dump.cpp'),str(code/'weights_io.cpp'),str(code/'weights_io_compressed.cpp'),'-o',str(ROOT/'weights_dump')],capture_output=True,text=True)
            assert r.returncode==0,r.stderr[-2000:]
            p=ROOT/'reference.tfw';r=subprocess.run([str(ROOT/'weights_dump'),str(ASSET/'original.tfwc3'),str(p)],capture_output=True,text=True)
            assert r.returncode==0
            atomic_json(ROOT/'native_reference.json',{'sha256':sha(p)})
            tasks=[(l,c,cpus[k%4]) for k,(l,c) in enumerate((l,c) for l in ('plain','planes','zigzag','nibble','transpose','xor') for c in ('gzip','lzma','zstd'))]
            function=storage_case;M['protocol']={'arms':18,'inference_values_changed':False,'native_reference_sha256':sha(p)}
        elif job=='full-corpus-factorization':
            source=raw_source();n=(source.stat().st_size+4*1048576-1)//(4*1048576)
            policies=('gzip','zstd','markov','coarse_right')
            tasks=[(i,p,cpus[k%4]) for k,(i,p) in enumerate((i,p) for i in range(n) for p in policies)]
            function=full_chunk;M['protocol']={'original_bytes':1000000000,'chunk_bytes':4*1048576,'policies':policies,
                'scope':'complete original corpus, paid chunked reversible proxy; same reset boundaries for every policy'}
        else:raise ValueError(job)
        M.update(status='RUNNING_FOUR_CPU_WORKERS',task_count=len(tasks));save()
        queue=context.Queue()
        for cpu in cpus:queue.put(cpu)
        with ProcessPoolExecutor(max_workers=4,mp_context=context,initializer=initialize_lane,initargs=(queue,)) as pool:
            futures=[pool.submit(function,t) for t in tasks]
            for future in as_completed(futures):M['cases'].append(future.result());save()
        if job=='full-corpus-factorization':
            M['full_archives']=[]
            for policy in policies:
                target=OUT/(policy+'.hpfull');rows=sorted([r for r in M['cases'] if r['policy']==policy],key=lambda r:r['chunk'])
                with target.open('xb') as f:
                    f.write(b'HPFULL13'+struct.pack('<QI',1000000000,n))
                    for row in rows:
                        blob=(ROOT/f"full_{policy}_{row['chunk']:03}.part").read_bytes()
                        assert hashlib.sha256(blob).hexdigest()==row['archive_sha256']
                        f.write(struct.pack('<II',row['input_bytes'],len(blob)));f.write(blob)
                M['full_archives'].append({'policy':policy,'archive_bytes':target.stat().st_size,'archive_sha256':sha(target),
                   'input_bytes_exactly_reconstructed':sum(r['input_bytes'] for r in rows),'chunks_independently_decoded':len(rows)})
                assert sum(r['input_bytes'] for r in rows)==1000000000
        M.update(status='COMPLETE_FOUR_LANE_FINITE_CPU_JOB',finished=time.time());save()
    except BaseException as e:
        M.update(status='FAIL',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
