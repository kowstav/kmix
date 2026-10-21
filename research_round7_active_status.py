import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');res={}
for n in ['remaining_experts_v1','root_eof_v3','calibration_native_v3','full_inverse_v2','exact_prior_storage_v1']:
 d=r/n;p=d/'manifest.json';m=json.loads(p.read_text()) if p.is_file() else None;q=d/'results.json';rows=json.loads(q.read_text()) if q.is_file() else []
 if m and 'blocks' in m:m={k:v for k,v in m.items() if k!='blocks'}
 res[n]={'manifest':m,'rows':[{'slice':x.get('slice'),'saving_bytes':x.get('mixture_saving_bytes',x.get('score',{}).get('prequential_saving_bytes',x.get('ideal_saving_bytes'))),'user_seconds':x.get('user_seconds'),'archive_saving_bytes':x.get('native_archive_saving_bytes')} for x in rows],
  'tail':(r/(n+'_controller.log')).read_text()[-600:] if (r/(n+'_controller.log')).is_file() else ''}
res['active']=[x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if any(k in x for k in ('remaining_experts','numeric_programs','full_stream_regen'))]
print(json.dumps(res,indent=2))
