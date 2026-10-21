"""Paid independent-group selection over an explicitly finite storage family."""
import gzip,json,struct
from .weight_storage import decode as decode_group,inverse,tensor_digest
MAGIC=b'HPWG14A0'
def pack(groups,deferred,digest):
    metadata=gzip.compress(json.dumps(deferred,separators=(',',':')).encode(),mtime=0)
    return MAGIC+struct.pack('<II',len(metadata),len(groups))+digest+metadata+b''.join(struct.pack('<Q',len(x))+x for x in groups)
def unpack(blob):
    if len(blob)<48 or blob[:8]!=MAGIC:raise ValueError('invalid grouped model')
    m,k=struct.unpack_from('<II',blob,8)
    if 48+m>len(blob) or not k:raise ValueError('invalid grouped header')
    deferred=json.loads(gzip.decompress(blob[48:48+m]));offset=48+m;tensors={}
    for _ in range(k):
        if offset+8>len(blob):raise ValueError('truncated group length')
        n,=struct.unpack_from('<Q',blob,offset);offset+=8
        if offset+n>len(blob):raise ValueError('truncated group')
        group=decode_group(blob[offset:offset+n]);offset+=n
        if tensors.keys() & group.keys():raise ValueError('duplicate tensor group')
        tensors.update(group)
    if offset!=len(blob):raise ValueError('trailing group bytes')
    if deferred:
        inv=tensors.get('rope.inv_freq')
        if inv is None:raise ValueError('missing rope dependency')
        schema=[['rope.inv_freq',inv[0],list(inv[1].shape),'plain',inv[1].nbytes]]+deferred
        extra=inverse(schema,inv[1].tobytes());extra.pop('rope.inv_freq')
        if tensors.keys() & extra.keys():raise ValueError('duplicate regeneration')
        tensors.update(extra)
    if tensor_digest(tensors)!=blob[16:48]:raise ValueError('tensor digest mismatch')
    return tensors
