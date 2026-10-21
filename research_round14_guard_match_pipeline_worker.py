"""Wait for exact storage gate; then build, preflight and submit one joint arm."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,multiprocessing as mp,os,shutil,subprocess,sys,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_guard_match_pipeline_v1')
M={'status':'WAITING_FOR_EXACT_STORAGE_PARITY','started':time.time(),'cases':[],'deletions':[],'GPU':False,'paid_usd':0}
def save():(W/'guard_match_pipeline_v1.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    assert not R.exists() and not (W/'guard_match_pipeline_v1.json').exists();R.mkdir();save();deadline=time.time()+1800
    while True:
        p=W/'guard_storage_parity_v1/manifest.json';gate=json.loads(p.read_text()) if p.exists() else {}
        if gate.get('status','').startswith('FAIL'):raise RuntimeError('storage gate failed; no joint build/submission')
        if gate.get('status')=='PASS_64K_GUARD_RAW_PACKED_SLIM_UPX_PARITY_AND_NEUTRAL_UPX':break
        assert time.time()<deadline,'parity gate wait exceeded';time.sleep(20)
    prep=json.loads((W/'prepared_guard_match_v6.json').read_text());assert sha(W/'sources_guard_match_v6.zip.dat')==prep['source_sha256']
    code=R/'code';code.mkdir()
    with zipfile.ZipFile(W/'sources_guard_match_v6.zip.dat') as z:
        for e in json.loads(z.read('source_manifest.json')):
            p=(code/e['path']).resolve();assert p.is_relative_to(code);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    sys.path.insert(0,str(code));from hutter_research import cpu_round13_native as n
    from hutter_research.cpu_round13_jobs import initialize_lane
    from hutter_research.dispatch_contracts import parse_successful_push
    prior=json.loads((W/'guard_storage_build_v2.json').read_text());base=next(x for x in prior['builds'] if x['name']=='guard_packed16')
    source=W/'guard_storage_binaries_v2/guard_packed16_source.zip';assert sha(source)==base['source_sha256'];tree=R/'tree';tree.mkdir()
    with zipfile.ZipFile(source) as z:
        for name in z.namelist():assert (tree/name).resolve().is_relative_to(tree)
        z.extractall(tree)
    tools=R/'tools';tools.mkdir();(tools/'ld.lld').symlink_to('/usr/bin/ld.lld-17');env=dict(os.environ,PATH=str(tools)+':'+os.environ['PATH'])
    cmd=[a.replace('-DHP_R14_ABLATION=0','-DHP_R14_ABLATION=2') for a in base['command']];assert cmd!=base['command'];M.update(status='BUILDING_COMBINED_GUARD_MATCH',command=cmd,source_sha256=sha(source));save()
    with (W/'guard_match_build_v1.log').open('xb') as f:q=subprocess.run(cmd,cwd=tree,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
    assert q.returncode==0
    out=W/'guard_match_binaries_v1';out.mkdir();joint=out/'cmix_guard_match';shutil.copyfile(tree/'cmix',joint);joint.chmod(0o700)
    baseline=out/'cmix_guard_base';shutil.copyfile(W/'guard_storage_binaries_v2/cmix_guard_packed16',baseline);baseline.chmod(0o700);assert sha(baseline)==base['raw_sha256']
    packed=out/'cmix_guard_match_upx';shutil.copyfile(joint,packed);packed.chmod(0o700)
    with (W/'guard_match_upx_v1.log').open('xb') as f:q=subprocess.run(['/kaggle/working/hp_round7/tools/upx-3.96','--lzma','-9',str(packed)],stdout=f,stderr=subprocess.STDOUT,timeout=180)
    assert q.returncode==0;M['binary']={'raw_bytes':joint.stat().st_size,'raw_sha256':sha(joint),'upx_bytes':packed.stat().st_size,'upx_sha256':sha(packed)};save()
    asset=R/'asset';asset.mkdir();prev=Path('/root/r14_guard_storage_parity_v1/asset')
    for name in ('native_cmix','original.tfwc3','english.dic','vocab.bm'):assert (prev/name).is_file();shutil.copyfile(prev/name,asset/name)
    canon=Path('/kaggle/working/hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt');assert sha(canon)=='7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce';regions=[]
    with canon.open('rb') as f:
        for i,offset in enumerate((32000000,288000000)):
            f.seek(offset);raw=f.read(16384);name=f'region_{i:02}.bin';(asset/name).write_bytes(raw);regions.append({'file':name,'offset':offset,'bytes':len(raw),'warmup_bytes':0})
    (asset/'r13_assets.json').write_text(json.dumps({'regions':regions}))
    n.ASSET=asset;n.ROOT=R/'preflight';n.ROOT.mkdir();n.OUT=W/'guard_match_preflight_v1';n.OUT.mkdir();n.DEADLINE=time.monotonic()+15*60
    for name in ('guard_base','guard_match'):
        p=n.ROOT/('cmix_head_'+name);shutil.copyfile(out/('cmix_'+name),p);p.chmod(0o700)
    cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4;ctx=mp.get_context('fork');qu=ctx.Queue()
    for c in cpus:qu.put(c)
    M['status']='FOUR_LANE_COMBINED_NATIVE_PREFLIGHT';save()
    with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(qu,)) as pool:
        for f in as_completed([pool.submit(n.archive_case,i,name,True) for i in (0,1) for name in ('guard_base','guard_match')]):M['cases'].append(f.result());save()
    M['status']='PASS_FOUR_NATIVE_COMBINED_INVERSES_AND_PACKED_GUARD_PARITY';save()
    upload=R/'private_asset';upload.mkdir()
    for name in ('cmix_guard_base','cmix_guard_match'):shutil.copyfile(out/name,upload/name)
    shutil.copyfile(source,upload/'native_source.zip.dat');shutil.copyfile(W/'guard_match_pipeline_v1.json',upload/'preflight_build.json')
    files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in upload.iterdir()}
    (upload/'guard_match_assets.json').write_text(json.dumps({'gate':M['status'],'files':files,'source_sha256':sha(source)},indent=2))
    dataset='chaoscpp/hutter-r14-guard-match-assets-v1';(upload/'dataset-metadata.json').write_text(json.dumps({'id':dataset,'title':'Hutter r14 guard match assets v1','licenses':[{'name':'other'}]}))
    q=subprocess.run(['kaggle','datasets','create','-p',str(upload)],capture_output=True,text=True,timeout=300);url='https://www.kaggle.com/datasets/'+dataset
    assert q.returncode==0 and url in q.stdout and 'error' not in q.stdout.lower(),'private dataset result unverified; inspect, do not retry';M['asset_url']=url;save()
    with zipfile.ZipFile(W/'kernel_guard_match_v6.zip.dat') as z:
        for name in z.namelist():assert (R/name).resolve().is_relative_to(R)
        z.extractall(R)
    folder=R/prep['folder'];assert sha(folder/'main.py')==prep['main_sha256']
    q=subprocess.run(['kaggle','kernels','list','--mine','--search',prep['folder'],'--csv'],capture_output=True,text=True,timeout=30);assert q.returncode==0 and prep['ref'] not in q.stdout
    q=subprocess.run(['kaggle','kernels','push','-p',str(folder)],capture_output=True,text=True,timeout=120)
    assert q.returncode==0;M['verified_push']=parse_successful_push(q.stdout,'chaoscpp')
    M.update(status='COMPLETE_COMBINED_NATIVE_PREFLIGHT_AND_VERIFIED_CPU_PUSH',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_AUTOMATIC_RETRY',error=repr(e),traceback=traceback.format_exc());save();raise
