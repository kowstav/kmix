"""Independent parser for the paid full-file factorization proxy frames."""
import gzip,hashlib,struct
from .constructor_codec import decode as decode_constructor

def exactly(stream,n):
    data=stream.read(n)
    if len(data)!=n:raise ValueError('truncated full-file frame')
    return data

def decoded_chunks(stream):
    if exactly(stream,8)!=b'HPFULL13':raise ValueError('invalid full-file magic')
    expected,count=struct.unpack('<QI',exactly(stream,12));observed=0
    if not expected or not count:raise ValueError('empty full-file declaration')
    for _ in range(count):
        length,size=struct.unpack('<II',exactly(stream,8))
        if not length or not size or length>4*1048576:raise ValueError('invalid chunk lengths')
        payload=exactly(stream,size)
        if payload[:8]==b'HPCTOR11':raw=decode_constructor(payload)
        elif payload[:2]==b'\x1f\x8b':raw=gzip.decompress(payload)
        elif payload[:4]==b'\x28\xb5\x2f\xfd':
            import zstandard as zstd
            raw=zstd.ZstdDecompressor().decompress(payload,max_output_size=length)
        else:raise ValueError('unknown paid chunk codec')
        if len(raw)!=length:raise ValueError('restored chunk length differs')
        observed+=length;yield raw
    if observed!=expected or stream.read(1):raise ValueError('full-file framing differs')

def verify(path):
    digest=hashlib.sha256();n=chunks=0
    with open(path,'rb') as stream:
        for raw in decoded_chunks(stream):digest.update(raw);n+=len(raw);chunks+=1
    return {'restored_bytes':n,'chunks':chunks,'restored_sha256':digest.hexdigest()}
