import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'calibration_native_v2';assert not D.exists();D.mkdir();rows=[]
m={'status':'RUNNING','pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repair':'Reuse successful v1 build; replace missing /usr/bin/time with Linux wait4. No repeated build or overwritten outputs.','deletions':[],'paid_rental_usd':0}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2));(D/'results.json').write_text(json.dumps(rows,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def timed(cmd,d,env,label):
 start=time.monotonic();log=(D/(label+'.log')).open('x');p=subprocess.Popen(cmd,cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);rc=os.waitstatus_to_exitcode(status);log.close();assert rc==0,(label,rc)
 return {'wall_seconds':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss}
save()
try:
 old=json.loads((R/'calibration_native_v1/manifest.json').read_text());assert old['status']=='FAIL' and old['binary_sha256']=='89e0d18855f5fdaf0f0bc0f60a56d0cdd8ac364c944bf05db9d547e485a1f600'
 b=R/'calibration_native_v1/cmix_calibrated';baseline=R/'lex_finalbit_trace_v1/cmix_trace';weights=R/'lex_audit/lex_h1_run11.tfwc2';table=R/'tiny_residual_v1/odds_0.u32';assert sha(b)==old['binary_sha256'];m.update(binary_sha256=sha(b),binary_bytes=b.stat().st_size,table_sha256=sha(table));save()
 base={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};base.update(LAB_RAW='1',LAB_VOCAB=str(R/'preserved/data/vocab.bm'),LAB_DICT=str(R/'preserved/gen/.dict'),LAB_KEEP_TEMP='1')
 for n in 'ef':
  raw=(R/'full_stream_regen_v2'/(n+'2m.bin')).read_bytes()[:65536];inp=D/(n+'64k.bin');inp.write_bytes(raw);runs={}
  for mode,program in [('reference',baseline),('neutral',b),('candidate',b)]:
   d=D/(n+'_'+mode);d.mkdir();(d/'.dict').symlink_to(R/'preserved/gen/.dict');e={**base,'LAB_COST':str(d/'cost.f32'),'LAB_BITTRACE':str(d/'final_p.u16')}
   if mode=='candidate':e['LAB_ODDS']=str(table)
   runs[mode]=timed([str(program),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,e,n+'_'+mode)
  ref,neutral,cand=[D/(n+'_'+s) for s in ['reference','neutral','candidate']];assert (ref/'out.cmx').read_bytes()==(neutral/'out.cmx').read_bytes();rp=np.fromfile(ref/'final_p.u16','<u2');npb=np.fromfile(neutral/'final_p.u16','<u2');cp=np.fromfile(cand/'final_p.u16','<u2');assert np.array_equal(rp,npb)
  f=np.fromfile(table,'<u4').astype(np.uint64);j=np.tile(np.arange(8),len(raw));p=rp.astype(np.uint64);a=p*f[j*16+(p>>12).astype(np.int64)];den=a+(65536-p)*(1<<20);expected=np.clip((a*65536+den//2)//den,1,65535).astype(np.uint16);assert np.array_equal(cp,expected),'Native rational correction mismatch'
  d=D/(n+'_decode');d.mkdir();(d/'.dict').symlink_to(R/'preserved/gen/.dict');runs['decode']=timed([str(b),'--transformer',str(weights),str(cand/'out.cmx'),'decoded.bin'],d,{**base,'LAB_ODDS':str(table)},n+'_decode');assert (d/'decoded.bin').read_bytes()==raw
  rc=np.fromfile(ref/'cost.f32','<f4').astype(np.float64);cc=np.fromfile(cand/'cost.f32','<f4').astype(np.float64)
  row={'slice':n,'input_bytes':len(raw),'native_archive_saving_bytes':(ref/'out.cmx').stat().st_size-(cand/'out.cmx').stat().st_size,'ideal_saving_bytes':float((rc-cc).sum()/8),'neutral_archive_exact':True,'neutral_probabilities_exact':True,'candidate_all_bits_match_integer_replay':True,'independent_raw_decode_exact':True,'runtime':runs};rows.append(row);save();print(json.dumps(row),flush=True)
 m.update(status='COMPLETE_64K_NATIVE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
