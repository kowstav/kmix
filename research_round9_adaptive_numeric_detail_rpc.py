import pathlib,json,subprocess,ast,math
import numpy as np
from scipy.special import expit
from numba import njit
R=pathlib.Path('/kaggle/working/hp_round9');S=pathlib.Path('/root/hp_round9/adaptive_strict_v1');T=pathlib.Path('/root/hp_round9/adaptive_native_v1/g_teacher')
h=(S/'hp_adaptive_law.h').read_text().replace(' private:',' public:')
(S/'detail.h').write_text(h)
c=(S/'hp_adaptive_law.cpp').read_text().replace('#include "hp_adaptive_law.h"','#include "detail.h"').replace('#include "research_round9_adaptive_law.h"','#include "detail.h"').replace('HPCausalAdaptive law;','HPCausalAdaptive law; FILE*ed=std::fopen("experts.u16","wb");').replace('law.Observe((ch>>b)&1);','for(int k=0;k<5;k++){uint16_t e=law.experts_[k];std::fwrite(&e,2,1,ed);} law.Observe((ch>>b)&1);').replace('std::fclose(out);','std::fclose(out);std::fclose(ed);')
(S/'detail.cpp').write_text(c)
subprocess.run(['clang++-17','-O3','-std=c++17','-march=x86-64-v3','-mrecip=none','-ffp-contract=off','-DHP_ADAPTIVE_REPLAY_MAIN','detail.cpp','-o','detail'],cwd=S,check=True)
subprocess.run([str(S/'detail'),*[str(T/p) for p in ['input.bin','final_p.u16','hidden.q8','stage.f32']],str(S/'detail_q.u16')],cwd=S,check=True)
p=np.fromfile(T/'final_p.u16','<u2');ell=np.log(p.astype(np.float64)/(65536-p.astype(np.float64)));hidden=np.memmap(T/'hidden.q8','u1','r',shape=(len(p)//8,193));valid=np.repeat(np.r_[0,hidden[:-1,0]],8);stage=np.memmap(T/'stage.f32','<f4','r',offset=12,shape=(len(p),19));nn=np.clip(stage[:,17].astype(np.float64),1/65536,65535/65536);feat=(np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*valid
cpp=np.fromfile(S/'experts.u16','<u2').reshape(-1,5);rows=[]
for mode in ['original_numpy','explicit_float64']:
 f=feat if mode=='original_numpy' else feat.astype(np.float64)
 dot=.0016181118716570748-.007454085408717222*ell+2.3818512619982752*f
 ex=np.column_stack([p,*[np.clip(np.floor(65536*expit(ell+a*dot)+.5),1,65535).astype('<u2') for a in [.5,1.,1.5,2.]]]);ix=np.argwhere(ex!=cpp)
 rows.append({'mode':mode,'features_dtype':str(feat.dtype),'valid_dtype':str(valid.dtype),'delta_dtype':str(dot.dtype),'expert_unequal_events':len(ix),'first_mismatches':[{'index':int(i),'expert':int(k),'python':int(ex[i,k]),'CPP':int(cpp[i,k]),'ell':float(ell[i]),'feat':float(feat[i])} for i,k in ix[:10]]})
(R/'adaptive_strict_v1/numeric_detail.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
