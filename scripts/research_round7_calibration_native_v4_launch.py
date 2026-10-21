import pathlib,subprocess,json
r=pathlib.Path('/kaggle/working/hp_round7');assert json.loads((r/'calibration_native_v3/manifest.json').read_text())['status']=='FAIL';assert not (r/'calibration_native_v4').exists()
code=(r/'research_round7_calibration_native_v3_worker.py').read_text().replace("D=R/'calibration_native_v3'","D=R/'calibration_native_v4'")
old="   d=D/(n+'_'+mode);d.mkdir();(d/'.dict').symlink_to(R/'preserved/gen/.dict');e={**base,'LAB_COST':str(d/'cost.f32'),'LAB_BITTRACE':str(d/'final_p.u16')}"
new="""   if n=='e':
    d=R/'calibration_native_v3'/(n+'_'+mode);assert all((d/p).is_file() for p in ['out.cmx','cost.f32','final_p.u16']);(D/(n+'_'+mode)).symlink_to(d,target_is_directory=True);runs[mode]={'reused_completed_v3_outputs':True,'runtime':None,'note':'wait4 timing was not persisted before failed decode; do not fabricate it'};continue
   d=D/(n+'_'+mode);d.mkdir();(d/'.dict').symlink_to(R/'preserved/gen/.dict');e={**base,'LAB_COST':str(d/'cost.f32'),'LAB_BITTRACE':str(d/'final_p.u16')}"""
assert old in code;code=code.replace(old,new)
old="[str(b),'--transformer',str(weights),str(cand/'out.cmx'),'decoded.bin']";assert old in code;code=code.replace(old,"[str(b),'-d','--transformer',str(weights),str(cand/'out.cmx'),'decoded.bin']")
code=code.replace('Reuse successful v1 build/wait4; preserve original baseline and restore lost executable mode on a hash-identical copy. Failed v1/v2 logs retained.','Correct explicit -d CLI mode. Reuse E compression outputs from v3, successful v1 build and hash-identical reference copy. All failed logs retained; no repeated E compression.')
(r/'research_round7_calibration_native_v4_worker.py').write_text(code);log=(r/'calibration_native_v4_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_calibration_native_v4_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'outputs':'calibration_native_v4','E_compression_reused':True}))
