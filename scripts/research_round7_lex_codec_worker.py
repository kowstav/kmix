"""Exact C3 -> published C5 screen; keeps original serialization dtypes/order."""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

import pathlib,struct,types,sys,importlib.util,json,time,hashlib,subprocess
import numpy as np
out=pathlib.Path('/kaggle/working/hp_round7');lab=pathlib.Path('/root/hp/lex_codec_lab');dest=out/'lex_audit'
src=(lab/'weights_io_compressed_unpromoted.cpp').read_text()
needle='    if (!wf.tensors.emplace(name, std::move(t)).second)'
assert src.count(needle)==2
src=src.replace(needle,'    std::fprintf(stderr, "ORDER\\t%s\\n", name.c_str());\n'+needle)
(lab/'weights_io_compressed_ordered.cpp').write_text(src)
subprocess.run(['g++','-std=c++17','-O2','-I'+str(lab),str(out/str(project_path('research_round7_tensor_dump.cpp'))),str(lab/'weights_io.cpp'),str(lab/'weights_io_compressed_ordered.cpp'),'-o',str(out/'lex_tensor_dump_ordered')],check=True)
r=subprocess.run([str(out/'lex_tensor_dump_ordered'),str(dest/'lex_h1_run11.tfwc2'),str(dest/'lex_unpromoted_raw.bin')],check=True,capture_output=True,text=True)
order=[x.split('\t',1)[1] for x in r.stderr.splitlines() if x.startswith('ORDER\t')]
(dest/'original_tensor_order.json').write_text(json.dumps(order))
pkg=types.ModuleType('pysrc');pkg.__path__=[];ex=types.ModuleType('pysrc.export_weights')
for name,val in [('DTYPE_INT8',0),('DTYPE_BF16_BITS',1),('DTYPE_FLOAT32',2),('DTYPE_INT32',3)]:setattr(ex,name,val)
ex._DTYPE_TO_NUMPY={0:np.int8,1:np.uint16,2:np.float32,3:np.int32}
ex.read_tensor_file=lambda *a:None;sys.modules['pysrc']=pkg;sys.modules['pysrc.export_weights']=ex
spec=importlib.util.spec_from_file_location('v5',out/'v5_weights_compress.py');v5=importlib.util.module_from_spec(spec);spec.loader.exec_module(v5)
raw=(dest/'lex_unpromoted_raw.bin').read_bytes();assert raw[:8]==b'FX2TFW01';pos=8
def u32():
    global pos
    value=struct.unpack_from('<I',raw,pos)[0];pos+=4;return value
n=u32();tensors={};counts=[]
for i in range(n):
    count=u32();name=raw[pos:pos+count].decode();pos+=count;code=raw[pos];pos+=1
    ndim=u32();shape=tuple(u32() for j in range(ndim));dtype=ex._DTYPE_TO_NUMPY[code]
    size=int(np.prod(shape))*np.dtype(dtype).itemsize
    arr=np.frombuffer(raw,dtype=dtype,count=int(np.prod(shape)),offset=pos)
    arr=arr.reshape(shape).copy();pos+=size;tensors[name]=(code,arr)
    if code==0:counts.append({'name':name,'shape':shape,'min':int(arr.min()),'max':int(arr.max()),'distinct':int(len(np.unique(arr))),'numel':arr.size,'entropy_bits':float(-sum(c/arr.size*np.log2(c/arr.size) for c in np.unique(arr,return_counts=True)[1]))*arr.size})
assert pos==len(raw) and len(set(order))==n and set(order)==set(tensors)
(dest/'tensor_stats.json').write_text(json.dumps(counts,indent=2))
print('LEX_Q4',json.dumps({'tensors':n,'int8_numel':sum(r['numel'] for r in counts),'q4_numel':sum(r['numel'] for r in counts if r['min']>=-7 and r['max']<=7),'int8_order0_entropy_bytes':sum(r['entropy_bits'] for r in counts)/8,'non_q4':[r for r in counts if r['min']< -7 or r['max']>7]}),flush=True)
before=time.monotonic();report=[];target=dest/'lex_h1_run11.fx2tfwc5'
v5.write_tensor_file_v2(str(target),[(k,*tensors[k]) for k in order],compact=True,report=report)
v5._verify_equal(tensors,v5._read_compressed(str(target)))
row={'original_bytes':(dest/'lex_h1_run11.tfwc2').stat().st_size,'v5_bytes':target.stat().st_size,'gross_saving_two_copies':2*((dest/'lex_h1_run11.tfwc2').stat().st_size-target.stat().st_size),'all_435_serialized_tensor_arrays_equal':True,'original_tensor_order_retained':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'seconds':time.monotonic()-before,'source':'Published FX4 C5, no model-value change; requires independent native loader and final package checks','q4_report':report}
(dest/'v5_codec_results.json').write_text(json.dumps(row,indent=2));print(json.dumps({k:v for k,v in row.items() if k!='q4_report'}),flush=True)
print('LEX_V5_CODEC_COMPLETE',flush=True)
