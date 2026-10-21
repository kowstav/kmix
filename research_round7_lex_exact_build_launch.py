import pathlib,tarfile,subprocess,shutil,json
out=pathlib.Path('/kaggle/working/hp_round7');old=pathlib.Path('/root/hp/lex_baseline_lab');dest=pathlib.Path('/root/hp/lex_matched_lab')
assert not dest.exists() and not (out/'lex_exact_build.log').exists(),'Refuse duplicate build'
shutil.copytree(old,dest)
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for name in ['src/runner.cpp','src/coder/encoder.cpp']:(dest/name).write_bytes(tar.extractfile('src/cmix-lex-transformer/'+name).read())
source=(out/'lex_build_api_worker.py').read_text();tail=source.split("mf=dest/'makefile'",1)[1]
worker=out/'lex_exact_build_worker.py';worker.write_text('import pathlib,subprocess,shutil,json,time,hashlib\nout=pathlib.Path('+repr(str(out))+');dest=pathlib.Path('+repr(str(dest))+')\nsubprocess.run(["python",str(out/"research_round7_lex_exact_labpatch.py")],cwd=dest,check=True)\nmf=dest/\'makefile\''+tail)
with (out/'lex_exact_build.log').open('w') as f:p=subprocess.Popen(['python','-u',str(worker)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'exact_lex_build_pid':p.pid,'all_original_source_files_preserved':True,'failed_generic_patch_copies_and_logs_preserved':True}))
