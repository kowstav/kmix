import pathlib,subprocess,json,hashlib
out=pathlib.Path('/kaggle/working/hp_round7')
assert "No such file or directory: '/usr/bin/time'" in (out/'lex_native_controller.log').read_text()
assert (out/'cmix_round7_lex_roundtrip').exists()
assert not (out/'lex_native_v2_controller.log').exists(),'Refuse duplicate launch'
source=(out/'research_round7_lex_native_controller.py').read_text()
source=source.replace("out/'lex_native'","out/'lex_native_v2'").replace("'/root/hp/lex_native'","'/root/hp/lex_native_v2'")
source=source.replace("subprocess.run(['python','-u',str(out/'research_round7_lex_roundtrip_prepare.py')],check=True)","subprocess.run(['apt-get','install','-y','--no-install-recommends','time'],check=True,timeout=300)\nassert pathlib.Path('/usr/bin/time').exists()")
script=out/'lex_native_v2_controller.py';script.write_text(source)
with (out/'lex_native_v2_controller.log').open('w') as f:p=subprocess.Popen(['python','-u',str(script)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'native_v2_controller_pid':p.pid,'reuses_completed_forced_compile':True,'repair':'install missing GNU time for CPU/RAM accounting before any native job starts','original_failure_preserved':True,'binary_sha256':hashlib.sha256((out/'cmix_round7_lex_roundtrip').read_bytes()).hexdigest()}))
