import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/lex_baseline_lab')
assert 'anchor found 2 times' in (out/'lex_build_resume.log').read_text()
assert not (out/'lex_build_api.log').exists(),'Refuse duplicate repair'
p=dest/'round7_lex_labpatch.py';s=p.read_text()
needle="    n = s.count(old)\n    assert n == count,"
replacement="    if new in s:\n        assert s.count(new)==count, 'Existing instrumentation count mismatch'\n        return\n    if path=='src/coder/encoder.cpp' and old.startswith('  if (bit)'):\n        count=2  # lex adds EncodeRawBit; both use the same quantized bit probability\n    n = s.count(old)\n    assert n == count,"
assert s.count(needle)==1;s=s.replace(needle,replacement);p.write_text(s)
source=(out/'lex_build_resume_worker.py').read_text()
tail=source.split("mf=dest/'makefile'",1)[1]
worker=out/'lex_build_api_worker.py'
worker.write_text('import pathlib,subprocess,shutil,json,time,hashlib\nout=pathlib.Path('+repr(str(out))+');dest=pathlib.Path('+repr(str(dest))+')\nsubprocess.run(["python",str(dest/"round7_lex_labpatch.py")],cwd=dest,check=True)\nmf=dest/\'makefile\''+tail)
with (out/'lex_build_api.log').open('w') as f:p=subprocess.Popen(['python','-u',str(worker)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'repair_pid':p.pid,'repair':'account for lex EncodeRawBit API; retain the already applied include instrumentation; all anchors remain checked','logs_preserved':True}))
