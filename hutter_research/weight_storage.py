"""Paid, tensor-preserving storage candidates; inference values never change."""
import gzip,hashlib,json,lzma,struct,zlib
import numpy as np
from .tensor_io import _DTYPE_TO_NUMPY

LAYOUTS=('plain','planes','zigzag','nibble','transpose','xor')
CODECS=('gzip','lzma','zstd')

def representation(tensors,layout,regenerate=False):
    if layout not in LAYOUTS:raise ValueError('unknown layout')
    schema=[];parts=[]
    for name,(dt,array) in sorted(tensors.items()):
        if regenerate and name in ('rope.sin','rope.cos') and dt==2 and array.ndim==2:
            from .native_weights import cuda_rope_table
            inv=tensors.get('rope.inv_freq')
            if inv is not None and inv[0]==2 and inv[1].shape==(array.shape[1],):
                table=cuda_rope_table(inv[1],array.shape[0],cos=name=='rope.cos')
                if table.tobytes()==array.tobytes():
                    schema.append([name,dt,list(array.shape),'rope_cos' if name=='rope.cos' else 'rope_sin',0])
                    continue
        data=np.ascontiguousarray(array);u=np.frombuffer(data.tobytes(),dtype='u1').copy()
        kind='plain'
        if layout=='transpose' and data.ndim==2:
            u=np.frombuffer(np.ascontiguousarray(data.T).tobytes(),dtype='u1');kind='transpose'
        elif layout=='planes' and data.dtype.itemsize>1:
            u=u.reshape(-1,data.dtype.itemsize).T.copy().ravel();kind='planes'
        elif layout in ('zigzag','nibble') and dt==0:
            v=data.astype(np.int16).ravel();z=(2*np.abs(v)-(v<0)).astype('u1')
            if layout=='nibble' and (not z.size or z.max()<16):
                if len(z)%2:z=np.r_[z,np.uint8(0)]
                u=(z[::2]|(z[1::2]<<4)).astype('u1');kind='nibble'
            else:u=z;kind='zigzag'
        elif layout=='xor' and len(u):
            u[1:]=u[1:]^u[:-1];kind='xor'
        raw=u.tobytes();parts.append(raw)
        schema.append([name,dt,list(data.shape),kind,len(raw)])
    return schema,b''.join(parts)

def inverse(schema,raw):
    tensors={};offset=0;deferred=[];names=set()
    for name,dt,shape,kind,length in schema:
        if name in names or dt not in _DTYPE_TO_NUMPY or length<0:raise ValueError('invalid tensor schema')
        names.add(name)
        if kind in ('rope_cos','rope_sin'):
            if dt!=2 or length!=0 or len(shape)!=2:raise ValueError('invalid regeneration record')
            deferred.append((name,shape,kind));continue
        payload=raw[offset:offset+length];offset+=length
        if len(payload)!=length:raise ValueError('truncated tensor')
        dtype=np.dtype(_DTYPE_TO_NUMPY[dt]);n=int(np.prod(shape));u=np.frombuffer(payload,dtype='u1').copy()
        if kind=='planes':u=u.reshape(dtype.itemsize,n).T.copy().ravel()
        elif kind=='xor':u=np.bitwise_xor.accumulate(u)
        elif kind in ('zigzag','nibble'):
            if kind=='nibble':
                z=np.empty(len(u)*2,dtype='u1');z[::2]=u&15;z[1::2]=u>>4;u=z[:n]
            v=((u.astype(np.int16)+1)//2);v[u%2==1]*=-1;u=v.astype('i1').view('u1')
        elif kind not in ('plain','transpose'):raise ValueError('unknown tensor transform')
        if len(u)!=n*dtype.itemsize:raise ValueError('tensor size mismatch')
        data=u.view(dtype)
        if kind=='transpose':
            if len(shape)!=2:raise ValueError('invalid transpose')
            data=data.reshape(shape[::-1]).T.copy()
        else:data=data.reshape(shape)
        tensors[name]=(dt,data)
    if offset!=len(raw):raise ValueError('trailing tensor bytes')
    for name,shape,kind in deferred:
        from .native_weights import cuda_rope_table
        inv=tensors.get('rope.inv_freq')
        if inv is None or inv[0]!=2 or inv[1].shape!=(shape[1],):raise ValueError('missing generation dependency')
        tensors[name]=(2,cuda_rope_table(inv[1],shape[0],cos=kind=='rope_cos'))
    return tensors

def tensor_digest(tensors):
    h=hashlib.sha256()
    for name,(dt,array) in sorted(tensors.items()):
        h.update(json.dumps([name,dt,list(array.shape)],separators=(',',':')).encode())
        h.update(array.tobytes())
    return h.digest()

def encode(tensors,layout,codec,regenerate=False):
    schema,raw=representation(tensors,layout,regenerate)
    metadata=gzip.compress(json.dumps(schema,separators=(',',':')).encode(),mtime=0)
    if codec=='gzip':payload=gzip.compress(raw,mtime=0)
    elif codec=='lzma':payload=lzma.compress(raw,preset=6)
    elif codec=='zstd':
        import zstandard as zstd
        payload=zstd.ZstdCompressor(level=9,threads=0).compress(raw)
    else:raise ValueError('unknown codec')
    digest=tensor_digest(tensors) if regenerate else hashlib.sha256(raw).digest()
    return (b'HPWT13B0' if regenerate else b'HPWT13A0')+struct.pack('<IBQ',len(metadata),CODECS.index(codec),len(raw))+digest+metadata+payload

def decode(blob):
    if blob[:8] not in (b'HPWT13A0',b'HPWT13B0') or len(blob)<53:raise ValueError('invalid weight container')
    m,c,n=struct.unpack_from('<IBQ',blob,8)
    if c>=len(CODECS) or 53+m>len(blob):raise ValueError('invalid metadata')
    schema=json.loads(gzip.decompress(blob[53:53+m]));payload=blob[53+m:]
    if c==0:raw=gzip.decompress(payload)
    elif c==1:raw=lzma.decompress(payload)
    else:
        import zstandard as zstd
        raw=zstd.ZstdDecompressor().decompress(payload,max_output_size=n)
    if len(raw)!=n:raise ValueError('corrupt tensor payload')
    tensors=inverse(schema,raw)
    digest=tensor_digest(tensors) if blob[:8]==b'HPWT13B0' else hashlib.sha256(raw).digest()
    if digest!=blob[21:53]:raise ValueError('corrupt tensor payload')
    return tensors
