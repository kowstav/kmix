"""Run the pinned GPLv3 FX4 weight codec with a minimal import adapter.

Original source is kept intact with its license and pinned manifest. The adapter
provides only datatype constants; raw checkpoint export is deliberately unused.
No training or floating point changes are performed. Verify every tensor byte.
"""
import pathlib,sys,types,importlib.util,json,hashlib,time
import numpy as np

out=pathlib.Path('/kaggle/working/hp_round7')
pkg=types.ModuleType('pysrc');pkg.__path__=[]
ex=types.ModuleType('pysrc.export_weights')
for name,value in [('DTYPE_INT8',0),('DTYPE_BF16_BITS',1),('DTYPE_FLOAT32',2),('DTYPE_INT32',3)]:setattr(ex,name,value)
ex._DTYPE_TO_NUMPY={0:np.int8,1:np.uint16,2:np.float32,3:np.int32}
def unused(*args,**kwargs):raise RuntimeError('Raw export API is not used by this adapter')
ex.read_tensor_file=unused
sys.modules['pysrc']=pkg;sys.modules['pysrc.export_weights']=ex
spec=importlib.util.spec_from_file_location('pinned_v5',out/'v5_weights_compress.py')
v5=importlib.util.module_from_spec(spec);spec.loader.exec_module(v5)
results=[]
def digest(tensors):
    h=hashlib.sha256()
    for name,(code,array) in tensors.items():
        h.update(name.encode()+b'\0'+bytes([code]));h.update(np.asarray(array.shape,dtype='<u8').tobytes());h.update(array.tobytes())
    return h.hexdigest()
for name,path in [('reference',out/'reference.fx2tfwc2'),('candidate_bf16',pathlib.Path('/root/hp/cand_final2/run/comp_tfweights'))]:
    started=time.monotonic();original=v5._read_compressed(str(path))
    print(json.dumps({'decoded':name,'tensors':len(original),'tensor_digest':digest(original),'elapsed':time.monotonic()-started}),flush=True)
    dest=out/(name+'.fx2tfwc5');report=[]
    v5.write_tensor_file_v2(str(dest),[(key,code,array) for key,(code,array) in original.items()],compact=True,report=report)
    decoded=v5._read_compressed(str(dest));v5._verify_equal(original,decoded)
    # Re-encoding the baseline preserves omitted-RoPE recipes and byte order.
    recoded=out/(name+'.reencoded.fx2tfwc2')
    v5.write_tensor_file_v2(str(recoded),[(key,code,array) for key,(code,array) in original.items()])
    if recoded.read_bytes()!=path.read_bytes():raise RuntimeError('V2 encoder did not reproduce original container exactly')
    row={'name':name,'input_bytes':path.stat().st_size,'output_bytes':dest.stat().st_size,'saving_bytes_per_copy':path.stat().st_size-dest.stat().st_size,'tensor_count':len(original),'tensor_sha256':digest(original),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'all_tensor_bytes_equal':True,'original_container_reencoded_identically':True,'elapsed_seconds':time.monotonic()-started,'q4_encodings':report}
    results.append(row);(out/'v5_codec_results.json').write_text(json.dumps(results,indent=2));print(json.dumps({k:v for k,v in row.items() if k!='q4_encodings'}),flush=True)
print('V5_CODEC_COMPLETE',flush=True)
