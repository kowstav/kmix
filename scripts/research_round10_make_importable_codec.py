"""One-time source migration. Generated codecs are normal importable modules.

No experiment imports training workers, mutates shared globals or evaluates
source strings at runtime. Preserve the upstream implementation and hashes.
"""

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

import pathlib,ast,hashlib,json
P=project_root(__file__);D=project_path('hutter_research', base=P);D.mkdir(exist_ok=True)
(D/'__init__.py').write_text('"""Explicit, importable Hutter research contracts."""\n',encoding='utf-8')
export=(project_path('research_round9_recovered_training_sources/export_weights.py', base=P)).read_text()
tree=ast.parse(export);functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['read_tensor_file','write_tensor_file']]
raw='import struct\nimport numpy as np\nMAGIC=b"FX2TFW01"\nDTYPE_INT8=0\nDTYPE_BF16_BITS=1\nDTYPE_FLOAT32=2\nDTYPE_INT32=3\n_DTYPE_TO_NUMPY={0:np.int8,1:np.uint16,2:np.float32,3:np.int32}\n'
raw+='\n\n'.join(ast.get_source_segment(export,n) for n in functions)+'\n';(D/'tensor_io.py').write_text(raw,encoding='utf-8')
up=(project_path('research_round9_recovered_training_sources/weights_compress.py', base=P)).read_text();legacy=up.replace('from pysrc.export_weights import (','from .tensor_io import (').replace('from pysrc.export_weights import write_tensor_file','from .tensor_io import write_tensor_file')
assert 'from pysrc' not in legacy;(D/'legacy_weights.py').write_text(legacy,encoding='utf-8')
v3=legacy.replace('MAGIC_V2 = b"FX2TFWC2"','MAGIC_V2 = b"FX2TFWC3"').replace('write_tensor_file_v2','write_tensor_file_v3').replace('read_tensor_file_v2','read_tensor_file_v3').replace('def _pick_encoding(','def _pick_encoding_base(',1)
extra='''
class Adapt:
    def __init__(self, k, glob):
        self.k=k; self.glob=glob; total=sum(glob)
        self.cnt=[max(1,(v*960+total//2)//total) if total else 1 for v in glob]
        self.tot=sum(self.cnt)
    def update(self, symbol):
        self.cnt[symbol]+=1; self.glob[symbol]+=1; self.tot+=1
        if self.tot>65536:
            self.cnt=[(v+1)>>1 for v in self.cnt]; self.tot=sum(self.cnt)
_BaseModels=_Models
class _Models(_BaseModels):
    def __init__(self):
        super().__init__(); self.glob={}
    def adapt(self,qmax):
        if qmax not in self.glob:self.glob[qmax]=[0]*(2*qmax+1)
        return Adapt(2*qmax+1,self.glob[qmax])
_BaseEncoder=BinEncoder
class BinEncoder(_BaseEncoder):
    def encode_adapt(self,m,s):
        cum=sum(m.cnt[:s]); r=self.range//m.tot
        self.low+=r*cum; self.range=self.range-r*cum if s==m.k-1 else r*m.cnt[s]
        while self.range<_TOP:self.range<<=8; self._shift_low()
        m.update(s)
_BaseDecoder=BinDecoder
class BinDecoder(_BaseDecoder):
    def decode_adapt(self,m):
        r=self.range//m.tot; target=self.code//r; cum=0; s=0
        while s<m.k-1 and target>=cum+m.cnt[s]:cum+=m.cnt[s]; s+=1
        self.code-=r*cum; self.range=self.range-r*cum if s==m.k-1 else r*m.cnt[s]
        while self.range<_TOP:self.code=((self.code<<8)|self._byte())&_MASK32; self.range<<=8
        m.update(s); return s
def _pick_encoding(name,dtype_code,array,seen):
    if dtype_code==DTYPE_INT8 and (not array.size or np.max(np.abs(array.astype(np.int16)))<=127):return 6
    return _pick_encoding_base(name,dtype_code,array,seen)

'''
anchor='def write_tensor_file_v3(';assert v3.count(anchor)==1;v3=v3.replace(anchor,extra+anchor)
anchor='        if encoding == ENC_INT4:';assert v3.count(anchor)==2
v3=v3.replace(anchor,'''        if encoding == 6:
            qmax=int(np.max(np.abs(data.astype(np.int16)))) if data.size else 0
            put_meta(qmax); model=models.adapt(qmax)
            for value in data.astype(np.int32).ravel().tolist():enc.encode_adapt(model,value+qmax)
        elif encoding == ENC_INT4:''',1)
v3=v3.replace(anchor,'''        if encoding == 6:
            assert dtype_code==DTYPE_INT8
            qmax=get_meta(); assert qmax<=127; model=models.adapt(qmax)
            array=np.array([dec.decode_adapt(model)-qmax for _ in range(count)],dtype=np.int8).reshape(shape)
        elif encoding == ENC_INT4:''',1)
(D/'native_weights.py').write_text(v3,encoding='utf-8')
for p in D.glob('*.py'):ast.parse(p.read_text())
result={'upstream_sha256':hashlib.sha256(up.encode()).hexdigest(),'runtime_exec':False,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.py')},'native_original_reproduction_required':True}
(project_path('research_round10_codec_migration_manifest.json', base=P)).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
