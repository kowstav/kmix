from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_native_cpu');tree=R/'tree';M={'status':'REPAIRING_SOURCE_BUNDLE_DEPENDENCIES','started':time.time(),'builds':[],'restored_headers':[],'deletions':[]}
def save():(W/'native_cpu_build_v2.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    assert not (W/'native_cpu_build_v2.json').exists();old=json.loads((W/'native_cpu_build_v1.json').read_text());assert old['status']=='FAIL_PRESERVED' and not old['builds'];save()
    base=Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
    for p in base.rglob('*.hpp'):
        dest=tree/p.relative_to(base);assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        M['restored_headers'].append({'path':p.relative_to(base).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    assert M['restored_headers'];save()
    env=dict(os.environ,PATH=str(R/'tools')+':'+os.environ['PATH']);common=old['flags']['common'];tf=old['flags']['transformer']
    out=W/'native_cpu_binaries_v2';out.mkdir();M.update(status='BUILDING_FIVE_CONTROLLED_BINARIES',flags=old['flags'],compiler=old['compiler']);save()
    for name,ablation,precision in [('neutral',0,0),('prune_word',1,0),('prune_match',2,0),('prune_indirect',3,0),('output_fp32',0,1)]:
        start=time.time();flags=common+f' -DHP_R14_ABLATION={ablation} -DHP_R14_OUTPUT_FP32={precision}';command=['make','-j4','cmix','CFLAGS_DEFINES='+flags,'CFLAGS_TF_DEFINES='+tf]
        with (W/('native_cpu_build_v2_'+name+'.log')).open('xb') as f:r=subprocess.run(command,cwd=tree,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
        assert r.returncode==0,(name,r.returncode)
        target=out/('cmix_'+name);shutil.copyfile(tree/'cmix',target);target.chmod(0o700)
        M['builds'].append({'name':name,'bytes':target.stat().st_size,'sha256':sha(target),'command':command,'build_wall_seconds':time.time()-start});save()
    zpath=W/'native_cpu_sources_v2.zip';entries=[]
    with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(tree.rglob('*')):
            if p.is_file() and (p.suffix in ('.h','.hpp','.cpp','.c','.inc','.tcc') or p.name=='makefile'):
                n=p.relative_to(tree).as_posix();z.write(p,n);entries.append({'path':n,'bytes':p.stat().st_size,'sha256':sha(p)})
        z.writestr('source_manifest.json',json.dumps(entries,indent=2))
    M.update(status='COMPLETE_AWAITING_NATIVE_PARITY',finished=time.time(),source_sha256=sha(zpath),source_entries=len(entries));save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
