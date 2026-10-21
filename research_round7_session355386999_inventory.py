import pathlib,json,subprocess,shutil,os,datetime
out=pathlib.Path('/kaggle/working/hp_round7')
r={'session':355386999,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'active':subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True),'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used','--format=csv,noheader'],text=True),'ephemeral_hp_exists':pathlib.Path('/root/hp').exists(),'disk':{k:dict(zip(['total','used','free'],shutil.disk_usage(k))) for k in ['/kaggle/working','/root']},'files':{}}
r['active']='\n'.join(s for s in r['active'].splitlines() if 'hp_round7' in s or '/cmix_round7_' in s)
for n in ['lex_native_2m_recovered/results.json','causal_latent_words_v2/summary.json','causal_latent_words_v3/summary.json','frozen_logits_pilot/results.json']:
    p=out/n;r['files'][n]=json.loads(p.read_text()) if p.exists() else None
for name in ['frozen_logits_pilot_v2','idea_arch_screens_v1']:
    r[name+'_exists']=(out/name).exists()
(out/'session355386999_inventory.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
