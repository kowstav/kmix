from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,os,shutil,sys,time,traceback,zipfile,multiprocessing as mp,resource
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_native_cpu_preflight');OUT=W/'native_cpu_preflight_v1'
M={'status':'RESTORING_FROZEN_CODE','started':time.time(),'cases':[],'workers':4,'deletions':[],'GPU':False,'paid_usd':0}
def save():(OUT/'manifest.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not R.exists() and not OUT.exists();R.mkdir();OUT.mkdir();save()
    try:
        code=R/'code';code.mkdir()
        with zipfile.ZipFile(W/'sources_v2.zip.dat') as z:
            for e in json.loads(z.read('source_manifest.json')):
                p=(code/e['path']).resolve();assert p.is_relative_to(code);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        sys.path.insert(0,str(code));from hutter_research import cpu_round13_native as n
        from hutter_research.cpu_round13_jobs import initialize_lane
        build=json.loads((W/'native_cpu_build_v2.json').read_text());assert build['status']=='COMPLETE_AWAITING_NATIVE_PARITY'
        asset=R/'asset';asset.mkdir();base=Path('/kaggle/working')
        files={'native_cmix':base/'hp_round8/native_stage_trace_v1/tree/cmix','original.tfwc3':base/'hp_round7/lex_audit/lex_h1_run11.tfwc2','english.dic':base/'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic','vocab.bm':base/'hp_round7/preserved/data/vocab.bm'}
        wanted={'native_cmix':'17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa','original.tfwc3':'948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71','english.dic':'4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a','vocab.bm':'3e7f8c043939ccba8675b3a260f65a665bc34acac883a7316cc50fecfd7d36b5'}
        for name,p in files.items():assert sha(p)==wanted[name];shutil.copyfile(p,asset/name)
        source=base/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt';assert sha(source)=='7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce'
        with source.open('rb') as f:f.seek(32000000);raw=f.read(16384)
        (asset/'region_00.bin').write_bytes(raw);(asset/'r13_assets.json').write_text(json.dumps({'regions':[{'file':'region_00.bin','offset':32000000,'bytes':16384,'warmup_bytes':0}]}))
        n.ASSET=asset;n.ROOT=R/'work';n.ROOT.mkdir();n.OUT=OUT;n.DEADLINE=time.monotonic()+15*60
        shutil.copyfile(asset/'native_cmix',n.ROOT/'pinned_cmix');(n.ROOT/'pinned_cmix').chmod(0o700)
        for e in build['builds']:
            p=W/'native_cpu_binaries_v2'/('cmix_'+e['name']);assert sha(p)==e['sha256'];dst=n.ROOT/('cmix_head_'+e['name']);shutil.copyfile(p,dst);dst.chmod(0o700)
        ctx=mp.get_context('fork');q=ctx.Queue();cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4
        for c in cpus:q.put(c)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M['status']='FOUR_LANE_INDEPENDENT_NATIVE_PREFLIGHT';save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(n.archive_case,0,name,True) for name in ['pinned']+[e['name'] for e in build['builds']]]):M['cases'].append(f.result());save()
        by={e['mode']:e for e in M['cases']};assert by['neutral']['archive_sha256']==by['pinned']['archive_sha256'] and by['neutral']['probabilities_sha256']==by['pinned']['probabilities_sha256']
        after=resource.getrusage(resource.RUSAGE_CHILDREN);M.update(status='PASS_NEUTRAL_PARITY_AND_SIX_EXACT_INVERSES',finished=time.time(),worker_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
    except BaseException as e:M.update(status='FAIL_PRESERVED_NO_LONG_JOB',error=repr(e),traceback=traceback.format_exc());save();raise
if __name__=='__main__':main()
