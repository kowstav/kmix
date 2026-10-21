import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');assert json.loads((r/'full_inverse_v1/manifest.json').read_text())['status']=='FAIL';assert not (r/'full_inverse_v2').exists()
s=(r/'research_round7_full_inverse_worker.py').read_text().replace("D=R/'full_inverse_v1';W=pathlib.Path('/root/hp/full_inverse_v1')","D=R/'full_inverse_v2';W=pathlib.Path('/root/hp/full_inverse_v2')")
a=s.index(" prefix='src/fx2-cmix-transformer-v1/'");b=s.index(" src=W/'source'",a)
s=s[:a]+" shutil.copytree('/root/hp/full_inverse_v1/source',W/'source')\n"+s[b:]
s=s.replace("'-std=c++17','-ffunction-sections'","'-std=c++17','-DUPDATE_LIMIT=3000','-DSEED=923','-ffunction-sections'")
(r/'research_round7_full_inverse_v2_worker.py').write_text(s);log=(r/'full_inverse_v2_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_full_inverse_v2_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'inverse_v2_pid':p.pid,'repair':'required UPDATE_LIMIT header macro; v1 sources/logs preserved'}))
