"""Queued true-prior, native/GPU control and frozen-capacity pilot; no SGD.

Uses one native process after the two-process recovery completes. Results are
sample neural diagnostics, never a full archive or an optimum claim.
"""
import pathlib,os,sys,subprocess,time,json,hashlib,traceback,gc
out=pathlib.Path('/kaggle/working/hp_round7');pre=out/'preserved'
dest=out/'frozen_logits_pilot';dest.mkdir(exist_ok=False)
work=pathlib.Path('/root/hp/frozen_logits_pilot');work.mkdir(exist_ok=False)
print('WAITING_FOR_EXISTING_NATIVE_RECOVERY',flush=True)
for _ in range(2880):
    text=(out/'lex_native_2m_recovery_controller.log').read_text()
    if 'Traceback' in text:raise RuntimeError('Native recovery failed; inspect saved evidence before pilot')
    if 'LEX_NATIVE_2M_RECOVERY_COMPLETE' in text:break
    time.sleep(5)
else:raise RuntimeError('Four-hour bounded wait expired')
assert 'cmix_round7_' not in '\n'.join(x for x in subprocess.check_output(['ps','-eo','args'],text=True).splitlines() if '/cmix_round7_' in x),'Another native experiment is active; inspect before pilot'
result={'scope':'65536-symbol cold A-prefix neural diagnostic; full native probabilities and true float16 PPMD priors; not a full package, model optimum or20% claim',
        'neural_training':False,'paid_rental_usd':0,'deletions':[],'models':[]}
def save():
    tmp=dest/'results.json.tmp';tmp.write_text(json.dumps(result,indent=2));tmp.replace(dest/'results.json')
