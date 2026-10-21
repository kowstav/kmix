import datetime,hashlib,json,os,pathlib,shutil,subprocess,tarfile,traceback,zipfile
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'full_stream_regen_v1';W=pathlib.Path('/root/hp/full_stream_regen_v1')
assert not D.exists() and not W.exists(),'No duplicate/full-data overwrite'
D.mkdir();W.mkdir(parents=True);m={'status':'RUNNING','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'deletions':[],'paid_rental_usd':0,'scratch':str(W)}
def save(): (D/'manifest.json').write_text(json.dumps(m,indent=2))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
save()
try:
 with tarfile.open(R/'preserved/research_sources_and_candidates.tar.gz') as t:
  name='cand_final2/run/cmix';payload=t.extractfile(name).read();(W/'cmix').write_bytes(payload);(W/'cmix').chmod(0o755)
 m['binary_sha256']=sha(W/'cmix');m['prepare_only_hook']=b'FX_PREPARE_ONLY' in payload;m['bytes_only_flag']=b'--bytes-only' in payload;save()
 assert m['prepare_only_hook'] or m['bytes_only_flag'],'Preserved package lacks model-free preparation; no full native coding launch'
 with zipfile.ZipFile(R/'preserved/data/enwik9.zip') as z:
  assert z.namelist()==['enwik9'];assert z.getinfo('enwik9').file_size==1000000000
  with z.open('enwik9') as src,(W/'enwik9').open('xb') as dst:shutil.copyfileobj(src,dst,1<<20)
 assert sha(W/'enwik9')=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
 env=dict(os.environ);cmd=[str(W/'cmix'),'-e',str(W/'enwik9'),'prepared']
 if m['prepare_only_hook']:env['FX_PREPARE_ONLY']='1'
 else:cmd+=['--bytes-only','--save-ppmd-bytes',str(D/'tokens.uint8'),'--save-article-boundaries',str(D/'article_boundaries.int32')]
 with (D/'prepare.log').open('x') as log:
  p=subprocess.Popen(cmd,cwd=W,env=env,stdout=log,stderr=subprocess.STDOUT);pid,status,u=os.wait4(p.pid,0);code=os.waitstatus_to_exitcode(status)
 assert code==0,('Preparation failed',code)
 ready=W/'prepared.cmix.temp';m['cpu_user_seconds']=u.ru_utime;m['max_rss_kbytes']=u.ru_maxrss
 if ready.exists():
  target=D/'full_ready.wrt';shutil.copyfile(ready,target);m['full_ready']={'bytes':target.stat().st_size,'sha256':sha(target)}
  # Existing slice offsets are found only for provenance; never reuse these as new validation.
  data=target.read_bytes();m['old_slice_offsets']={}
  for n in 'abcd':
   p=R/'preserved/slices'/(n+'2m.bin') if n in 'ab' else R/(n+'2m.bin');s=p.read_bytes();at=data.find(s[:65536]);m['old_slice_offsets'][n]={'offset':at,'full2m_identical':at>=0 and data[at:at+len(s)]==s}
  # Fresh regions preregistered by absolute offsets, not ranked by performance.
  m['fresh_regions']={n:{'offset':off,'bytes':2000000} for n,off in [('e',220000000),('f',480000000)]}
  for n,x in m['fresh_regions'].items():
   assert x['offset']+x['bytes']<=len(data);p=D/(n+'2m.bin');p.write_bytes(data[x['offset']:x['offset']+x['bytes']]);x['sha256']=sha(p)
  m['ready_dictionary_sha256']=sha(W/'.dict') if (W/'.dict').is_file() else None
  m['reference_dictionary_match']=m['ready_dictionary_sha256']==sha(R/'preserved/gen/.dict')
 else:
  m['full_ready']=None;m['tokens_bytes']=(D/'tokens.uint8').stat().st_size
 m['scratch_files']=[{'path':str(p),'bytes':p.stat().st_size} for p in W.iterdir() if p.is_file()]
 m.update(status='COMPLETE_PREPARATION_ONLY',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),training_priors='NOT_REGENERATED',raw_full_decode='NOT_VERIFIED');save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
