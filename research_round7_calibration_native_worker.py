import datetime,hashlib,json,os,pathlib,shutil,subprocess,time,traceback
import numpy as np
import research_round7_lex_finalbit_trace_worker as W
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'calibration_native_v1';assert not D.exists();D.mkdir()
W.DEST=D;W.TREE=pathlib.Path('/root/hp/calibration_native_v1');m={'status':'RUNNING','pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preregistered':'A/B chosen ridge64, frozen512B table; native64K E/F first; all controls/decode exact; no full-package claim','deletions':[],'paid_rental_usd':0};rows=[]
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2));(D/'results.json').write_text(json.dumps(rows,indent=2))
save()
try:
 prior=json.loads((R/'full_stream_regen_v2/manifest.json').read_text());assert prior['status']=='COMPLETE_PREPARATION_ONLY' and prior['reference_dictionary_match'];assert all(x['full2m_identical'] for x in prior['old_slice_offsets'].values())
 m['source']=W.extract_sources();env=dict(os.environ);env['PATH']=W.restore_compiler()
 dec=(W.TREE/'src/coder/decoder.cpp').read_text();enc=(W.TREE/'src/coder/encoder.cpp').read_text();anchor='  const unsigned int p = Discretize(p_->Predict());\n';assert enc.count(anchor)==1 and dec.count(anchor)==1
 header='''#ifndef HP_CALIBRATION_ODDS_H
#define HP_CALIBRATION_ODDS_H
#include <cstdint>
#include <cstdio>
#include <cstdlib>
static unsigned hp_coded_bit_position=0;
static unsigned hp_adjust_final(unsigned p){
 static uint32_t factor[128];static bool initialized=false;
 if(!initialized){for(auto &v:factor)v=1u<<20;
  if(const char *path=std::getenv("LAB_ODDS")){FILE*f=std::fopen(path,"rb");if(!f)std::abort();
   for(auto &v:factor){unsigned char b[4];if(std::fread(b,1,4,f)!=4)std::abort();v=uint32_t(b[0])|(uint32_t(b[1])<<8)|(uint32_t(b[2])<<16)|(uint32_t(b[3])<<24);if(v<800000||v>1400000)std::abort();}
   if(std::fgetc(f)!=EOF)std::abort();std::fclose(f);
  }initialized=true;
 }
 uint32_t f=factor[(hp_coded_bit_position++&7)*16+(p>>12)];
 uint64_t a=uint64_t(p)*f,b=uint64_t(65536-p)*(1u<<20),den=a+b;
 unsigned q=unsigned((a*65536+den/2)/den);return q<1?1:q>65535?65535:q;
}
#endif
'''
 (W.TREE/'src/coder/hp_calibration_odds.h').write_text(header)
 for name,text in [('encoder.cpp',enc),('decoder.cpp',dec)]:
  text='#include "hp_calibration_odds.h"\n'+text.replace(anchor,'  const unsigned int p = hp_adjust_final(Discretize(p_->Predict()));\n');(W.TREE/'src/coder'/name).write_text(text)
 # Same compiler, numerical flags and predictor implementation as verified observer.
 cmd=['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+W.FLAGS,'CFLAGS_TF_DEFINES='+W.TF]
 (D/'build_command.json').write_text(json.dumps(cmd));
 with (D/'build.log').open('x') as log:subprocess.run(cmd,cwd=W.TREE,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
 b=D/'cmix_calibrated';shutil.copy2(W.TREE/'cmix',b);m['binary_bytes']=b.stat().st_size;m['binary_sha256']=W.sha(b);save()
 baseline=R/'lex_finalbit_trace_v1/cmix_trace';weights=R/'lex_audit/lex_h1_run11.tfwc2';assert W.sha(baseline)=='d906d0f2e98c1f5d0d3c1f3ca893b2190750b4bd708b9e001382c7330381c76e'
 table=R/'tiny_residual_v1/odds_0.u32';m['table_sha256']=W.sha(table);save()
 base={k:v for k,v in env.items() if not k.startswith('LAB_')};base.update(LAB_RAW='1',LAB_VOCAB=str(R/'preserved/data/vocab.bm'),LAB_DICT=str(R/'preserved/gen/.dict'),LAB_KEEP_TEMP='1')
 for n in 'ef':
  raw=(R/'full_stream_regen_v2'/(n+'2m.bin')).read_bytes()[:65536];inp=D/(n+'64k.bin');inp.write_bytes(raw);runs={}
  for mode,program in [('reference',baseline),('neutral',b),('candidate',b)]:
   d=D/(n+'_'+mode);d.mkdir();(d/'.dict').symlink_to(R/'preserved/gen/.dict');e={**base,'LAB_COST':str(d/'cost.f32'),'LAB_BITTRACE':str(d/'final_p.u16')}
   if mode=='candidate':e['LAB_ODDS']=str(table)
   runs[mode]=W.timed([str(program),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,e,n+'_'+mode)
  ref,neutral,cand=[D/(n+'_'+s) for s in ['reference','neutral','candidate']];assert (ref/'out.cmx').read_bytes()==(neutral/'out.cmx').read_bytes();rp=np.fromfile(ref/'final_p.u16','<u2');npb=np.fromfile(neutral/'final_p.u16','<u2');cp=np.fromfile(cand/'final_p.u16','<u2');assert np.array_equal(rp,npb)
  f=np.fromfile(table,'<u4').astype(np.uint64);j=np.tile(np.arange(8),len(raw));p=rp.astype(np.uint64);a=p*f[j*16+(p>>12).astype(np.int64)];den=a+(65536-p)*(1<<20);expected=np.clip((a*65536+den//2)//den,1,65535).astype(np.uint16);assert np.array_equal(cp,expected),'Native rational correction mismatch'
  d=D/(n+'_decode');d.mkdir();(d/'.dict').symlink_to(R/'preserved/gen/.dict');runs['decode']=W.timed([str(b),'--transformer',str(weights),str(cand/'out.cmx'),'decoded.bin'],d,{**base,'LAB_ODDS':str(table)},n+'_decode');assert (d/'decoded.bin').read_bytes()==raw
  rc=np.fromfile(ref/'cost.f32','<f4').astype(np.float64);cc=np.fromfile(cand/'cost.f32','<f4').astype(np.float64)
  row={'slice':n,'input_bytes':len(raw),'native_archive_saving_bytes':(ref/'out.cmx').stat().st_size-(cand/'out.cmx').stat().st_size,'ideal_saving_bytes':float((rc-cc).sum()/8),'neutral_archive_exact':True,'neutral_probabilities_exact':True,'candidate_all_bits_match_integer_replay':True,'independent_raw_decode_exact':True,'runtime':runs};rows.append(row);save();print(json.dumps(row),flush=True)
 m['status']='COMPLETE_64K_NATIVE';save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
