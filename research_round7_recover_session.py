def _hp_round7_recover_session():
    import pathlib, json, subprocess, os
    out=pathlib.Path('/kaggle/working/hp_round7')
    logs={p.name:p.read_text(errors='replace')[-2000:] for p in out.glob('*.log')}
    result={'logs':logs,'files':[{'name':p.name,'size':p.stat().st_size,'is_dir':p.is_dir()} for p in out.iterdir()]}
    result['compilers']={}
    for name in ['clang++','clang++-20','clang++-18','g++','zstd']:
        import shutil
        executable=shutil.which(name)
        result['compilers'][name]=executable
    worker=r'''
import pathlib,tarfile,shutil,zipfile,os,json
out=pathlib.Path('/kaggle/working/hp_round7'); hp=pathlib.Path('/root/hp')
hp.mkdir(exist_ok=True)
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for member in tar.getmembers():
        target=(hp/member.name).resolve()
        if not target.is_relative_to(hp.resolve()): raise RuntimeError('Archive target escapes recovery root')
        if member.issym():
            link=pathlib.Path(member.linkname)
            resolved=link.resolve() if link.is_absolute() else (target.parent/link).resolve()
            if not resolved.is_relative_to(hp.resolve()): raise RuntimeError('Archive symlink escapes recovery root')
            member.linkname=os.path.relpath(resolved,target.parent)
        tar.extract(member,hp,filter='data')
for folder in ['data','gen','dic','slices','runs/lex_a','runs/lex_b','src/cmix-lex']:
    (hp/folder).mkdir(parents=True,exist_ok=True)
for p in (out/'preserved').rglob('*'):
    if not p.is_file() or p.suffix in ['.gz','.json']: continue
    rel=p.relative_to(out/'preserved'); dst=hp/rel; dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists(): dst.symlink_to(p)
with zipfile.ZipFile(hp/'data/enwik9.zip') as z:
    if not (hp/'data/enwik9').exists(): z.extract('enwik9',hp/'data')
(hp/'dic/dic.txt').symlink_to(hp/'gen/.dict')
for name in ['a','b']:
    dst=hp/('runs/lex_'+name)/'cost.f32'
    if not dst.exists(): dst.symlink_to(out/'preserved'/('runs/lex_'+name)/'cost.f32')
for name in ['c','d']:
    for ext in ['.bin','.probs.f16']:
        src=out/(name+'2m'+ext)
        if src.exists(): (hp/'slices'/(name+'2m'+ext)).symlink_to(src)
# Restore the exact fxcm source that was compiled into the preserved candidate.
(hp/'src/cmix-lex/src/models').mkdir(parents=True,exist_ok=True)
for name in ['fxcmv1.cpp','fxcmv1.h']:
    shutil.copyfile(hp/'cand_final2/src/models'/name,hp/'src/cmix-lex/src/models'/name)
print(json.dumps({'recovered':True,'data_bytes':(hp/'data/enwik9').stat().st_size,'candidate_bytes':[(p.name,p.stat().st_size) for p in (hp/'cand_final2/run').iterdir() if p.is_file()]}),flush=True)
'''
    script=out/'recover_worker.py'; script.write_text(worker)
    with (out/'recover.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(script)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    result['recovery_pid']=p.pid
    print(json.dumps(result))
_hp_round7_recover_session()
del _hp_round7_recover_session
