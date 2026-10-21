from pathlib import Path
import hashlib,json,os,resource,shutil,subprocess,time,traceback
W=Path('/kaggle/working/hp_round13');OUT=W/'native_preflight_v1.json';ROOT=Path('/root/hp_round13_native_preflight_v1')
M={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'cases':[],'deletions':[]}
def save():OUT.write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
try:
    assert not OUT.exists() and not ROOT.exists();ROOT.mkdir();save()
    b=json.loads((W/'native_build_v1.json').read_text());assert b['status']=='COMPLETE_LAB_BINARIES_AWAITING_PARITY_PREFLIGHT'
    asset=Path('/root/hp_round13_asset_v1');meta=json.loads((asset/'r13_assets.json').read_text())
    raw=(asset/meta['regions'][0]['file']).read_bytes()[:16384];(ROOT/'input.bin').write_bytes(raw)
    for mode in ('pinned',0,1,2):
        case=ROOT/str(mode);case.mkdir();(case/'input.bin').write_bytes(raw);(case/'.dict').symlink_to(asset/'english.dic')
        binary=asset/'native_cmix' if mode=='pinned' else W/'native_binaries_v1'/f'cmix_head_{mode}'
        if mode=='pinned':copy=case/'cmix';shutil.copyfile(binary,copy);copy.chmod(0o700);binary=copy
        env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))}
        env.update(LAB_RAW='1',LAB_DICT=str(asset/'english.dic'),LAB_VOCAB=str(asset/'vocab.bm'),LAB_KEEP_TEMP='1',LAB_BITTRACE=str(case/'probabilities.u16'))
        row={'mode':mode,'binary_sha256':sha(binary)}
        for action in ('encode','decode'):
            args=[str(binary),'-n','--transformer',str(asset/'original.tfwc3'),'input.bin','archive.cmx'] if action=='encode' else [str(binary),'-d','--transformer',str(asset/'original.tfwc3'),'archive.cmx','restored.bin']
            runenv=dict(env)
            if action=='decode':runenv.pop('LAB_BITTRACE')
            start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
            with (case/(action+'.log')).open('xb') as f:r=subprocess.run(args,cwd=case,env=runenv,stdout=f,stderr=subprocess.STDOUT,timeout=180)
            after=resource.getrusage(resource.RUSAGE_CHILDREN);assert r.returncode==0,(mode,action,r.returncode)
            row[action]={'wall_seconds':time.monotonic()-start,'CPU_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'peak_RSS_KiB':after.ru_maxrss}
        assert (case/'restored.bin').read_bytes()==raw
        for filename in ('archive.cmx','probabilities.u16','encode.log','decode.log'):
            shutil.copyfile(case/filename,W/f'native_preflight_{mode}_{filename}')
        row.update(archive_bytes=(case/'archive.cmx').stat().st_size,archive_sha256=sha(case/'archive.cmx'),probabilities_sha256=sha(case/'probabilities.u16'),independent_decode_exact=True)
        M['cases'].append(row);save()
    assert M['cases'][0]['archive_sha256']==M['cases'][1]['archive_sha256'],'neutral native archive differs from pinned coder'
    assert M['cases'][0]['probabilities_sha256']==M['cases'][1]['probabilities_sha256'],'neutral probability trajectory differs'
    M.update(status='PASS_NEUTRAL_NATIVE_PARITY_AND_THREE_EXACT_DECODES',finished=time.time());save()
except BaseException as e:
    M.update(status='FAIL_PRESERVED_NO_REMOTE_COMMIT',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
