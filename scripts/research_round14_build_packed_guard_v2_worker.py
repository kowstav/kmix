"""Exact guard storage engineering, four compiler lanes, preserved originals."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_guard_storage_v2');M={'status':'WAITING_FOR_COMPILER','started':time.time(),'builds':[],'deletions':[]}
def save():(W/'guard_storage_build_v2.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    assert not R.exists() and not (W/'guard_storage_build_v2.json').exists();R.mkdir();save();deadline=time.time()+1200
    while True:
        p=W/'compiler_restore_session356740330_v2.json';m=json.loads(p.read_text()) if p.exists() else {}
        if m.get('status','').startswith('FAIL'):raise RuntimeError('compiler restoration failed')
        if m.get('status')=='COMPLETE_PINNED_COMPILER_AVAILABLE':break
        assert time.time()<deadline;time.sleep(20)
    source=W/'native_cpu_sources_v2.zip';assert sha(source)=='a21f035652bf756db9e0bc43c34835ed85412540dc5dd9329d62fd1cd4183840'
    packed=W/'probability_tables_packed_v2.inc.dat';assert sha(packed)=='6eb41d6bd3c78ffdaa83854e374eb7ef4167e97f27b305c4debbd8308114e059'
    base=R/'source';base.mkdir()
    with zipfile.ZipFile(source) as z:
        for e in json.loads(z.read('source_manifest.json')):
            p=(base/e['path']).resolve();assert p.is_relative_to(base);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    tools=R/'tools';tools.mkdir();(tools/'ld.lld').symlink_to('/usr/bin/ld.lld-17');env=dict(os.environ,PATH=str(tools)+':'+os.environ['PATH'])
    build=json.loads((W/'native_cpu_build_v2.json').read_text());common=build['flags']['common'];tf=build['flags']['transformer']
    output=W/'guard_storage_binaries_v2';output.mkdir();upx=Path('/kaggle/working/hp_round7/tools/upx-3.96');assert upx.is_file();upx.chmod(0o700)
    M.update(status='BUILDING_EXACT_STORAGE_VARIANTS',upx_sha256=sha(upx),compiler=m['clang_version']);save()
    for name,head,packing,slim in [('neutral_raw',0,False,False),('guard_raw',2,False,False),('guard_packed',2,True,False),('guard_packed16',2,True,True)]:
        tree=R/name;shutil.copytree(base,tree)
        if packing:shutil.copyfile(packed,tree/'src/hp_r13/probability_tables.inc')
        if slim:
            p=tree/'src/hp_r13/integer_mixer.h';s=p.read_text();a='kContexts=640,kFeatures=24';b='for(int i=0;i<8;i++)features_[16+i]=stretch(memory[i]);'
            assert s.count(a)==s.count(b)==1;s=s.replace(a,'kContexts=640,kFeatures=16').replace(b,'(void)memory; // Native guard always supplies neutral zero-logit memory.');p.write_text(s)
        flags=common.replace('-DHP_R13_HEAD=0','-DHP_R13_HEAD='+str(head))+' -DHP_R14_ABLATION=0 -DHP_R14_OUTPUT_FP32=0'
        cmd=['make','-j4','cmix','CFLAGS_DEFINES='+flags,'CFLAGS_TF_DEFINES='+tf];start=time.time()
        with (W/('guard_storage_v2_'+name+'.log')).open('xb') as f:r=subprocess.run(cmd,cwd=tree,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
        assert r.returncode==0,(name,r.returncode)
        p=output/('cmix_'+name);shutil.copyfile(tree/'cmix',p);p.chmod(0o700)
        packed_bin=output/('cmix_'+name+'_upx');shutil.copyfile(p,packed_bin);packed_bin.chmod(0o700)
        with (W/('guard_storage_v2_'+name+'_upx.log')).open('xb') as f:r=subprocess.run([str(upx),'--lzma','-9',str(packed_bin)],stdout=f,stderr=subprocess.STDOUT,timeout=180)
        assert r.returncode==0,('upx',name,r.returncode)
        zpath=output/(name+'_source.zip')
        with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
            for q in sorted(tree.rglob('*')):
                if q.is_file() and (q.suffix in ('.h','.hpp','.cpp','.c','.inc','.tcc') or q.name=='makefile'):z.write(q,q.relative_to(tree).as_posix())
        row={'name':name,'raw_bytes':p.stat().st_size,'raw_sha256':sha(p),'upx_bytes':packed_bin.stat().st_size,'upx_sha256':sha(packed_bin),'source_sha256':sha(zpath),'command':cmd,'wall_seconds':time.time()-start}
        M['builds'].append(row);save()
    M.update(status='COMPLETE_BUILDS_AWAITING_NATIVE_PARITY',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
