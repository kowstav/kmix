"""Repair diagnostics CLI and tensor packing order; reuse successful V1 export.

No trained model is changed. V1 stored rope.cos before rope.inv_freq, preventing
its exact regeneration and bloating the diagnostic container. V2 emits inv_freq
first, then verifies native reader bytes. The native CLI already implemented
neural-only decompression internally, but its validation rejected -d; an isolated
runner patch exposes that existing path and is checked on the unchanged baseline.
"""
import pathlib,json,os,time,hashlib,subprocess,traceback,shutil,sys,ast,importlib.util
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'core_export_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/core_export_v2');S.mkdir(exist_ok=False);OLD=pathlib.Path('/root/hp_round9/core_export_v1');DATA=pathlib.Path('/root/hp_round9/core_data_v2');BASE=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree');T=S/'tree'
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'same selected/trained tensors with ordered compact packing, isolated native neural-only decoder repair and actual codec comparison','spending_usd':0,'deletions':[],'exports':[],'native_candidates':[],'scratch':str(S)}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('w') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 a={'wall_seconds':time.monotonic()-t,'CPU_seconds':u.ru_utime+u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0,(label,a);return a
try:
 old=json.loads((R/'core_export_v1/manifest.json').read_text());assert old['status']=='FAIL';m['original_reference_failure']=old['error'];m['models_unchanged_from_V1']=True
 # An isolated CLI-only repair. All predictor/model source and compile flags stay matched.
 shutil.copytree(BASE,T,symlinks=True,ignore=shutil.ignore_patterns('task_bin'));p=T/'src/runner.cpp';source=p.read_text();source=source.replace("(mode == 'c' || mode == 'n'));","(mode == 'c' || mode == 'n' || mode == 'd'));")
 anchor="if (mode != 'c' && mode != 'n' && mode != 'e' && !enwik9_decompression) {";assert source.count(anchor)==1;source=source.replace(anchor,"if (mode != 'c' && mode != 'n' && mode != 'e' && mode != 'd' && !enwik9_decompression) {")
 source=source.replace('  if (!options.AnySet()) return;','  if (!options.AnySet()) return;\n  if (mode == \'d\' && (options.bytes_only || !options.save_ppmd_bytes.empty() || !options.save_article_boundaries.empty())) UsageError("input extraction flags are compression-only");');p.write_text(source);m['runner_patch_sha256']=sha(p)
 spec=importlib.util.spec_from_file_location('flags','/kaggle/working/hp_round8/research_round8_native_hidden_trace_worker.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.DEST=D;helper.TREE=T;env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env['PATH']=helper.restore_compiler();save('isolated native neural-only decoder interface build')
 m['build_accounting']=run(['make','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+helper.FLAGS,'CFLAGS_TF_DEFINES='+helper.TF],T,env,'compile');binary=T/'cmix';dictionary=T/'dictionary/english.dic';env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1');m['binary_sha256']=sha(binary)
 sys.path.insert(0,'/root/hp_round9/runtime_site_v1');sys.path.insert(0,'/root/hp_round9/restored/src/fx2-cmix-transformer-v1');from pysrc.export_weights import read_tensor_file,write_tensor_file;from pysrc.weights_compress import write_tensor_file_v2,read_tensor_file_v2,_verify_equal
 def compact(name,raw):
  entries=read_tensor_file(str(raw));ordered=sorted(entries,key=lambda key:(key!='rope.inv_freq',key));packed=S/(name+'.tfwc2');start=time.monotonic();write_tensor_file_v2(str(packed),[(key,*entries[key]) for key in ordered]);_verify_equal(entries,read_tensor_file_v2(str(packed)));dump=S/(name+'_native_dump.bin');account=run([str(pathlib.Path('/root/hp_round9/core_data_v1/weights_dump')),str(packed),str(dump)],S,env,name+'_reader');assert sha(dump)==sha(raw);m['exports'].append({'name':name,'raw_sha256':sha(raw),'packed_sha256':sha(packed),'packed_bytes':packed.stat().st_size,'packing_seconds':time.monotonic()-start,'native_tensor_identity':True,'reader_accounting':account});save('ordered compact native tensor identity PASS '+name);return packed
 zero=compact('zero_update',OLD/'zero_update.bin');assert sha(OLD/'zero_update.bin')==sha(DATA/'lex_weights.bin');raw=DATA/'input.bin'
 def decode(name,packed,archive,reference_nn=None):
  C=S/(name+'_decode');C.mkdir();(C/'.dict').symlink_to(dictionary);nnpath=C/'neural.f16';account=run([str(binary),'-d','--transformer-only','--transformer',str(packed),'--save-transformer-probs',str(nnpath),str(archive),'decoded.bin'],C,env,name+'_decode');assert sha(C/'decoded.bin')==sha(raw)
  if reference_nn is not None:assert sha(nnpath)==sha(reference_nn),'native probability observer differs after CLI-only/packing repair'
  return account,nnpath
 save('neutral baseline independent native decode and neural probability identity');da,nnpath=decode('zero_update',zero,DATA/'native_control.cmx',DATA/'native_nn.f16');m['control']={'zero_update_original_tensors_bit_identical':True,'independent_decode_exact':True,'neural_probability_identity':True,'decode_accounting':da};save('neutral native codec gates PASS')
 # Reuse the established export function without executing its failed original worker.
 tree=ast.parse((R/'research_round9_core_export_worker.py').read_text());outer=next(n for n in tree.body if isinstance(n,ast.Try));fn=next(n for n in outer.body if isinstance(n,ast.FunctionDef) and n.name=='export');import torch
 original=read_tensor_file(str(DATA/'lex_weights.bin'));ns={'torch':torch,'np':np,'original':original,'S':S,'m':{'exports':[]},'sha':sha,'save':save,'write_tensor_file':write_tensor_file,'write_tensor_file_v2':write_tensor_file_v2,'_verify_equal':_verify_equal,'read_tensor_file_v2':read_tensor_file_v2,'time':time,'pathlib':pathlib,'run':run,'os':os};fn.body=fn.body[:next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='packed' for t in n.targets))];fn.body.append(ast.Return(value=ast.Name(id='raw',ctx=ast.Load())));ast.fix_missing_locations(fn);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<exact-shadow-export-only>','exec'),ns)
 tokens=np.fromfile(DATA/'tokens.u8','u1');freq=np.fromfile(DATA/'word_frequency.i32','<i4');bounds=np.fromfile(DATA/'bounds.i32','<i4');articles=[(int(a),int(b)) for a,b in zip(bounds[:-1],bounds[1:]) if b-a>=65];ix=np.concatenate([np.arange(a+1,min(b,a+1024)) for a,b in articles[::5]]);target=tokens[ix]
 def cost(nnfile):
  nn=np.memmap(nnfile,'<f2','r',shape=(len(tokens),205));p=np.maximum(nn[ix-1].astype(np.float64),1e-6);p/=p.sum(-1,keepdims=True);loss=-np.log2(p[np.arange(len(ix)),target]);fr=freq[ix];return {'all_bits_per_symbol':float(loss.mean()),'common_or_unlabelled_bits_per_symbol':float(loss[(fr<0)|(fr>=1392)].mean()),'rare_bits_per_symbol':float(loss[(fr>=0)&(fr<1392)].mean()),'targets':len(ix)}
 m['native_development_baseline']=cost(DATA/'native_nn.f16');extension=json.loads((R/'core_extension_v1/manifest.json').read_text())
 for name in ['unweighted','cut107_half','cut1392_zero']:
  checkpoint=next(v for v in extension['rungs'] if v['arm']==name and v['seed']==6506 and v['step']==1152);ckpt=pathlib.Path(checkpoint['checkpoint_path']);assert sha(ckpt)==checkpoint['checkpoint_sha256'];rawweights=OLD/(name+'.bin')
  if not rawweights.exists():rawweights=ns['export'](name,ckpt)
  packed=compact(name,rawweights)
  if name=='unweighted':archive=OLD/'unweighted/out.cmx';nnp=OLD/'unweighted/neural.f16';ea={'reused_successful_V1_native_encode':True,'log':'core_export_v1/unweighted_encode.log'}
  else:
   C=S/name;C.mkdir();(C/'.dict').symlink_to(dictionary);archive=C/'out.cmx';nnp=C/'neural.f16';save(name+' native neural-only encode');ea=run([str(binary),'-n','--transformer-only','--transformer',str(packed),'--save-transformer-probs',str(nnp),str(raw),str(archive)],C,env,name+'_encode')
  da,decode_nn=decode(name,packed,archive,nnp);m['native_candidates'].append({'name':name,'archive_bytes':archive.stat().st_size,'baseline_archive_bytes':DATA.joinpath('native_control.cmx').stat().st_size,'archive_gain_bytes':DATA.joinpath('native_control.cmx').stat().st_size-archive.stat().st_size,'development':cost(nnp),'independent_decode_exact':True,'encode_decode_neural_probability_identity':True,'encode_accounting':ea,'decode_accounting':da,'packed_model_bytes':packed.stat().st_size,'final_combined_CM_qualified':False});save(name+' trained native codec gates PASS')
 m.update(status='COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON',finished=time.time(),full_package_qualified=False);save('selected-core exports actually compress/decompress; final CM and independent corpus remain open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
