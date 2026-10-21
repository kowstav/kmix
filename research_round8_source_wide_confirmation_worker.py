import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,shutil,subprocess,time,traceback
import numpy as np
from scipy.special import expit
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');S=R/'native_stage_trace_v1';D=R/'source_wide_confirmation_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','session':355735431,'pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_spending_usd':0,'deletions':[],'exports':[],'evaluations':[],'actual_candidate_archive_evaluated':False,'scope':'fresh frozen wider source E/F cold-Q16 confirmation; teacher archive only'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(s):m['stage']=s;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(s,flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('x') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,s,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(s)
 a={'wall_seconds':time.monotonic()-t,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=a;raise RuntimeError(label)
 return a
try:
 wide=json.loads((R/'source_wide_box_v1/manifest.json').read_text());old=json.loads((R/'native_stage_fit_v2/manifest.json').read_text());native=json.loads((R/'atom_cache_v1/manifest.json').read_text());stage=json.loads((S/'manifest.json').read_text());assert wide['status']=='COMPLETE_WIDER_SOURCE_FINITE_BOX' and wide['advance_gate_pass'] and wide['certificate_bytes']<=.05
 m['frozen_wider_coefficients']=wide['coefficients'];m['frozen_wider_manifest_sha256']=sha(R/'source_wide_box_v1/manifest.json');m['source_hashes']=[{'file':n,'sha256':sha(R/n)} for n in ['research_round8_source_wide_confirmation_worker.py','research_round8_source_wide_confirmation_protocol.md']];m['production_stream']=native['production_stream'];save('wider candidate frozen before E/F data and source generation')
 source=R/'lexical_full_prepare_v1/lexical_full_ready.wrt';assert source.stat().st_size==587138826 and sha(source)==m['production_stream']['sha256'];binary=S/'tree/cmix';weights=P/'lex_audit/lex_h1_run11.tfwc2';dictionary=S/'tree/dictionary/english.dic';assert sha(binary)==stage['binary_sha256'] and sha(weights)==native['weights_sha256'] and sha(dictionary)==native['dictionary_sha256'];assert shutil.disk_usage(D).free>900000000
 env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))};env.update(LAB_RAW='1',LAB_VOCAB=str(P/'preserved/data/vocab.bm'),LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1');heads=[('wide',np.array(wide['coefficients'])),('narrow',np.array(old['results'][24]['coefficients'])),('generic',np.array(old['results'][0]['coefficients']))]
 for s,offset in [('e',190000000),('f',430000000)]:
  dest=D/(s+'512k');dest.mkdir();(dest/'.dict').symlink_to(dictionary);raw=dest/'input.bin'
  with source.open('rb') as f:f.seek(offset);data=f.read(524288)
  assert len(data)==524288;raw.write_bytes(data);out=dest/'out.cmx';qp=dest/'final_p.u16';sp=dest/'stage.f32';hp=dest/'hidden.q8';save('native original source/hidden export '+s)
  account=run([str(binary),'-n','--transformer',str(weights),str(raw),str(out)],dest,{**env,'LAB_BITTRACE':str(qp),'LAB_STAGETRACE':str(sp),'LAB_HIDDENTRACE':str(hp)},s+'_native_export');assert qp.stat().st_size==8388608 and sp.stat().st_size==318767116 and hp.stat().st_size==101187584
  row={'slice':s,'canonical_offset':offset,'input_sha256':sha(raw),'native_archive_bytes':out.stat().st_size,'native_archive_sha256':sha(out),'native_p_sha256':sha(qp),'stage_bytes':sp.stat().st_size,'stage_sha256':sha(sp),'hidden_bytes':hp.stat().st_size,'hidden_sha256':sha(hp),'accounting':account};m['exports'].append(row)
  p=np.fromfile(qp,dtype='<u2');y=((np.frombuffer(data,np.uint8)[:,None]>>(7-np.arange(8)))&1).astype(np.float64).reshape(-1);frames=np.memmap(sp,mode='r',dtype='<f4',offset=12,shape=(len(p),19));h=np.memmap(hp,mode='r',dtype=np.uint8,shape=(len(data),193));assert np.all(h[:,0]<=1);valid=np.repeat(np.r_[np.uint8(0),h[:-1,0]],8).astype(np.float32);ell=np.log(p.astype(np.float64)/(65536.-p));prob=np.clip(frames[:,17].astype(np.float64),1/65536,65535/65536);feature=(np.clip(np.log(prob/(1-prob))-ell,-12,12)/12).astype(np.float32)*valid;assert np.isfinite(feature).all();results=[]
  for name,t in heads:
   gain=ideal=0.;qsha=hashlib.sha256()
   for i in range(0,len(p),131072):
    pp=p[i:i+131072].astype(np.float64);yy=y[i:i+131072];ll=ell[i:i+131072];X=np.column_stack([np.ones(len(pp)),ll]+([feature[i:i+131072]] if name!='generic' else []));q=expit(ll+X@t);u=np.clip(np.floor(65536*q+.5),1,65535).astype('<u2');qsha.update(u.tobytes());base=np.where(yy,pp,65536-pp)/65536.;gain+=float(np.sum(np.log2(np.where(yy,u.astype(np.float64),65536.-u)/65536./base))/8);ideal+=float(np.sum(np.log2(np.where(yy,q,1-q)/base))/8)
   results.append({'head':name,'Q16_saving_bytes':gain,'ideal_saving_bytes':ideal,'prediction_sha256':qsha.hexdigest()})
  m['evaluations'].append({'slice':s,'bytes':524288,'results':results,'source_feature_sha256':hashlib.sha256(feature.tobytes()).hexdigest()});save('frozen wider/narrow/generic exactQ16scored '+s)
 m['wider_both_slices_improve']=all(v['results'][0]['Q16_saving_bytes']>0 for v in m['evaluations']);m['wider_both_slices_beat_generic']=all(v['results'][0]['Q16_saving_bytes']>v['results'][2]['Q16_saving_bytes'] for v in m['evaluations']);m['wider_confirmation_Q16_gain_bytes']=sum(v['results'][0]['Q16_saving_bytes'] for v in m['evaluations']);m.update(status='COMPLETE_FRESH_WIDER_SOURCE_EF_Q16_CONFIRMATION',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('fresh confirmation complete; actual wider candidate archive still open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
