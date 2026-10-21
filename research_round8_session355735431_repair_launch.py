import pathlib,subprocess,json,os,signal
R=pathlib.Path('/kaggle/working/hp_round8')
# Stop only the observed waiting controller, after verifying PID and exact argv.
p=pathlib.Path('/proc/117/cmdline')
if p.exists():
 cmd=p.read_bytes().split(bytes([0]));assert str(R/'research_round8_resume_error_memory_worker.py').encode() in cmd
 m=json.loads((R/'error_memory_resume_v1/manifest.json').read_text());assert m['stage'].startswith('waiting') and not m['native_exports'] if 'native_exports' in m else m['stage'].startswith('waiting')
 os.kill(117,signal.SIGTERM)
print(json.dumps({'stopped_waiting_controller':117,'reason':'parent exited on NumPy boolean JSON serialization; preserve original failed directories and scripts','deletions':[]}))
for directory,source in [('atom_fit_resume_v2','research_round8_resume_atom_fit_worker_v2.py'),('error_memory_resume_v2','research_round8_resume_error_memory_worker_v2.py'),('canonical_cost_atlas_v2','research_round8_canonical_cost_atlas_v2.py')]:
 assert not (R/directory).exists()
 p=subprocess.Popen(['python','-u',str(R/source)],stdout=(R/(directory+'_controller.log')).open('x'),stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'pid':p.pid,'experiment':directory,'native_inference_reused':True,'spending_usd':0,'deletions':[]}))
