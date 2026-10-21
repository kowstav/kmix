"""Bounded post-training sparsification; no SGD, scale change or neural fit.

All candidates use the already verified FX2TFWC5 loader. This deliberately
changes model values. Stored weight savings are not a compression result until
the final-coder likelihood loss is charged. Preserve baseline and every output.
"""
import pathlib,types,sys,importlib.util,json,time,hashlib
import numpy as np
out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'ptq_round7';dest.mkdir(exist_ok=False)
pkg=types.ModuleType('pysrc');pkg.__path__=[];ex=types.ModuleType('pysrc.export_weights')
for name,val in [('DTYPE_INT8',0),('DTYPE_BF16_BITS',1),('DTYPE_FLOAT32',2),('DTYPE_INT32',3)]:setattr(ex,name,val)
ex._DTYPE_TO_NUMPY={0:np.int8,1:np.uint16,2:np.float32,3:np.int32}
def unused(*a,**kw):raise RuntimeError('Raw export API unused')
ex.read_tensor_file=unused;sys.modules['pysrc']=pkg;sys.modules['pysrc.export_weights']=ex
spec=importlib.util.spec_from_file_location('v5',out/'v5_weights_compress.py');v5=importlib.util.module_from_spec(spec);spec.loader.exec_module(v5)
original=v5._read_compressed(str(out/'candidate_bf16.fx2tfwc5'))
print(json.dumps({'decoded_baseline_tensors':len(original),'baseline_bytes':(out/'candidate_bf16.fx2tfwc5').stat().st_size}),flush=True)
results=[]
for name,scope,threshold in [('mlp_down_unit0','mlp.down',1),('mlp_unit0','mlp',1),('all_unit2_zero','all',2)]:
    tensors=[];changed=0;touched=[];before=time.monotonic()
    for key,(dtype,array) in original.items():
        value=array
        if dtype==0 and (scope=='all' or ('.'+scope+'.' in key)):
            mask=(np.abs(array.astype(np.int16))<=threshold)&(array!=0)
            if mask.any():value=array.copy();value[mask]=0;changed+=int(mask.sum());touched.append(key)
        tensors.append((key,dtype,value))
    path=dest/(name+'.fx2tfwc5');v5.write_tensor_file_v2(str(path),tensors,compact=True)
    v5._verify_equal({k:(c,a) for k,c,a in tensors},v5._read_compressed(str(path)))
    row={'name':name,'scope':scope,'zero_code_magnitude_at_most':threshold,'changed_q4_values':changed,'tensors_changed':touched,'weights_bytes':path.stat().st_size,'baseline_weights_bytes':(out/'candidate_bf16.fx2tfwc5').stat().st_size,'saving_bytes_two_copies':2*((out/'candidate_bf16.fx2tfwc5').stat().st_size-path.stat().st_size),'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-before,'codec_roundtrip_tensor_bytes_equal':True,'neural_training_steps':0,'scales_and_non_q4_values_unchanged':True}
    results.append(row);(dest/'codec_results.json').write_text(json.dumps(results,indent=2));print(json.dumps({k:v for k,v in row.items() if k!='tensors_changed'}),flush=True)
print('PTQ_CODEC_COMPLETE',flush=True)
