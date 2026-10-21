import datetime,json,pathlib,shutil,subprocess,tarfile
r=pathlib.Path('/kaggle/working/hp_round7');out=r/'session355529591_inventory.json'
t=r/'preserved/research_sources_and_candidates.tar.gz'
with tarfile.open(t) as f:
    names=[m.name for m in f.getmembers() if m.isfile() and any(s in m.name.lower() for s in ('preprocess','dict','order','train','genprob','ppmd','vocab','tfh','makefile'))]
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'session':355529591,
 'disk':dict(zip(('total','used','free'),shutil.disk_usage('/kaggle/working'))),
 'active':[x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'hp_round7' in x],
 'preserved_source_candidates':names,
 'models':[{'path':str(p),'bytes':p.stat().st_size} for p in r.rglob('*.tfwc2')],
 'dataset':str(r/'preserved/data/enwik9.zip'),'deletions':[]}
out.write_text(json.dumps(result,indent=2));print(json.dumps({'saved':str(out),'tar_candidates':len(names),'free':result['disk']['free']}))
