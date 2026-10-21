"""Exact model packing in the original container's tensor order.

The observer dumped sorted tensors; adaptive coding is order-sensitive. Recover
the original order rather than charge a spurious repacking penalty to training.
Native reader tensor identity allows already-decoded archives to be reused.
"""
import os,pathlib,json,time,hashlib,traceback,sys,subprocess
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'model_order_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/model_order_v1');S.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'scratch':str(S),'models':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(s):m['stage']=s;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(s,flush=True)
try:
 sys.path.insert(0,'/root/hp_round9/runtime_site_v1');sys.path.insert(0,'/root/hp_round9/restored/src/fx2-cmix-transformer-v1')
 from pysrc.export_weights import read_tensor_file
 from pysrc.weights_compress import write_tensor_file_v2,read_tensor_file_v2,_verify_equal
 base=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2');ordered_original=read_tensor_file_v2(str(base));order=list(ordered_original);m['original_order']=order;m['original_model_bytes']=base.stat().st_size;m['original_model_sha256']=sha(base)
 for name in ['zero_update','unweighted','cut107_half','cut1392_zero']:
  raw=pathlib.Path('/root/hp_round9/core_export_v1')/(name+'.bin');entries=read_tensor_file(str(raw));assert set(entries)==set(order);packed=S/(name+'.tfwc2');start=time.monotonic();write_tensor_file_v2(str(packed),[(k,*entries[k]) for k in order]);_verify_equal(entries,read_tensor_file_v2(str(packed)))
  dump=S/(name+'.native.bin');p=subprocess.run(['/root/hp_round9/core_data_v1/weights_dump',str(packed),str(dump)],capture_output=True);assert p.returncode==0,p.stderr.decode();assert sha(dump)==sha(raw),'native sorted tensor bytes differ after reordering'
  changed={};examples=[]
  for key,(dt,a) in entries.items():
   b=ordered_original[key][1];assert a.shape==b.shape and a.dtype==b.dtype;different=int(np.count_nonzero(a.view('u1').reshape(-1)!=b.view('u1').reshape(-1)));changed[str(dt)]=changed.get(str(dt),0)+different
   if different:examples.append({'tensor':key,'dtype':dt,'changed_bytes':different,'elements':a.size})
  if name=='zero_update':assert not any(changed.values())
  old=pathlib.Path('/root/hp_round9/core_export_v2')/(name+'.tfwc2')
  m['models'].append({'name':name,'packed_path':str(packed),'packed_bytes':packed.stat().st_size,'packed_sha256':sha(packed),'original_model_delta_bytes_per_copy':packed.stat().st_size-base.stat().st_size,'gain_vs_sorted_pack_bytes_per_copy':old.stat().st_size-packed.stat().st_size,'native_tensor_identity_sha256':sha(dump),'native_identity_with_previously_decoded_model':True,'packing_seconds':time.monotonic()-start,'changed_bytes_by_dtype':changed,'changed_tensors':examples,'zero_reproduces_original_packed_bytes':name=='zero_update' and sha(packed)==sha(base)});save(name+' original-order exact native model packed')
 m.update(status='COMPLETE_ORIGINAL_ORDER_NATIVE_MODEL_PACKING',finished=time.time(),archive_reuse_contract='all native tensor bytes equal already independently decoded models; no predictor source changes; final warm/package qualification still pending');save('original order packing and native tensor identities verified')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
