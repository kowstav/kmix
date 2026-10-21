import json,pathlib,shutil,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');assert json.loads((r/'calibration_native_v2/manifest.json').read_text())['status']=='FAIL';d=r/'calibration_native_v3';assert not d.exists();
code=(r/'research_round7_calibration_native_v2_worker.py').read_text().replace("D=R/'calibration_native_v2'","D=R/'calibration_native_v3'")
needle="b=R/'calibration_native_v1/cmix_calibrated';baseline=R/'lex_finalbit_trace_v1/cmix_trace';"
assert needle in code
code=code.replace(needle,"b=R/'calibration_native_v1/cmix_calibrated';baseline=D/'cmix_reference';baseline.write_bytes((R/'lex_finalbit_trace_v1/cmix_trace').read_bytes());baseline.chmod(0o755);")
code=code.replace("Reuse successful v1 build; replace missing /usr/bin/time with Linux wait4. No repeated build or overwritten outputs.","Reuse successful v1 build/wait4; preserve original baseline and restore lost executable mode on a hash-identical copy. Failed v1/v2 logs retained.")
(r/'research_round7_calibration_native_v3_worker.py').write_text(code);log=(r/'calibration_native_v3_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_calibration_native_v3_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'native_v3_pid':p.pid,'restored_permission_on_copy_only':True}))
