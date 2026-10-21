import pathlib,subprocess,tarfile,json,hashlib
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/lex_baseline_lab')
log=out/'lex_build.log';assert 'IndentationError: unexpected indent' in log.read_text()
assert not (out/'lex_build_resume.log').exists(),'Refuse duplicate repair'
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for name in ['src/runner.cpp','src/coder/encoder.cpp']:
        assert (dest/name).read_bytes()==tar.extractfile('src/cmix-lex-transformer/'+name).read(),'Original build inputs changed before repair'
source=(out/'research_round7_lex_build_worker.py').read_text()
tail=source.split('# Restrict instrumentation to encoder and runner.')[1]
tail=tail.replace("patch=patch.split('# ---- predictor:')[0]+patch.split('# keep .dict')[1].split('# LAB_UNIFORM_NN')[0]","patch=patch.split('# ---- predictor:')[0]+'# keep .dict'+patch.split('# keep .dict')[1].split('# LAB_UNIFORM_NN')[0]")
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:patch=tar.extractfile('tools/labpatch.py').read().decode()
worker=out/'lex_build_resume_worker.py'
worker.write_text('import pathlib,subprocess,shutil,json,time,hashlib\nout=pathlib.Path('+repr(str(out))+');dest=pathlib.Path('+repr(str(dest))+')\npatch='+repr(patch)+'\n# Restrict instrumentation to encoder and runner.'+tail)
with (out/'lex_build_resume.log').open('w') as f:p=subprocess.Popen(['python','-u',str(worker)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'resume_pid':p.pid,'repair':'restored a missing comment prefix in generated instrumentation; original sources verified unchanged','initial_failure_log_preserved':True}))
