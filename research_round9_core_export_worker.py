"""Round-trip selected-core checkpoint exports through the actual native reader.

Zero update must reproduce every original tensor bit. Trained candidates are
then measured by the native neural codec; GPU likelihood is never substituted
for this test. This is not yet the combined final CM codec or full-corpus test.
"""
import os,sys,pathlib,json,hashlib,time,traceback,subprocess,struct
os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,torch
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'core_export_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/core_export_v1');S.mkdir(exist_ok=False);DATA=pathlib.Path('/root/hp_round9/core_data_v2');T=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'exact selected-core export plus native neural-only masking comparison, final CM qualification open','spending_usd':0,'deletions':[],'exports':[],'native_candidates':[],'scratch':str(S)}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 start=time.monotonic()
 with (D/(label+'.log')).open('w') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 row={'wall_seconds':time.monotonic()-start,'CPU_seconds':u.ru_utime+u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0,(label,row);return row
try:
 sys.path.insert(0,'/root/hp_round9/runtime_site_v1');sys.path.insert(0,'/root/hp_round9/restored/src/fx2-cmix-transformer-v1')
 from pysrc.export_weights import read_tensor_file,write_tensor_file
 from pysrc.weights_compress import write_tensor_file_v2,read_tensor_file_v2,_verify_equal
 original=read_tensor_file(str(DATA/'lex_weights.bin'));m['actual_original_tensors_sha256']=sha(DATA/'lex_weights.bin')
 def export(name,ckpt,zero=False):
  state=torch.load(ckpt,map_location='cpu',weights_only=False)['model'];out={};changes=[]
  for key,(dtype,arr) in original.items():
   value=arr.copy()
   if key in state and dtype==2:value=state[key].detach().numpy().astype('<f4').reshape(arr.shape)
   elif key.endswith('.q') and key[:-2] in state:
    base=key[:-2];w=state[base].detach().numpy().astype(np.float64);sc=original[base+'.scale'][1];scale=((sc.astype(np.uint32)<<16).view('<f4')).astype(np.float64).reshape(-1,1)
    cb=original.get(base+'.codebook')
    if cb is not None:
     levels=cb[1].astype(np.float64);normalized=w/(scale*.25);ix=np.searchsorted(levels,normalized);lo=np.clip(ix-1,0,len(levels)-1);hi=np.clip(ix,0,len(levels)-1);nearest=np.where(np.abs(normalized-levels[lo])<=np.abs(normalized-levels[hi]),lo,hi);value=(nearest-7).astype('i1').reshape(arr.shape)
    else:value=np.clip(np.rint(w/scale),-127,127).astype('i1').reshape(arr.shape)
   assert value.shape==arr.shape and value.dtype==arr.dtype,key
   count=int(np.count_nonzero(value.view('u1').reshape(-1)!=arr.view('u1').reshape(-1)))
   if count:changes.append({'tensor':key,'changed_bytes':count})
   out[key]=(dtype,value)
  if zero:assert not changes,changes
  raw=S/(name+'.bin');write_tensor_file(str(raw),[(k,dt,a) for k,(dt,a) in out.items()]);assert not zero or sha(raw)==sha(DATA/'lex_weights.bin')
  packed=S/(name+'.tfwc2');save('packing exact native export '+name);packstart=time.monotonic();write_tensor_file_v2(str(packed),[(k,dt,a) for k,(dt,a) in out.items()]);_verify_equal(out,read_tensor_file_v2(str(packed)));packseconds=time.monotonic()-packstart
  dump=S/(name+'_native_dump.bin');account=run([str(pathlib.Path('/root/hp_round9/core_data_v1/weights_dump')),str(packed),str(dump)],S,os.environ,name+'_native_reader');assert sha(dump)==sha(raw),'actual native reader changed exported tensors'
  row={'name':name,'checkpoint_path':str(ckpt),'checkpoint_sha256':sha(ckpt),'zero_update_original_tensor_identity':zero,'changed_tensors':changes,'raw_sha256':sha(raw),'packed_sha256':sha(packed),'packed_bytes':packed.stat().st_size,'packing_seconds':packseconds,'native_reader_tensor_identity':True,'reader_accounting':account};m['exports'].append(row);save('native tensor roundtrip PASS '+name);return packed
 zero=pathlib.Path('/root/hp_round9/preserved_core_training_v2/selected_core_zero_update.pt');export('zero_update',zero,True)
 extension=json.loads((R/'core_extension_v1/manifest.json').read_text());m['frozen_candidates']=['unweighted','cut107_half','cut1392_zero'];m['selection_contract']='seed6506 step1152; representative full-loss winner, light mask and zero-loss stress; selected before native measurement, development corpus reused'
 original_nn=np.memmap(DATA/'native_nn.f16','<f2','r',shape=(262138,205));tokens=np.fromfile(DATA/'tokens.u8','u1');freq=np.fromfile(DATA/'word_frequency.i32','<i4');bounds=np.fromfile(DATA/'bounds.i32','<i4');articles=[(int(a),int(b)) for a,b in zip(bounds[:-1],bounds[1:]) if b-a>=65];dev=articles[::5];ix=np.concatenate([np.arange(a+1,min(b,a+1024)) for a,b in dev]);target=tokens[ix];raw=DATA/'input.bin';dictionary=T/'dictionary/english.dic';env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1')
 def devcost(nn):
  p=np.maximum(nn[ix-1].astype(np.float64),1e-6);p/=p.sum(-1,keepdims=True);loss=-np.log2(p[np.arange(len(ix)),target]);fr=freq[ix];return {'all_bits_per_symbol':float(loss.mean()),'common_or_unlabelled_bits_per_symbol':float(loss[(fr<0)|(fr>=1392)].mean()),'rare_bits_per_symbol':float(loss[(fr>=0)&(fr<1392)].mean()),'targets':len(ix)}
 m['native_development_baseline']=devcost(original_nn)
 for name in m['frozen_candidates']:
  row=next(v for v in extension['rungs'] if v['arm']==name and v['seed']==6506 and v['step']==1152);ckpt=pathlib.Path(row['checkpoint_path']);assert sha(ckpt)==row['checkpoint_sha256'];packed=export(name,ckpt);C=S/name;C.mkdir();(C/'.dict').symlink_to(dictionary);out=C/'out.cmx';nnpath=C/'neural.f16';save('native neural codec candidate '+name)
  ea=run([str(T/'cmix'),'-n','--transformer-only','--transformer',str(packed),'--save-transformer-probs',str(nnpath),str(raw),str(out)],C,env,name+'_encode');assert nnpath.stat().st_size==DATA.joinpath('native_nn.f16').stat().st_size
  DE=S/(name+'_decode');DE.mkdir();(DE/'.dict').symlink_to(dictionary);da=run([str(T/'cmix'),'-d','--transformer-only','--transformer',str(packed),str(out),'decoded.bin'],DE,env,name+'_decode');assert sha(DE/'decoded.bin')==sha(raw)
  cost=devcost(np.memmap(nnpath,'<f2','r',shape=(len(tokens),205)));m['native_candidates'].append({'name':name,'neural_only_archive_bytes':out.stat().st_size,'baseline_neural_only_archive_bytes':DATA.joinpath('native_control.cmx').stat().st_size,'archive_gain_bytes':DATA.joinpath('native_control.cmx').stat().st_size-out.stat().st_size,'development':cost,'encode_accounting':ea,'decode_accounting':da,'independent_decode_exact':True,'native_combined_final_CM_test':False});save('native neural-only encode/decode PASS '+name)
 m.update(status='COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON',finished=time.time(),final_CM_or_full_package_qualified=False);save('actual core finetuning exports evaluated natively; final CM and independent corpus gates pending')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
