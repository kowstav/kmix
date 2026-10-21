"""Constants-first factorization without coding known literal/mask bytes twice.

The independently coded side stream supplies positions and original bytes. The
native coder Predict/Perceive-updates every known bit but does not modify the
arithmetic interval. Compare original context with masked context, and a trained
common specialist if its compact native export becomes available. Whole-word
frequency is used by the encoder only; all decoding choices are paid in side.
"""
import pathlib,json,os,time,traceback,hashlib,subprocess,shutil,ast,importlib.util,zlib,struct
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'known_literals_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/known_literals_v1');S.mkdir(exist_ok=False);DATA=pathlib.Path('/root/hp_round9/core_data_v2');BASE=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree');T=S/'tree'
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'priced known-literal bypass, original/masked context and common-specialist combination under actual native CM','spending_usd':0,'deletions':[],'candidates':[],'scratch':str(S)}
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
 old=json.loads((R/'literal_split_v1/manifest.json').read_text());assert old['status'].startswith('COMPLETE');m['literal_split_reference_sha256']=sha(R/'literal_split_v1/manifest.json');m['worker_sha256']=sha(R/'research_round9_known_literals_worker.py')
 shutil.copytree(BASE,T,symlinks=True,ignore=shutil.ignore_patterns('task_bin'));p=T/'src/runner.cpp';source=p.read_text()
 helpercode='''
class HPKnownBytes {
  FILE *mask_=nullptr,*values_=nullptr;
 public:
  HPKnownBytes() {
    const char *mask=std::getenv("HP_KNOWN_MASK"),*values=std::getenv("HP_KNOWN_VALUES");
    if(bool(mask)!=bool(values)) std::abort();
    if(mask){mask_=std::fopen(mask,"rb");values_=std::fopen(values,"rb");if(!mask_||!values_)std::abort();}
  }
  bool Next(unsigned char *value) {
    if(!mask_)return false;
    const int flag=std::getc(mask_),v=std::getc(values_);
    if((flag!=0&&flag!=1)||v<0||(flag==0&&v!=0))std::abort();
    *value=static_cast<unsigned char>(v);return flag==1;
  }
  ~HPKnownBytes(){if(mask_){if(std::getc(mask_)!=EOF||std::getc(values_)!=EOF)std::abort();std::fclose(mask_);std::fclose(values_);}}
};
'''
 anchor='void Compress(unsigned long long input_bytes,';assert source.count(anchor)==1;source=source.replace(anchor,helpercode+'\n'+anchor)
 source=source.replace('  Encoder e(os, p);','  Encoder e(os, p);\n  HPKnownBytes known;')
 oldloop='''      for (int j = 7; j >= 0; --j) {
        e.Encode((c>>j)&1);
      }'''
 newloop='''      unsigned char known_byte=0;
      if(known.Next(&known_byte)) {if(c!=known_byte)std::abort();e.ObserveKnownByte(c);}
      else for (int j = 7; j >= 0; --j) {
        e.Encode((c>>j)&1);
      }'''
 assert source.count(oldloop)==1;source=source.replace(oldloop,newloop).replace('  Decoder d(is, p);','  Decoder d(is, p);\n  HPKnownBytes known;')
 oldloop='''    int byte = 1;
    while (byte < 256) {
      byte += byte + d.Decode();
    }
    os->put(byte);'''
 newloop='''    unsigned char known_byte=0;
    int byte = 1;
    if(known.Next(&known_byte)){d.ObserveKnownByte(known_byte);byte=known_byte;}
    else while (byte < 256) {
      byte += byte + d.Decode();
    }
    os->put(byte);'''
 assert source.count(oldloop)==1;p.write_text(source.replace(oldloop,newloop));m['runner_source_sha256']=sha(p)
 spec=importlib.util.spec_from_file_location('flags','/kaggle/working/hp_round8/research_round8_native_hidden_trace_worker.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.DEST=D;helper.TREE=T;env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','HP_KNOWN_'))};env['PATH']=helper.restore_compiler();save('building exact native known-symbol bypass')
 m['build_accounting']=run(['make','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+helper.FLAGS,'CFLAGS_TF_DEFINES='+helper.TF],T,env,'compile');binary=T/'cmix';dictionary=T/'dictionary/english.dic';weights=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2');env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1');m['binary']={'sha256':sha(binary),'bytes':binary.stat().st_size,'lab_delta_vs_teacher':binary.stat().st_size-(BASE/'cmix').stat().st_size}
 # Reuse only the existing reversible side-stream functions.
 module=ast.parse((R/'research_round9_literal_split_worker.py').read_text());fs=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['vint','getv','split','restore']];ns={'np':np,'struct':struct,'zlib':zlib};exec(compile(ast.Module(body=fs,type_ignores=[]),'<side-codec-only>','exec'),ns);split=ns['split'];restore=ns['restore']
 raw=(DATA/'input.bin').read_bytes()[:65536];freq=np.fromfile(DATA/'word_frequency.i32','<i4')[:len(raw)];m['baseline']=old['baseline'];baseline=pathlib.Path('/root/hp_round9/literal_split_v1/baseline/out.cmx');m['contract']={'word_filter':'same full literal/OOV/body-word supervision as loss-mask pilot; positions and bytes paid in independent side stream','known_bits':'native Predict and Perceive still execute for each bit; arithmetic interval is unchanged','raw_context':'insert original side-supplied literal bytes into decoded history; no redacted context penalty','mask_context':'feed known spaces and restore original rare bytes after main decode','side_causality':'unknown known-values file entries are required to be zero; only side-supplied literals enter decoder','streaming':'native known-byte helper reads sequential files in constant memory; prototype Python side preparation is small65KiB, full production side parser/loader pending','artifact_price':'13B container + compressed side + actual native main archive; lab executable delta and weight delta recorded, full packaged decoder still pending','models':'unchanged selected core and one already-trained1392zero common specialist','confirmation':'previously viewed early65KiB prefix; independent corpus required'}
 def measure(name,data,mask,values,model,side=None,raw_context=True):
  C=S/name;C.mkdir();(C/'.dict').symlink_to(dictionary);inp=C/'input.bin';inp.write_bytes(data);mp=C/'mask.u8';vp=C/'values.u8';mask.astype('u1').tofile(mp);values.astype('u1').tofile(vp);ee={**env,'HP_KNOWN_MASK':str(mp),'HP_KNOWN_VALUES':str(vp)};archive=C/'out.cmx';hidden=C/'hidden.q8';save(name+' native known-symbol encode');ea=run([str(binary),'-n','--transformer',str(model),str(inp),str(archive)],C,{**ee,'LAB_HIDDENTRACE':str(hidden)},name+'_encode');DE=S/(name+'_decode');DE.mkdir();(DE/'.dict').symlink_to(dictionary);decodehidden=DE/'hidden.q8';da=run([str(binary),'-d','--transformer',str(model),str(archive),'decoded.bin'],DE,{**ee,'LAB_HIDDENTRACE':str(decodehidden)},name+'_decode');assert (DE/'decoded.bin').read_bytes()==data and sha(hidden)==sha(decodehidden)
  if side is None:assert archive.read_bytes()==baseline.read_bytes();return hidden
  restored=(DE/'decoded.bin').read_bytes() if raw_context else restore(DE.joinpath('decoded.bin').read_bytes(),side);assert restored==raw;packed=S/(name+'.hpknown');packed.write_bytes(b'HPKNOWN1'+bytes([0 if raw_context else 1])+struct.pack('<I',len(side))+side+archive.read_bytes());return {'name':name,'native_main_bytes':archive.stat().st_size,'side_bytes':len(side),'container_bytes':packed.stat().st_size,'gain_vs_original_native_before_new_package_bytes':baseline.stat().st_size-packed.stat().st_size,'independent_decode_and_restore_exact':True,'encode_decode_hidden_identity':True,'hidden_sha256':sha(hidden),'selected_model_bytes':model.stat().st_size,'model_delta_bytes_per_copy':model.stat().st_size-weights.stat().st_size,'encode_accounting':ea,'decode_accounting':da}
 zero=np.zeros(len(raw),'u1');neutral_hidden=measure('neutral_all_unknown',raw,zero,zero,weights);m['neutral']={'archive_identity':True,'independent_decode_exact':True,'encoder_decoder_hidden_identity':True,'hidden_sha256':sha(neutral_hidden)};save('all-unknown exact neutral native gates PASS')
 for cutoff in [107,1392,8372]:
  main,side,spans,nbytes=split(raw,freq,cutoff);mask=(freq>=0)&(freq<cutoff);values=np.where(mask,np.frombuffer(raw,'u1'),0);row=measure('raw_context_cut'+str(cutoff),raw,mask,values,weights,side,True);assert row['hidden_sha256']==sha(neutral_hidden),'known original literals changed native core trajectory';row.update(cutoff=cutoff,known_bytes=nbytes,raw_context_preserves_original_hidden=True);m['candidates'].append(row);save('raw-context '+str(cutoff)+' native gates PASS')
 cutoff=1392;main,side,spans,nbytes=split(raw,freq,cutoff);mask=(freq>=0)&(freq<cutoff);values=np.where(mask,32,0);row=measure('masked_context_cut1392',main,mask,values,weights,side,False);row.update(cutoff=cutoff,known_bytes=nbytes);m['candidates'].append(row);save('masked-context known-space gates PASS')
 candidate=pathlib.Path('/root/hp_round9/core_export_v2/cut1392_zero.tfwc2');save('waiting for exact native common-specialist export, reuse existing training')
 waitstart=time.time()
 while not candidate.exists():
  manifest=json.loads((R/'core_export_v2/manifest.json').read_text())
  if manifest['status']=='FAIL':raise RuntimeError(manifest['error'])
  assert time.time()-waitstart<3600,'export still unavailable after1hour';time.sleep(15)
 # A file existing during compression is not sufficient: wait for reader identity.
 while True:
  manifest=json.loads((R/'core_export_v2/manifest.json').read_text())
  if any(v['name']=='cut1392_zero' and v['native_tensor_identity'] for v in manifest.get('exports',[])):break
  if manifest['status']=='FAIL':raise RuntimeError(manifest['error'])
  time.sleep(15)
 values=np.where(mask,np.frombuffer(raw,'u1'),0);row=measure('raw_context_cut1392_common_specialist',raw,mask,values,candidate,side,True);row.update(cutoff=cutoff,known_bytes=nbytes);m['candidates'].append(row);m.update(status='COMPLETE_PRICED_KNOWN_LITERAL_BYPASS_AND_COMMON_SPECIALIST_NATIVE_SCREEN',finished=time.time(),full_package_qualified=False);save('known constants/contexts/common-specialist combinations actually tested; full package and independent corpus remain open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
