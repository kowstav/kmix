"""C/D-selected distributed/selective finetunes: exact V3 model + final CM.

Reuses completed unchanged B/E teacher codecs. Every new candidate gets actual
encoding, independent decoding, trajectory identity and CPU/RSS accounting.
"""
import os,pathlib,json,time,hashlib,traceback,ast,sys,subprocess
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'native_promotion_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/native_promotion_v1');S.mkdir(exist_ok=False)
m={'status':'WAITING_FOR_SELECTIVE_CORE_AND_EXACT_PACKING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'scratch':str(S),'exports':[],'candidates':[]}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('w') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 row={'wall_seconds':time.monotonic()-t,'CPU_seconds':u.ru_utime+u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0,(label,row);return row
try:
 save('reuse running GPU1 selective job; no duplicate fit or native teacher')
 start=time.time()
 while True:
  states={name:json.loads((R/name/'manifest.json').read_text())['status'] for name in ['core_selective_v1','model_order_v3']}
  if any(v=='FAIL' for v in states.values()):raise RuntimeError(states)
  if all(v.startswith('COMPLETE') for v in states.values()):break
  assert time.time()-start<10800;time.sleep(15)
 sys.path.insert(0,'/root/hp_round9/runtime_site_v1');sys.path.insert(0,'/root/hp_round9/restored/src/fx2-cmix-transformer-v1');sys.path.insert(0,str(R));import torch
 from pysrc.export_weights import read_tensor_file,write_tensor_file
 from pysrc.weights_compress import _verify_equal
 from research_round9_native_weight_v3 import write_tensor_file_v3,read_tensor_file_v3
 original=read_tensor_file('/root/hp_round9/core_data_v2/lex_weights.bin');base=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2');ordered_original=read_tensor_file_v3(str(base));order=list(ordered_original)
 distributed=json.loads((R/'core_distributed_v2/manifest.json').read_text());selective=json.loads((R/'core_selective_v1/manifest.json').read_text());assert distributed['status'].startswith('COMPLETE')
 dr=[v for v in distributed['rungs'] if v['step']==384 and v['development']['mode']=='raw'];sr=[v for v in selective['rungs'] if v['step']==384]
 baseline=next(v for v in dr if v['arm']=='raw_unweighted' and v['seed']==7006);winner=min([v for v in dr if v['arm']!='raw_unweighted'],key=lambda v:v['development']['all_bits_per_symbol']);swinner=min(sr,key=lambda v:v['development']['all_bits_per_symbol']);control=next(v for v in sr if v['arm']=='all_high_control' and v['seed']==swinner['seed'])
 chosen=[('distributed_control',baseline),('distributed_CD_winner',winner),('selective_CD_winner',swinner)]
 if swinner['arm']!='all_high_control':chosen.append(('selective_matched_high_lr_control',control))
 m['selection_contract']='freeze using only C/D full original-symbol CE; no E/F value enters selection. All families already have previous E/F observations; no untouched confirmation claim.';m['frozen_candidates']=[{'name':name,**row} for name,row in chosen];m['status']='RUNNING_NATIVE_EXPORT';save('C/D candidates frozen, original V3 codec/native costs used')
 tree=ast.parse((R/'research_round9_core_export_worker.py').read_text());outer=next(n for n in tree.body if isinstance(n,ast.Try));fn=next(n for n in outer.body if isinstance(n,ast.FunctionDef) and n.name=='export');fn.body=fn.body[:next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='packed' for t in n.targets))];fn.body.append(ast.Return(value=ast.Name(id='raw',ctx=ast.Load())));ast.fix_missing_locations(fn);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<exact-shadow-tensor-export-only>','exec'),globals());export_shadow=export
 codecs=json.loads((R/'core_native_codec_v3/manifest.json').read_text());assert codecs['status'].startswith('COMPLETE');T=pathlib.Path(codecs['scratch'])/'tree';binary=T/'cmix';dictionary=T/'dictionary/english.dic';assert sha(binary)==codecs['binary_sha256'];env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1')
 cases={};teachers={}
 for s in 'be':
  teacher=next(v for v in codecs['final_CM_teachers'] if v['slice']==s);root=pathlib.Path(codecs['scratch'])/teacher['name'];data=(root/'input.bin').read_bytes();assert sha(root/'input.bin')==teacher['input_sha256'];assert sha(root/'out.cmx')==teacher['archive_sha256'];cases[s]=data;teachers[s]=teacher
 # Reuse the independently executed native measure function, not its rebuild.
 outer=next(n for n in ast.parse((R/'research_round9_core_native_codec_v3_worker.py').read_text()).body if isinstance(n,ast.Try));fn=next(n for n in outer.body if isinstance(n,ast.FunctionDef) and n.name=='measure');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<same-executed-native-codec-procedure>','exec'),globals())
 for name,row in chosen:
  cp=pathlib.Path(row['checkpoint_path']);assert sha(cp)==row['checkpoint_sha256'];raw=export_shadow(name,cp);canonical=read_tensor_file(str(raw));entries={}
  for key,(dt,a) in canonical.items():
   odt,oa=ordered_original[key]
   if odt==1 and dt==2:
    promoted=(oa.astype(np.uint32)<<16).view('<f4').reshape(a.shape);entries[key]=(odt,oa.copy()) if np.array_equal(a.view('u1'),promoted.view('u1')) else (dt,a)
   else:entries[key]=(dt,a)
  packed=S/(name+'.tfwc3');write_tensor_file_v3(str(packed),[(key,*entries[key]) for key in order]);_verify_equal(entries,read_tensor_file_v3(str(packed)));dump=S/(name+'.native.bin');run(['/root/hp_round9/core_data_v1/weights_dump',str(packed),str(dump)],S,env,name+'_reader');assert sha(dump)==sha(raw)
  m['exports'].append({'name':name,'arm':row['arm'],'seed':row['seed'],'step':row['step'],'checkpoint_sha256':row['checkpoint_sha256'],'packed_path':str(packed),'packed_bytes':packed.stat().st_size,'packed_sha256':sha(packed),'native_tensor_sha256':sha(dump),'model_delta_per_copy':packed.stat().st_size-base.stat().st_size,'native_reader_identity':True});save(name+' exact V3 model cost verified')
  for s,data in cases.items():
   result=measure(name+'_'+s,data,packed,False);result.update(slice=s,arm=row['arm'],seed=row['seed'],gain_vs_original_teacher_bytes=teachers[s]['archive_bytes']-result['archive_bytes'],model_delta_per_copy=packed.stat().st_size-base.stat().st_size);m['candidates'].append(result);save(name+' '+s+' actual final CM and independent decode PASS')
 m.update(status='COMPLETE_CD_SELECTED_NATIVE_MODEL_PRICE_AND_COMBINED_CM_CONFIRMATION',finished=time.time(),full_package_qualified=False);save('new distributed/selective candidates genuinely tested through final coder')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
