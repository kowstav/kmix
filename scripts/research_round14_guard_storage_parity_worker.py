"""64 KiB exact-law/UPX parity on four lanes; separate neutral packed check."""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,os,shutil,sys,time,traceback,zipfile,multiprocessing as mp,resource
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_guard_storage_parity_v1');OUT=W/'guard_storage_parity_v1'
M={'status':'RESTORING_FROZEN_HARNESS','started':time.time(),'cases':[],'workers':4,'deletions':[],'GPU':False,'paid_usd':0}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save():(OUT/'manifest.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists() and not OUT.exists();R.mkdir();OUT.mkdir();save();code=R/'code';code.mkdir()
    with zipfile.ZipFile(W/'sources_confirm_v5.zip.dat') as z:
        for e in json.loads(z.read('source_manifest.json')):
            p=(code/e['path']).resolve();assert p.is_relative_to(code);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    sys.path.insert(0,str(code));from hutter_research import cpu_round13_native as n
    from hutter_research.cpu_round13_jobs import initialize_lane
    build=json.loads((W/'guard_storage_build_v2.json').read_text());assert build['status']=='COMPLETE_BUILDS_AWAITING_NATIVE_PARITY'
    asset=R/'asset';asset.mkdir();base=Path('/kaggle/working')
    files={'native_cmix':base/'hp_round8/native_stage_trace_v1/tree/cmix','original.tfwc3':base/'hp_round7/lex_audit/lex_h1_run11.tfwc2','english.dic':base/'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic','vocab.bm':base/'hp_round7/preserved/data/vocab.bm'}
    wanted={'native_cmix':'17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa','original.tfwc3':'948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71','english.dic':'4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a','vocab.bm':'3e7f8c043939ccba8675b3a260f65a665bc34acac883a7316cc50fecfd7d36b5'}
    for name,p in files.items():assert sha(p)==wanted[name];shutil.copyfile(p,asset/name)
    source=base/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt';assert sha(source)=='7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce'
    with source.open('rb') as f:f.seek(32000000);raw=f.read(65536)
    regions=[]
    for i,size in enumerate((65536,16384)):
        name=f'region_{i:02}.bin';(asset/name).write_bytes(raw[:size]);regions.append({'file':name,'offset':32000000,'bytes':size,'warmup_bytes':0})
    (asset/'r13_assets.json').write_text(json.dumps({'regions':regions}))
    n.ASSET=asset;n.ROOT=R/'work';n.ROOT.mkdir();n.OUT=OUT;n.DEADLINE=time.monotonic()+25*60
    for e in build['builds']:
        for suffix,key in (('', 'raw_sha256'),('_upx','upx_sha256')):
            p=W/'guard_storage_binaries_v2'/('cmix_'+e['name']+suffix);assert sha(p)==e[key]
            dest=n.ROOT/('cmix_head_'+e['name']+suffix);shutil.copyfile(p,dest);dest.chmod(0o700)
    jobs=[(0,'guard_raw'),(0,'guard_packed'),(0,'guard_packed16'),(0,'guard_packed16_upx'),(1,'neutral_raw_upx')]
    cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4;ctx=mp.get_context('fork');q=ctx.Queue()
    for c in cpus:q.put(c)
    before=resource.getrusage(resource.RUSAGE_CHILDREN);M['status']='FOUR_LANE_NATIVE_PARITY';save()
    with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
        for f in as_completed([pool.submit(n.archive_case,i,name,True) for i,name in jobs]):M['cases'].append(f.result());save()
    by={r['mode']:r for r in M['cases']}
    for key in ('archive_sha256','probabilities_sha256'):
        assert len({by[arm][key] for _,arm in jobs[:4]})==1
        prior=next(r for r in json.loads((W/'native_cpu_preflight_v1/manifest.json').read_text())['cases'] if r['mode']=='pinned')
        assert by['neutral_raw_upx'][key]==prior[key]
    after=resource.getrusage(resource.RUSAGE_CHILDREN);M.update(status='PASS_64K_GUARD_RAW_PACKED_SLIM_UPX_PARITY_AND_NEUTRAL_UPX',finished=time.time(),worker_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_QUALITY_TRANSFER',error=repr(e),traceback=traceback.format_exc());save();raise
