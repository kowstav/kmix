"""Corrected neural arithmetic path AND trained weights in the final CM coder.

Historical --transformer-only executes the network but Predict() still returns
PPMD. V3 routes only that diagnostic mode to its observed neural distribution.
Combined CM remains identical at zero update. Every archive gets independent
decoding; the original source/failure/incorrectly named V2 archives are retained.
"""
import pathlib,json,os,time,hashlib,subprocess,traceback,shutil,importlib.util
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'core_native_codec_v3';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/core_native_codec_v3');S.mkdir(exist_ok=False);BASE=pathlib.Path('/root/hp_round9/core_export_v2/tree');T=S/'tree';DATA=pathlib.Path('/root/hp_round9/core_data_v2');WEIGHTS=pathlib.Path('/root/hp_round9/core_export_v2')
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'neural_candidates':[],'final_CM_candidates':[],'scope':'repair diagnostic-only bit law, independently decode, then exact trained weights through combined final CM on three slices','scratch':str(S)}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 start=time.monotonic()
 with (D/(label+'.log')).open('w') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,st,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(st)
 v={'wall_seconds':time.monotonic()-start,'CPU_seconds':u.ru_utime+u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0,(label,v);return v
try:
 export=json.loads((R/'core_export_v2/manifest.json').read_text());assert export['status'].startswith('COMPLETE');shutil.copytree(BASE,T,symlinks=True,ignore=shutil.ignore_patterns('task_bin'))
 p=T/'src/predictor.cpp';src=p.read_text();old='''  if (ppmd_only_ || transformer_only_) {
    float p = byte_model_->Predict()[0];''';assert src.count(old)==1
 new='''  if (transformer_only_) {
    // Context encodes the leading sentinel one followed by known current bits.
    unsigned int prefix=manager_.bit_context_,shift=8;
    for(unsigned int v=prefix;v>1;v>>=1)--shift;
    const unsigned int lo=(prefix<<shift)-256, mid=lo+(1u<<(shift-1)),hi=lo+(1u<<shift);
    float numerator=0,denominator=0;
    for(unsigned int b=mid;b<hi;++b){int ix=byte_to_index_[b];if(ix>=0)numerator+=probs_scratch_[ix];}
    denominator=numerator;
    for(unsigned int b=lo;b<mid;++b){int ix=byte_to_index_[b];if(ix>=0)denominator+=probs_scratch_[ix];}
    float prob=denominator>0?numerator/denominator:0.5f;
    return std::max(0.001f,std::min(0.999f,prob));
  }
  if (ppmd_only_) {
    float p = byte_model_->Predict()[0];''';p.write_text(src.replace(old,new));m['predictor_patch_sha256']=sha(p);m['historical_measurement_correction']='V2 transformer-only archives actually used PPMD bit probabilities; model tensor identity and observed neural losses remain valid, neural archive gains were unmeasured.'
 spec=importlib.util.spec_from_file_location('flags','/kaggle/working/hp_round8/research_round8_native_hidden_trace_worker.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.DEST=D;helper.TREE=T;env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env['PATH']=helper.restore_compiler();save('building corrected diagnostic neural bit predictor')
 m['build_accounting']=run(['make','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+helper.FLAGS,'CFLAGS_TF_DEFINES='+helper.TF],T,env,'compile');binary=T/'cmix';dictionary=T/'dictionary/english.dic';env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1');m['binary_sha256']=sha(binary)
 def measure(name,data,weights,neural):
  C=S/name;C.mkdir();inp=C/'input.bin';inp.write_bytes(data);(C/'.dict').symlink_to(dictionary);archive=C/'out.cmx';nnfile=C/'neural.f16';flags=['--transformer-only'] if neural else [];save(name+' encode');ea=run([str(binary),'-n',*flags,'--transformer',str(weights),'--save-transformer-probs',str(nnfile),str(inp),str(archive)],C,env,name+'_encode');DE=S/(name+'_decode');DE.mkdir();(DE/'.dict').symlink_to(dictionary);save(name+' independent decode');da=run([str(binary),'-d',*flags,'--transformer',str(weights),'--save-transformer-probs',str(DE/'neural.f16'),str(archive),'decoded.bin'],DE,env,name+'_decode');assert DE.joinpath('decoded.bin').read_bytes()==data;assert sha(DE/'neural.f16')==sha(nnfile)
  return {'name':name,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'input_sha256':sha(inp),'neural_probability_sha256':sha(nnfile),'independent_decode_exact':True,'encode_decode_neural_identity':True,'encode_accounting':ea,'decode_accounting':da,'packed_model_bytes':weights.stat().st_size}
 raw=(DATA/'input.bin').read_bytes();zero=WEIGHTS/'zero_update.tfwc2';teacher=measure('neural_teacher',raw,zero,True);assert teacher['neural_probability_sha256']==sha(DATA/'native_nn.f16');assert teacher['archive_bytes']!=(DATA/'native_control.cmx').stat().st_size,'diagnostic unexpectedly still equals PPMD archive';m['neural_teacher']=teacher;save('corrected neural codec independent baseline PASS')
 for name in ['unweighted','cut107_half','cut1392_zero']:
  row=measure('neural_'+name,raw,WEIGHTS/(name+'.tfwc2'),True);row['gain_vs_neural_teacher_bytes']=teacher['archive_bytes']-row['archive_bytes'];m['neural_candidates'].append(row);save(name+' corrected neural archive measured')
 # First A slice matches the previous full-CM baseline byte for byte, despite
 # the diagnostic-only source change. B/E are fresh for these core candidates.
 cases={'a':raw[:65536]}
 for s in ['b','e']:
  q=pathlib.Path('/kaggle/working/hp_round8/atom_cache_v1/b512k.bin') if s=='b' else pathlib.Path('/kaggle/working/hp_round8/source_wide_confirmation_v1/e512k/input.bin');cases[s]=q.read_bytes()[:65536]
 for s,data in cases.items():
  teacher=measure('final_'+s+'_teacher',data,zero,False)
  if s=='a':assert (S/'final_a_teacher/out.cmx').read_bytes()==pathlib.Path('/root/hp_round9/literal_split_v1/baseline/out.cmx').read_bytes(),'diagnostic repair changed original combined CM'
  m.setdefault('final_CM_teachers',[]).append({'slice':s,**teacher});save(s+' original combined CM neutral PASS')
  for name in ['unweighted','cut107_half','cut1392_zero']:
   row=measure('final_'+s+'_'+name,data,WEIGHTS/(name+'.tfwc2'),False);row.update(slice=s,model=name,gain_vs_native_teacher_bytes=teacher['archive_bytes']-row['archive_bytes'],model_delta_bytes_per_copy=row['packed_model_bytes']-2978039);m['final_CM_candidates'].append(row);save(name+' '+s+' actual final coder result')
 m.update(status='COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS',finished=time.time(),full_package_qualified=False,scope_limits='A/B/E64KiB cold, A previously seen; B/E held out from selected-core training but viewed by other branches; model bytes priced per copy, final self-contained package and fullwarm/resources remain pending');save('all diagnostic and actual combined-CM model tests complete')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