try:
    import numpy as np
    binary=out/'cmix_round7_v5';weights=out/'reference.fx2tfwc5';binary.chmod(binary.stat().st_mode|0o111)
    inp=work/'input.bin';raw=(pre/'slices/a2m.bin').read_bytes()[:65536];inp.write_bytes(raw)
    (work/'.dict').symlink_to(pre/'gen/.dict')
    env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(pre/'data/vocab.bm'),'LAB_DICT':str(pre/'gen/.dict'),'LAB_KEEP_TEMP':'1'}
    for k in ['LAB_COST','LAB_FINAL_P','LAB_FINALMIX','LAB_UNIFORM_NN','LAB_SX']:env.pop(k,None)
    args=[str(binary),'-n','--transformer-only','--transformer',str(weights),
          '--save-transformer-probs',str(work/'native_nn.f16'),'--save-ppmd-probs',str(work/'priors.f16'),
          '--save-ppmd-bytes',str(work/'tokens.u8'),'--save-article-boundaries',str(work/'bounds.i32'),str(inp),'native_neural_only.cmx']
    log=(dest/'native_control.log').open('w');started=time.monotonic()
    p=subprocess.Popen(args,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT);pid,status,usage=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status);log.close()
    result['native_control']={'returncode':p.returncode,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'max_rss_kbytes':usage.ru_maxrss,
        'wall_seconds':time.monotonic()-started,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
        'weights_sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(raw).hexdigest()}
    save();assert p.returncode==0,'Native probability/prior generation failed'
    N=len(raw);V=205
    tokens=np.fromfile(work/'tokens.u8','u1').astype(np.int64);assert tokens.size==N
    prior=np.fromfile(work/'priors.f16','<f2').reshape(N,V);native=np.fromfile(work/'native_nn.f16','<f2').reshape(N,V)
    bounds=np.fromfile(work/'bounds.i32','<i4').astype(np.int64);assert bounds[0]==0 and bounds[-1]==N and np.all(np.diff(bounds)>0)
    result['data_contract']={'input_bytes':N,'prior_source':'Actual native PPMD after completed byte, IEEE float16, full205 columns; no sparse threshold or neural/uniform substitute',
        'boundaries':bounds.tolist(),'prior_sha256':hashlib.sha256((work/'priors.f16').read_bytes()).hexdigest(),'native_neural_sha256':hashlib.sha256((work/'native_nn.f16').read_bytes()).hexdigest()};save()
    sys.path.insert(0,'/root/hp/round7_runtime_site');sys.path.insert(0,'/root/hp/tools')
    import torch,tfh
    torch.set_num_threads(1);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.set_float32_matmul_precision('highest')
    def bits(rows):
        q=np.maximum(rows[:-1].astype(np.float64),1e-6);q/=q.sum(axis=1,keepdims=True)
        return -np.log2(q[np.arange(N-1),tokens[1:]])
    native_bits=bits(native);native_clamped=np.maximum(native.astype(np.float64),1e-6);native_clamped/=native_clamped.sum(axis=1,keepdims=True)
    # The actual stronger checkpoint receives its own native prior dump.
    # Compare neural likelihoods only if the supplied priors match exactly.
    lex_binary=out/'cmix_round7_lex_codebook';lex_weights=out/'lex_audit/lex_h1_run11.tfwc2'
    lex_args=[str(lex_binary),'-n','--transformer-only','--transformer',str(lex_weights),
              '--save-transformer-probs',str(work/'lex_native_nn.f16'),'--save-ppmd-probs',str(work/'lex_priors.f16'),str(inp),'lex_neural_only.cmx']
    log=(dest/'lex_native_control.log').open('w');started=time.monotonic()
    p=subprocess.Popen(lex_args,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT);pid,status,usage=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status);log.close()
    result['lex_native_control']={'returncode':p.returncode,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'max_rss_kbytes':usage.ru_maxrss,
                                 'wall_seconds':time.monotonic()-started,'binary_sha256':hashlib.sha256(lex_binary.read_bytes()).hexdigest(),'weights_sha256':hashlib.sha256(lex_weights.read_bytes()).hexdigest()}
    save();assert p.returncode==0,'Stronger native neural control failed'
    lex_native=np.fromfile(work/'lex_native_nn.f16','<f2').reshape(N,V);lex_bits=bits(lex_native)
    result['lex_native_control'].update(priors_bit_exact_with_reference=(work/'lex_priors.f16').read_bytes()==(work/'priors.f16').read_bytes(),
                                       mean_neural_bits_per_symbol=float(lex_bits.mean()),summed_neural_bits=float(lex_bits.sum()),
                                       native_neural_only_archive_bytes=(work/'lex_neural_only.cmx').stat().st_size)
    lex_bits.astype('<f4').tofile(dest/'lex_native_true_bits.f32');native_bits.astype('<f4').tofile(dest/'reference_native_true_bits.f32');save()
    for name in ['6m-q4-fp32.tch','8m.tch','10m.tch']:
        if name!='6m-q4-fp32.tch' and not result.get('control_parity_gate_passed',False):break
        sd=torch.load(tfh.REPO+'/models/'+name,map_location='cpu',weights_only=True)
        if all(k.startswith('_orig_mod.') for k in sd):sd={k[len('_orig_mod.'):]:v for k,v in sd.items()}
        nl=1+max(int(k.split('.')[1]) for k in sd if k.startswith('blocks.'));d=sd['embedding.weight'].shape[1]
        cfg=tfh.make_config(quantized=name=='6m-q4-fp32.tch',n_layers=nl,attention_weight_sharing_pattern=list(range(nl)),mlp_weight_sharing_pattern=list(range(nl)),
                           d_model=d,d_mlp=4*d,n_query_heads=d//64,n_key_value_heads=d//64,kimi_linear_n_heads=d//64,kimi_linear=[True,True,True,False]*(nl//4))
        model=tfh.Transformer(cfg);model.load_state_dict(sd,strict=True);del sd;model.to('cuda');model.eval()
        gpu_rows=np.zeros((N,V),np.float16);torch.cuda.reset_peak_memory_stats();started=time.monotonic()
        with torch.inference_mode():
            for a,b in zip(bounds[:-1],bounds[1:]):
                for ps,pe in tfh.pieces_of(int(b-a)):
                    lo=int(a+ps);hi=int(a+pe)
                    if hi-lo>=2:
                        t=torch.from_numpy(tokens[lo:hi]).to('cuda')[None];pr=torch.from_numpy(prior[lo:hi].astype(np.float32)).to('cuda')[None]
                        cu=torch.tensor([[0,hi-lo]],dtype=torch.int32,device='cuda')
                        logits=model.compute_logits(t,pr,cu)[0].float();rows=torch.softmax(logits,dim=-1).to(torch.float16).cpu().numpy()
                        gpu_rows[lo:hi-1]=rows[:-1]
                    gpu_rows[hi-1]=prior[hi-1]
        torch.cuda.synchronize();duration=time.monotonic()-started
        loss=bits(gpu_rows);loss.astype('<f4').tofile(dest/(name.replace('.tch','')+'_true_bits.f32'))
        row={'checkpoint':name,'layers':nl,'width':d,'measured_targets':N-1,'mean_neural_bits_per_symbol':float(loss.mean()),
             'summed_neural_bits':float(loss.sum()),'gpu_wall_seconds_including_jit':duration,'gpu_peak_allocated_bytes':torch.cuda.max_memory_allocated(),
             'quantized_forward':name=='6m-q4-fp32.tch','output_float16_then_floor_1e_minus6_and_normalize':True,
             'configuration_note':'8M/10M unstored hyperparameters inherited from6M; structural loading passed but author config still unverified',
             'packed_model_and_native_CPU_accounting':'Not measured for larger models; raw checkpoint size is not packed cost'}
        if name=='6m-q4-fp32.tch':
            q=np.maximum(gpu_rows.astype(np.float64),1e-6);q/=q.sum(axis=1,keepdims=True)
            kl=np.sum(native_clamped*np.log2(native_clamped/q),axis=1)
            parity={'mean_absolute_actual_bits_difference':float(np.abs(loss-native_bits).mean()),'max_absolute_actual_bits_difference':float(np.abs(loss-native_bits).max()),
                    'signed_mean_actual_bits_difference':float((loss-native_bits).mean()),'mean_native_to_GPU_KL_bits':float(kl.mean()),
                    'max_absolute_probability_difference':float(np.abs(q-native_clamped).max()),'scope':'Provisional sampled screening control; does not prove bit-exact final coding or CPU export parity'}
            result['control_parity']=parity
            result['control_parity_gate_passed']=(parity['mean_absolute_actual_bits_difference']<=.005 and parity['max_absolute_actual_bits_difference']<=.1 and parity['mean_native_to_GPU_KL_bits']<=1e-5 and parity['max_absolute_probability_difference']<=1e-3)
            gpu_rows.tofile(dest/'control_gpu.f16')
            # Preserve compact true-outcome costs and full short control probability evidence.
            (dest/'control_native.f16').write_bytes((work/'native_nn.f16').read_bytes())
        if result['lex_native_control']['priors_bit_exact_with_reference']:
            row['paired_sample_neural_bits_difference_vs_lex_native']=float((loss-lex_bits).sum())
            row['comparison_warning']='Sample neural likelihood only; larger models are unquantized, configuration assumptions and packaging/CPU costs unresolved'
        result['models'].append(row);save();print(json.dumps(row),flush=True)
        del model;torch.cuda.empty_cache();gc.collect()
    save();print('FROZEN_LOGITS_PILOT_COMPLETE',flush=True)
except Exception as e:
    result.update(failed=True,error=str(e),traceback=traceback.format_exc());save();print(result['traceback'],flush=True);raise
