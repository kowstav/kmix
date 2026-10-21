from pathlib import Path
p=Path('research_round9_word_softmax_worker.py');s=p.read_text(encoding='utf-8');a=s.index('def load(s):');b=s.index('class Model',a)
new='''def load(s):
 base=R/'atom_cache_v1';root=(R/'native_stage_trace_v1' if s in 'ab' else R/'native_stage_weak_confirmation_v1' if s in 'cd' else R/'source_wide_confirmation_v1')/(s+'512k');rawpath=base/(s+'512k.bin') if s in 'abcd' else root/'input.bin';raw=np.frombuffer(rawpath.read_bytes(),'u1').copy();pp=base/(s+'_native/final_p.u16') if s in 'abcd' else root/'final_p.u16';hp=base/(s+'_native/hidden.q8') if s in 'abcd' else root/'hidden.q8'
 native_int=np.fromfile(pp,'<u2');native_p=native_int.reshape(-1,8).astype(np.float32)/65536;h=np.memmap(hp,'u1','r',shape=(len(raw),193));valid=np.r_[0,h[:-1,0]].astype(np.float32);history=np.vstack([np.zeros((1,192)),np.asarray(h[:-1,1:],np.float32)/127.5-1]);history*=valid[:,None];node,active=parse_nodes(raw,s,nodes);active*=valid;bits=((raw[:,None]>>(7-np.arange(8)))&1).astype(np.float32)
 ell=np.log(native_int.astype(np.float64)/(65536-native_int.astype(np.float64)));st=np.memmap(root/'stage.f32','<f4','r',offset=12,shape=(len(native_int),19));nn=np.clip(st[:,17].astype(np.float64),1/65536,65535/65536);feat=((np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*np.repeat(valid,8)).astype(np.float64);theta=np.array([.0016181118716570748,-.007454085408717222,2.3818512619982752],dtype=np.float64);dot=theta[0]+theta[1]*ell+theta[2]*feat;experts=np.column_stack([native_int,*[np.clip(np.floor(65536*expit(ell+scale*dot)+.5),1,65535).astype('<u2') for scale in [.5,1.,1.5,2.]]]);q=replay(experts,bits.reshape(-1).astype('u1'),2.6441431586476938e-06)[0];p=q.reshape(-1,8).astype(np.float32)/65536
 m.setdefault('inputs',[]).append({'slice':s,'raw_sha256':sha(rawpath),'native_p_sha256':sha(pp),'hidden_sha256':sha(hp),'adaptive_Q16_sha256':hashlib.sha256(q.tobytes()).hexdigest()});return {'history':history.astype(np.float32),'node':node,'active':active,'raw':raw.astype(np.int64),'p':p,'native_p':native_p,'y':bits}
'''
s=s[:a]+new+s[b:];s=s.replace('model.eval();gain=0.;qh=','model.eval();gain=nativegain=0.;qh=')
old="gain+=float(np.log2(sel/np.where(y,p,65536-p)).sum()/8);qh.update(q.tobytes())"
new="gain+=float(np.log2(sel/np.where(y,p,65536-p)).sum()/8);np0=rec['native_p'][lo:hi].astype(np.float64)*65536;nativegain+=float(np.log2(sel/np.where(y,np0,65536-np0)).sum()/8);qh.update(q.tobytes())"
assert s.count(old)==1;s=s.replace(old,new).replace("gain+rec['adaptive_gain_vs_native_bytes']","nativegain")
anchor="torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;"
assert s.count(anchor)==1
s=s.replace(anchor,"from numba import njit\n from scipy.special import expit\n replay_tree=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());replay_nodes=[n for n in replay_tree.body if isinstance(n,ast.FunctionDef) and n.name=='replay'];namespace={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=replay_nodes,type_ignores=[]),'<frozen-adaptive-replay>','exec'),namespace);replay=namespace['replay']\n "+anchor)
s=s.replace("'objective':'ordinary full-bit native-relative mixture loss; no rare masks'","'objective':'ordinary full-bit adaptive-relative mixture loss; no rare masks'")
s=s.replace("'mixture':'nonnegative context gate capped.1 with native integer law, gated previous valid hidden; no target/oracle routing'","'mixture':'nonnegative context gate capped.1 with frozen causal scaled5H262144 adaptive integer law, gated previous valid hidden; no target/oracle routing'")
s=s.replace("rows.sort(key=lambda v:v['development']['gain_vs_native_bytes']","rows.sort(key=lambda v:v['development']['gain_vs_adaptive_bytes']")
p.write_text(s,encoding='utf-8')
