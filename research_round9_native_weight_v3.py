"""FX2TFWC3 Python codec matched to the executed native reader.

Keep public v2 metadata/BF16/plane/RoPE rules; add native ENC_ADAPT=6 exactly.
Native cpp source is the authoritative numerical contract. Full reader identity
and neutral original-container reproduction are required, not just self roundtrip.
"""
import inspect
import numpy as np
import pysrc.weights_compress as w
class Adapt:
 def __init__(self,k,g):
  self.k=k;self.glob=g;t=sum(g);self.cnt=[max(1,(v*960+t//2)//t) if t else 1 for v in g];self.tot=sum(self.cnt)
 def update(self,s):
  self.cnt[s]+=1;self.glob[s]+=1;self.tot+=1
  if self.tot>65536:self.cnt=[(v+1)>>1 for v in self.cnt];self.tot=sum(self.cnt)
class Models(w._Models):
 def __init__(self):super().__init__();self.glob={}
 def adapt(self,qmax):
  if qmax not in self.glob:self.glob[qmax]=[0]*(2*qmax+1)
  return Adapt(2*qmax+1,self.glob[qmax])
class Encoder(w.BinEncoder):
 def encode_adapt(self,m,s):
  cum=sum(m.cnt[:s]);r=self.range//m.tot;self.low+=r*cum;self.range=self.range-r*cum if s==m.k-1 else r*m.cnt[s]
  while self.range<w._TOP:self.range<<=8;self._shift_low()
  m.update(s)
class Decoder(w.BinDecoder):
 def decode_adapt(self,m):
  r=self.range//m.tot;target=self.code//r;cum=0;s=0
  while s<m.k-1 and target>=cum+m.cnt[s]:cum+=m.cnt[s];s+=1
  self.code-=r*cum;self.range=self.range-r*cum if s==m.k-1 else r*m.cnt[s]
  while self.range<w._TOP:self.code=((self.code<<8)|self._byte())&w._MASK32;self.range<<=8
  m.update(s);return s
def choose(name,dt,a,seen):
 if dt==w.DTYPE_INT8 and (not a.size or np.max(np.abs(a.astype(np.int16)))<=127):return 6
 return w._pick_encoding(name,dt,a,seen)
ns=dict(vars(w));ns.update(_Models=Models,BinEncoder=Encoder,BinDecoder=Decoder,MAGIC_V2=b'FX2TFWC3',_pick_encoding=choose)
src=inspect.getsource(w.write_tensor_file_v2).replace('write_tensor_file_v2','write_tensor_file_v3',1)
anchor='        if encoding == ENC_INT4:';assert src.count(anchor)==1
src=src.replace(anchor,"        if encoding == 6:\n            qmax=int(np.max(np.abs(data.astype(np.int16)))) if data.size else 0\n            put_meta(qmax);adapt=models.adapt(qmax)\n            for v in data.astype(np.int32).ravel().tolist():enc.encode_adapt(adapt,v+qmax)\n        elif encoding == ENC_INT4:")
exec(compile(src,'<native-v3-encoder>','exec'),ns);write_tensor_file_v3=ns['write_tensor_file_v3']
src=inspect.getsource(w.read_tensor_file_v2).replace('read_tensor_file_v2','read_tensor_file_v3',1)
anchor='        if encoding == ENC_INT4:';assert src.count(anchor)==1
src=src.replace(anchor,"        if encoding == 6:\n            assert dtype_code==DTYPE_INT8\n            qmax=get_meta();assert qmax<=127;adapt=models.adapt(qmax)\n            array=np.array([dec.decode_adapt(adapt)-qmax for _ in range(count)],dtype=np.int8).reshape(shape)\n        elif encoding == ENC_INT4:")
exec(compile(src,'<native-v3-decoder>','exec'),ns);read_tensor_file_v3=ns['read_tensor_file_v3']
