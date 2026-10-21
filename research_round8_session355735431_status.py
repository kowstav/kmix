import json,pathlib,subprocess,datetime,shutil
R=pathlib.Path('/kaggle/working/hp_round8');rows=[]
for name in ['atom_fit_resume_v1','error_memory_resume_v1','canonical_cost_atlas_v1']:
 p=R/name/'manifest.json'
 if p.exists():
  m=json.loads(p.read_text());rows.append({'experiment':name,**{k:m.get(k) for k in ['status','stage','pid','error','best_priced_AB_bytes','fixed_online_AB','advance_gate_pass','confirmation_candidates_evaluated']},'heads':len(m.get('results',[])),'features':len(m.get('feature_exports',[])),'atlas_slices':len(m.get('slices',[])),'last_head':m.get('results',[{}])[-1].get('name') if m.get('results') else None})
live=[s for s in subprocess.check_output(['ps','-eo','pid,etime,pcpu,rss,args'],text=True).splitlines() if any(w in s for w in ['research_round8_resume_atom_fit_worker.py','research_round8_resume_error_memory_worker.py','research_round8_canonical_cost_atlas.py'])]
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'session':355735431,'manifests':rows,'live':live,'working_free_bytes':shutil.disk_usage(R).free}))
