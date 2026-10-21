"""P04 paid numeric-template packets: exact raw round trips and matched codecs.

Templates selected on A/B only; at most256, >=3 repetitions, <=8slots.
This is a generic-codec mechanism screen, not a native compressor gain.
"""
import collections,hashlib,json,lzma,pathlib,re,resource,time,zlib
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'macro_packets_v1';assert not D.exists();D.mkdir()
def vu(v):
 b=bytearray()
 while v>=128:b.append((v&127)|128);v>>=7
 b.append(v);return bytes(b)
def blob(b):return vu(len(b))+b
class Reader:
 def __init__(self,b):self.b=b;self.i=0
 def v(self):
  x=s=0
  while True:
   c=self.b[self.i];self.i+=1;x|=(c&127)<<s
   if c<128:return x
   s+=7;assert s<=64
 def blob(self):n=self.v();b=self.b[self.i:self.i+n];self.i+=n;assert len(b)==n;return b
def lines(raw):
 p=0
 for row in raw.split(b'\n'):
  end=p+len(row)+(p+len(row)<len(raw));yield raw[p:end],p,end;p=end
def split(line):
 matches=list(re.finditer(rb'[0-9]+',line));parts=[];digits=[];at=0
 for m in matches:parts.append(line[at:m.start()]);digits.append(m.group());at=m.end()
 parts.append(line[at:]);return tuple(parts),digits
def pool_packet(templates):return b'HPMP1'+vu(len(templates))+b''.join(vu(len(t))+b''.join(blob(p) for p in t) for t in templates)
def encode(raw,templates):
 ids={t:i for i,t in enumerate(templates)};out=bytearray(blob(pool_packet(templates)));stats=[]
 for line,a,b in lines(raw):
  t,digits=split(line)
  if t in ids:out+=vu(ids[t]+1)+b''.join(blob(d) for d in digits);stats.append((a,b))
  else:out+=vu(0)+blob(line)
 return bytes(out),stats
def decode(packet):
 r=Reader(packet);pool=Reader(r.blob());assert pool.b.startswith(b'HPMP1');pool.i=5;ts=[tuple(pool.blob() for _ in range(pool.v())) for _ in range(pool.v())];assert pool.i==len(pool.b);out=bytearray()
 while r.i<len(r.b):
  i=r.v()
  if i==0:out+=r.blob()
  else:
   parts=ts[i-1];out+=parts[0]
   for p in parts[1:]:out+=r.blob()+p
 return bytes(out)
began=time.monotonic();raws={n:(R/'preserved/slices'/(n+'2m.bin') if n in 'ab' else R/(n+'2m.bin')).read_bytes() for n in 'abcd'}
count=collections.Counter()
for n in 'ab':
 for line,a,b in lines(raws[n]):
  t,d=split(line)
  if d and len(d)<=8 and len(line)<=8192:count[t]+=1
templates=[t for t,c in sorted(count.items(),key=lambda x:(-x[1]*sum(map(len,x[0])),x[0])) if c>=3][:256];pool=pool_packet(templates);poolz=zlib.compress(pool,9);rows=[]
for n,raw in raws.items():
 packet,covered=encode(raw,templates);assert decode(packet)==raw;cost=np.fromfile(R/'lex_finalbit_2m_v1'/n/'cost.f32','<f4');prefix=np.r_[0,np.cumsum(cost,dtype=np.float64)];bits=sum(prefix[b]-prefix[a] for a,b in covered)
 row={'slice':n,'raw_bytes':len(raw),'templates':len(templates),'covered_lines':len(covered),'covered_native_bits':float(bits),'all_native_bits':float(prefix[-1]),'raw_packet_bytes':len(packet),'packet_sha256':hashlib.sha256(packet).hexdigest(),'raw_roundtrip':'PASS','model_pool_raw_bytes':len(pool),'model_pool_zlib_bytes':len(poolz),
 'relaxed_native_ceiling_bytes_two_copy_pool':float(bits/8-2*len(poolz)),
 'ceiling_relaxation':'Selected-line framing, IDs, variables, misses, code and runtime all free; this is an optimistic diagnostic for this frozen template pool, not an attainable gain.',
 'codecs':{}}
 for label,enc in [('zlib9',lambda b:zlib.compress(b,9)),('lzma6',lambda b:lzma.compress(b,preset=6))]:
  base=len(enc(raw));cand=len(enc(packet));row['codecs'][label]={'baseline_bytes':base,'candidate_bytes_one_pool_in_packet':cand,'delta_bytes':cand-base,'delta_percent':100*(cand/base-1),'extra_second_pool_if_hardcoded':len(enc(pool))}
 rows.append(row);(D/(n+'.json')).write_text(json.dumps(row,indent=2))
m={'status':'COMPLETE','preregistered':'A/B-frozen repeated numeric templates,256cap,>=3 repeats,<=8slots; ABCD matched zlib9/LZMA6','raw_roundtrips':4,'wall_seconds':time.monotonic()-began,'max_rss_kbytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'deletions':[],'paid_rental_usd':0}
(D/'manifest.json').write_text(json.dumps(m,indent=2));(D/'results.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'manifest':m,'rows':rows}))
