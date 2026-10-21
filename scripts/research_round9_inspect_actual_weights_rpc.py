import pathlib,json,struct,numpy as np
S=pathlib.Path('/root/hp_round9/core_data_v1');p=S/'lex_weights.bin';f=p.open('rb');assert f.read(8)==b'FX2TFW01';n=struct.unpack('<I',f.read(4))[0];a=[]
for _ in range(n):
 name=f.read(struct.unpack('<I',f.read(4))[0]).decode();dtype=f.read(1)[0];nd=struct.unpack('<I',f.read(4))[0];shape=list(struct.unpack('<'+'I'*nd,f.read(nd*4)));size=int(np.prod(shape))*[1,2,4,4][dtype];raw=f.read(size);row={'name':name,'dtype':dtype,'shape':shape}
 if name.startswith('config.') or name.endswith('.codebook'):row['values']=np.frombuffer(raw,['i1','<u2','<f4','<i4'][dtype]).tolist()
 a.append(row)
print(json.dumps(a));
