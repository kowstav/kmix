"""Four-lane actual native archives, with a neutral trajectory gate first."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import gzip,hashlib,json,multiprocessing as mp,os,resource,shutil,subprocess,time,traceback
import numpy as np
from .cpu_round13_jobs import atomic_json,initialize_lane,sha
from . import cpu_round13_jobs as lanes
ASSET=HEAD=ROOT=OUT=None
DEADLINE=None

def run(args,work,env,label):
    start=time.monotonic()
    with (work/(label+'.log')).open('xb') as f:
        p=subprocess.Popen(args,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT)
        stop=None
        while True:
            pid,status,u=os.wait4(p.pid,os.WNOHANG)
            if pid:p.returncode=os.waitstatus_to_exitcode(status);break
            if time.monotonic()>DEADLINE:stop='declared notebook deadline';p.terminate()
            time.sleep(.5)
    return {'exit':p.returncode,'wall_seconds':time.monotonic()-start,'CPU_user_seconds':u.ru_utime,
        'CPU_system_seconds':u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'stop':stop}

def archive_case(region,mode,preflight=False,expected_bytes=None):
    meta=json.loads((ASSET/'r13_assets.json').read_text());r=meta['regions'][region]
    raw=(ASSET/r['file']).read_bytes();raw=raw[:16384] if preflight else raw
    if expected_bytes is not None and len(raw)!=expected_bytes:
        raise ValueError(f'actual native input length {len(raw)} differs from declared {expected_bytes}; preflight={preflight}')
    label=f"{'preflight' if preflight else 'native'}_{region:02}_{mode}";work=ROOT/label;work.mkdir()
    (work/'input.bin').write_bytes(raw);(work/'.dict').symlink_to(ASSET/'english.dic')
    binary=ROOT/'pinned_cmix' if mode=='pinned' else ROOT/f'cmix_head_{mode}'
    env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))}
    env.update(LAB_RAW='1',LAB_DICT=str(ASSET/'english.dic'),LAB_VOCAB=str(ASSET/'vocab.bm'),LAB_KEEP_TEMP='1',OMP_NUM_THREADS='1')
    row={'mode':mode,'region':region,'offset':r['offset'],'bytes':len(raw),'CPU_lane':lanes.LANE_CPU,
         'worker_pid':os.getpid(),'binary_sha256':sha(binary),'status':'ENCODING'}
    record=OUT/(label+'.json');atomic_json(record,row)
    row['encode']=run([str(binary),'-n','--transformer',str(ASSET/'original.tfwc3'),'input.bin','archive.cmx'],work,
                     {**env,'LAB_BITTRACE':str(work/'probabilities.u16')},'encode')
    for name in ('encode.log','archive.cmx'):
        if (work/name).exists():shutil.copyfile(work/name,OUT/(label+'_'+name))
    assert row['encode']['exit']==0,(label,row['encode'])
    row['status']='INDEPENDENT_DECODE';atomic_json(record,row)
    row['decode']=run([str(binary),'-d','--transformer',str(ASSET/'original.tfwc3'),'archive.cmx','restored.bin'],work,env,'decode')
    shutil.copyfile(work/'decode.log',OUT/(label+'_decode.log'))
    assert row['decode']['exit']==0 and (work/'restored.bin').read_bytes()==raw,(label,'inverse failed')
    p=work/'probabilities.u16';assert p.stat().st_size==16*len(raw),'coded target/trace length differs'
    total=warm=0.;warmup=0 if preflight else r['warmup_bytes']
    with p.open('rb') as f:
        for offset in range(0,len(raw),262144):
            n=min(262144,len(raw)-offset);q=np.frombuffer(f.read(16*n),dtype='<u2').astype('float64')
            y=np.unpackbits(np.frombuffer(raw[offset:offset+n],dtype='u1'));assert q.min()>0
            costs=-np.log2(np.where(y,q,65536-q)/65536);total+=float(costs.sum())
            begin=max(0,warmup-offset)*8
            if begin<len(costs):warm+=float(costs[begin:].sum())
    with p.open('rb') as f,gzip.open(OUT/(label+'_probabilities.u16.gz'),'wb',6) as g:shutil.copyfileobj(f,g)
    row.update(status='COMPLETE_INDEPENDENT_NATIVE_ARCHIVE',archive_bytes=(work/'archive.cmx').stat().st_size,
       archive_sha256=sha(work/'archive.cmx'),probabilities_sha256=sha(p),input_sha256=hashlib.sha256(raw).hexdigest(),
       exact_independent_inverse=True,all_target_bits=total,warm_target_bits=warm,warmup_bytes=warmup,
       no_global_history_claim=True,production_build_qualification=False)
    atomic_json(record,row);return row

def preflight(mode):return archive_case(0,mode,True)
def region_cases(index):
    modes=['pinned',0,1,2];shift=(index//2)%4;modes=modes[shift:]+modes[:shift]
    rows=[archive_case(index,mode) for mode in modes];by={r['mode']:r for r in rows}
    assert by['pinned']['archive_sha256']==by[0]['archive_sha256'],'rebuilt neutral regional archive differs'
    assert by['pinned']['probabilities_sha256']==by[0]['probabilities_sha256'],'rebuilt neutral regional trajectory differs'
    return {'region':index,'CPU_lane':lanes.LANE_CPU,'neutral_trajectory_exact':True,'cases':rows,
       'candidate_gains':[{'mode':m,'actual_whole_archive_gain_bytes':by['pinned']['archive_bytes']-by[m]['archive_bytes'],
         'warm_logloss_gain_bytes':(by['pinned']['warm_target_bits']-by[m]['warm_target_bits'])/8} for m in (1,2)]}

def main():
    global ASSET,HEAD,ROOT,OUT,DEADLINE
    assets=list(Path('/kaggle/input').rglob('r13_assets.json'));heads=list(Path('/kaggle/input').rglob('r13_native_assets.json'))
    assert len(assets)==len(heads)==1
    ASSET=assets[0].parent;HEAD=heads[0].parent;ROOT=Path('/root/r13_native_archive');ROOT.mkdir();OUT=Path('/kaggle/working/native-final-head');OUT.mkdir()
    DEADLINE=time.monotonic()+10.3*3600;cpus=sorted(os.sched_getaffinity(0));assert len(cpus)>=4;cpus=cpus[:4]
    M={'id':'R13-native-final-head-v1','status':'VERIFYING_ASSETS','started':time.time(),'worker_count':4,
       'worker_CPU_lanes':cpus,'preflight_cases':[],'regions':[],'deletions':[],'paid_usd':0,'GPU':False,
       'protocol':{'regions':[0,2,4,6],'bytes_per_region':3145728,'warmup_bytes_per_region':2097152,
          'arms':['pinned',0,1,2],'mode_0':'rebuilt neutral','mode_1':'integer full_250','mode_2':'four-expert fixed-share guard',
          'scope':'matched regional histories; actual independently decoded native archives; no complete-package qualification'}}
    def save():atomic_json(OUT/'manifest.json',M)
    try:
        save()
        for folder,manifest in ((ASSET,assets[0]),(HEAD,heads[0])):
            for name,row in json.loads(manifest.read_text())['files'].items():assert (folder/name).stat().st_size==row['bytes'] and sha(folder/name)==row['sha256']
        for mode in (0,1,2):shutil.copyfile(HEAD/f'cmix_head_{mode}',ROOT/f'cmix_head_{mode}');(ROOT/f'cmix_head_{mode}').chmod(0o700)
        shutil.copyfile(ASSET/'native_cmix',ROOT/'pinned_cmix');(ROOT/'pinned_cmix').chmod(0o700)
        context=mp.get_context('fork');queue=context.Queue()
        for cpu in cpus:queue.put(cpu)
        before=resource.getrusage(resource.RUSAGE_CHILDREN)
        with ProcessPoolExecutor(max_workers=4,mp_context=context,initializer=initialize_lane,initargs=(queue,)) as pool:
            M['status']='FOUR_LANE_NATIVE_PARITY_PREFLIGHT';save()
            for f in as_completed([pool.submit(preflight,m) for m in ('pinned',0,1,2)]):M['preflight_cases'].append(f.result());save()
            rows={r['mode']:r for r in M['preflight_cases']}
            assert rows['pinned']['archive_sha256']==rows[0]['archive_sha256'] and rows['pinned']['probabilities_sha256']==rows[0]['probabilities_sha256'],'neutral preflight differs'
            M['status']='RUNNING_FOUR_LANE_ACTUAL_NATIVE_REGIONS';save()
            for f in as_completed([pool.submit(region_cases,i) for i in (0,2,4,6)]):M['regions'].append(f.result());save()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_FOUR_LANE_NATIVE_FINITE_ARMS',finished=time.time(),
           all_worker_and_descendant_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
