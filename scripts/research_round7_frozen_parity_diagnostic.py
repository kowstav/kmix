"""Read-only decomposition of the failed F01 numerical fidelity control."""
import pathlib,json,numpy as np,hashlib
out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'frozen_logits_pilot_v2';work=pathlib.Path('/root/hp/frozen_logits_pilot_v2')
assert not (dest/'parity_diagnostic.json').exists(),'Preserve prior diagnostic; do not overwrite'
N=65536;V=205
native=np.fromfile(dest/'control_native.f16','<f2').reshape(N,V)[:-1].astype(np.float64)
gpu=np.fromfile(dest/'control_gpu.f16','<f2').reshape(N,V)[:-1].astype(np.float64)
tokens=np.fromfile(work/'tokens.u8','u1');bounds=np.fromfile(work/'bounds.i32','<i4')
for q in [native,gpu]:q[:]=np.maximum(q,1e-6);q/=q.sum(axis=1,keepdims=True)
rows=np.arange(N-1);target=tokens[1:];nb=-np.log2(native[rows,target]);gb=-np.log2(gpu[rows,target]);delta=gb-nb
kl=np.sum(native*np.log2(native/gpu),axis=1);mx=np.max(np.abs(native-gpu),axis=1)
start=bounds[np.searchsorted(bounds,rows,side='right')-1];offset=rows-start
boundary=np.isin(rows,bounds[1:-1]-1)
def summary(mask):
    return {'rows':int(mask.sum()),'mean_abs_target_bits_difference':float(np.abs(delta[mask]).mean()),'max_abs_target_bits_difference':float(np.abs(delta[mask]).max()),'mean_KL_bits':float(kl[mask].mean()),'max_probability_difference':float(mx[mask].max()),'signed_mean_target_bits_difference':float(delta[mask].mean())} if mask.any() else {'rows':0}
result={'scope':'Diagnostic of a FAILED fidelity gate; no new compression claim','boundary_fallback':summary(boundary),'non_boundary':summary(~boundary),
        'by_offset':{},'KL_quantiles':np.quantile(kl,[0,.5,.9,.99,.999,1]).tolist(),'target_abs_error_quantiles':np.quantile(np.abs(delta),[0,.5,.9,.99,.999,1]).tolist(),
        'top_target_errors':[],'top_distribution_errors':[],'mean_KL_shift_check':{},'neural_training':False,'deletions':[],'paid_rental_usd':0}
for lo,hi in [(0,1),(1,4),(4,16),(16,64),(64,256),(256,1024),(1024,131072)]:result['by_offset'][f'{lo}-{hi-1}']=summary((offset>=lo)&(offset<hi)&~boundary)
for metric,key in [(np.abs(delta),'top_target_errors'),(kl,'top_distribution_errors')]:
    for i in np.argsort(metric)[-24:][::-1]:
        i=int(i);j=int(np.argmax(np.abs(native[i]-gpu[i])))
        result[key].append({'row':i,'offset':int(offset[i]),'target':int(target[i]),'native_target_p':float(native[i,target[i]]),'gpu_target_p':float(gpu[i,target[i]]),'target_bits_difference':float(delta[i]),'KL_bits':float(kl[i]),'max_probability_error_token':j,'native_error_p':float(native[i,j]),'gpu_error_p':float(gpu[i,j]),'boundary_fallback':bool(boundary[i])})
for shift in [-1,0,1]:
    if shift<0:a=native[1:];b=gpu[:-1]
    elif shift>0:a=native[:-1];b=gpu[1:]
    else:a=native;b=gpu
    result['mean_KL_shift_check'][str(shift)]=float(np.sum(a*np.log2(a/b),axis=1).mean())
result['source_sha256']=hashlib.sha256((out/'research_round7_frozen_parity_diagnostic.py').read_bytes()).hexdigest()
(dest/'parity_diagnostic.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if not k.startswith('top_')},indent=2))
print('TOP_TARGET_ERRORS',json.dumps(result['top_target_errors'][:6]))
