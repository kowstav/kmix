import ctypes,ctypes.util,datetime,hashlib,json,lzma,pathlib,time,traceback,zlib
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'exact_prior_transforms_v1';assert not D.exists();D.mkdir();m={'status':'RUNNING','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'lossless prior-data representation only, not enwik9 compression','deletions':[],'paid_rental_usd':0};(D/'manifest.json').write_text(json.dumps(m,indent=2))
try:
 lib=ctypes.CDLL(ctypes.util.find_library('zstd'))
 lib.ZSTD_compressBound.argtypes=[ctypes.c_size_t];lib.ZSTD_compressBound.restype=ctypes.c_size_t
 lib.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int];lib.ZSTD_compress.restype=ctypes.c_size_t
 lib.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];lib.ZSTD_decompress.restype=ctypes.c_size_t
 lib.ZSTD_isError.argtypes=[ctypes.c_size_t];lib.ZSTD_isError.restype=ctypes.c_uint
 lib.ZSTD_versionString.restype=ctypes.c_char_p;m['zstd_version']=lib.ZSTD_versionString().decode()
 def ze(b,level=3):
  buf=ctypes.create_string_buffer(lib.ZSTD_compressBound(len(b)));n=lib.ZSTD_compress(buf,len(buf),b,len(b),level);assert not lib.ZSTD_isError(n);return buf.raw[:n]
 def zd(b,n):
  buf=ctypes.create_string_buffer(n);got=lib.ZSTD_decompress(buf,n,b,len(b));assert got==n;return buf.raw
 a=np.memmap(R/'exact_prior_storage_v1/priors.f16',dtype='<u2',mode='r',shape=(262144,205));rows=[]
 for lo in range(0,len(a),65536):
  u=np.asarray(a[lo:lo+65536]);original=u.tobytes();xor=u.copy();xor[1:]=np.bitwise_xor(u[1:],u[:-1]);delta=u.copy();delta[1:]=u[1:]-u[:-1]
  for name,v in [('raw',u),('byte_shuffle',u),('xor_byte_shuffle',xor),('delta_byte_shuffle',delta)]:
   begin=time.monotonic();b=v.tobytes() if name=='raw' else v.view(np.uint8).reshape(65536,205,2).transpose(1,2,0).copy().tobytes();transform_s=time.monotonic()-begin
   for codec,enc,dec in [('zstd3',lambda b:ze(b,3),lambda b:zd(b,len(original))),('zstd9',lambda b:ze(b,9),lambda b:zd(b,len(original))),('zlib3',lambda b:zlib.compress(b,3),zlib.decompress)]:
    begin=time.monotonic();packed=enc(b);cs=time.monotonic()-begin;begin=time.monotonic();back=dec(packed)
    if name!='raw':back=np.frombuffer(back,np.uint8).reshape(205,2,65536).transpose(2,0,1).copy().view('<u2').reshape(65536,205)
    else:back=np.frombuffer(back,'<u2').reshape(65536,205)
    if name.startswith('xor'):back=np.bitwise_xor.accumulate(back,axis=0)
    if name.startswith('delta'):back=np.cumsum(back,axis=0,dtype=np.uint64).astype('<u2')
    restored=back.tobytes();ds=time.monotonic()-begin;assert restored==original
    rows.append({'start':lo,'transform':name,'codec':codec,'raw_bytes':len(original),'compressed_bytes':len(packed),'ratio':len(packed)/len(original),'transform_seconds':transform_s,'compress_seconds':cs,'decode_and_inverse_seconds':ds,'exact_roundtrip':True})
 m.update(status='COMPLETE',rows=rows,prior_source_sha256=json.loads((R/'exact_prior_storage_v1/manifest.json').read_text())['prior_sha256']);(D/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m))
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());(D/'manifest.json').write_text(json.dumps(m,indent=2));raise
