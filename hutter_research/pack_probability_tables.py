"""Finite, exact integer table storage search; not probability approximation."""
from pathlib import Path
import hashlib,json,struct

def varint(x):
    assert x>=0
    out=bytearray()
    while x>=128:out.append((x&127)|128);x>>=7
    out.append(x);return out

def zig(x):return 2*x if x>=0 else -2*x-1

def pack(values,degree):
    v=list(map(int,values));delta=[v[i]-v[i-1] for i in range(1,len(v))]
    if degree==1:seq=delta;seeds=[v[0]]
    elif degree==2:seq=[delta[i]-delta[i-1] for i in range(1,len(delta))];seeds=[v[0],delta[0]]
    else:raise ValueError('degree')
    out=bytearray();i=0
    while i<len(seq):
        j=i+1
        while j<len(seq) and seq[j]==seq[i]:j+=1
        out+=varint(zig(seq[i]));out+=varint(j-i);i=j
    return bytes(out),seeds

def unpack(encoded,seeds,degree,count):
    out=[seeds[0]];delta=seeds[1] if degree==2 else 0
    if degree==2:out.append(out[0]+delta)
    i=0
    def get():
        nonlocal i
        x=shift=0
        while True:
            b=encoded[i];i+=1;x|=(b&127)<<shift
            if b<128:return x
            shift+=7;assert shift<=63
    while i<len(encoded):
        u=get();d=u//2 if u%2==0 else -(u//2)-1;n=get();assert n>0
        for _ in range(n):
            if degree==2:delta+=d
            else:delta=d
            out.append(out[-1]+delta)
    assert len(out)==count;return out

HEADER='''#pragma once
#include <array>
#include <cstdint>
#include <cstddef>
#include <limits>
#include <stdexcept>
namespace hp {
namespace table_storage {
template<class T, std::size_t N, std::size_t M>
inline std::array<T,N> Decode(const uint8_t (&data)[M], unsigned degree, int64_t first, int64_t initial_delta) {
  std::array<T,N> out{};std::size_t p=0,i=0;int64_t value=first,delta=initial_delta;
  auto emit=[&](){if(i>=N||value<std::numeric_limits<T>::min()||value>std::numeric_limits<T>::max())throw std::logic_error("table value/range");out[i++]=T(value);};
  auto get=[&](){uint64_t x=0;unsigned shift=0;for(;;){if(p>=M||shift>=63)throw std::logic_error("table varint");const auto b=data[p++];x|=uint64_t(b&127)<<shift;if(!(b&128))return x;shift+=7;}};
  emit();if(degree==2){value+=delta;emit();}
  while(p<M){const auto u=get();const int64_t d=(u&1)?-int64_t(u>>1)-1:int64_t(u>>1);const auto n=get();if(n==0||n>N-i)throw std::logic_error("table run");for(uint64_t k=0;k<n;k++){delta=degree==2?delta+d:d;value+=delta;emit();}}
  if(i!=N)throw std::logic_error("table length");return out;
}
}
'''

def build(binary,header,manifest):
    raw=Path(binary).read_bytes();assert len(raw)==163846
    specs=[('kStretch','int16_t','h',65536),('kSquash','uint16_t','H',8193),('kOdds','uint32_t','I',4097)]
    offset=0;rows=[];text=HEADER
    for name,ctype,fmt,n in specs:
        size=struct.calcsize('<'+fmt)*n;values=list(struct.unpack('<'+str(n)+fmt,raw[offset:offset+size]));offset+=size
        candidates=[]
        for degree in (1,2):
            encoded,seeds=pack(values,degree);assert unpack(encoded,seeds,degree,n)==values
            candidates.append((len(encoded),degree,encoded,seeds))
        _,degree,encoded,seeds=min(candidates,key=lambda x:(x[0],x[1]))
        text+='inline constexpr uint8_t '+name+'Packed[]={\n'
        text+='\n'.join(','.join(map(str,encoded[i:i+32]))+',' for i in range(0,len(encoded),32))+'\n};\n'
        text+=f'inline const auto {name}=table_storage::Decode<{ctype},{n}>({name}Packed,{degree},{seeds[0]},{seeds[1] if degree==2 else 0});\n'
        rows.append({'table':name,'entries':n,'degree':degree,'packed_data_bytes':len(encoded),'raw_bytes':size,'candidate_bytes':{str(x[1]):x[0] for x in candidates},'values_exact':True})
    text+='}\n';Path(header).write_bytes(text.encode('utf-8'))
    m={'status':'EXACT_PYTHON_RECONSTRUCTION_ALL_TABLE_VALUES','raw_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(text.encode()).hexdigest(),'tables':rows,'code_size_included_only_after_compilation':True,'deletions':[]}
    Path(manifest).write_text(json.dumps(m,indent=2),encoding='utf-8');return m

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('binary');p.add_argument('header');p.add_argument('manifest');a=p.parse_args();print(json.dumps(build(a.binary,a.header,a.manifest)))
