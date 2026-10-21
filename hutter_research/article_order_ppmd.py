"""Exact paid article permutation with a larger-context PPMd-I proxy.

Sources: https://pyppmd.readthedocs.io/en/latest/api_guide.html
The serialized stream pays permutation, lengths, PPMd order and memory.
"""
import gzip,hashlib,re,struct
import numpy as np
from .constructor_codec import WORDS
MAGIC=b'HPOR14A0';CTORS={w.encode() for w in WORDS};WORD=re.compile(rb'[A-Za-z]{3,}')
def compress(pages,order,max_order=8,mem_size=64<<20):
    import pyppmd
    n=len(pages);order=list(map(int,order))
    if sorted(order)!=list(range(n)):raise ValueError('invalid permutation')
    ordering=b'' if order==list(range(n)) else gzip.compress(np.asarray(order,dtype='<u4').tobytes(),mtime=0)
    lengths=gzip.compress(np.asarray([len(pages[i]) for i in order],dtype='<u4').tobytes(),mtime=0)
    payload=pyppmd.compress(b''.join(pages[i] for i in order),max_order=max_order,mem_size=mem_size,variant='I')
    return MAGIC+struct.pack('<6I',n,max_order,mem_size,len(ordering),len(lengths),len(payload))+ordering+lengths+payload
def decompress(blob):
    import pyppmd
    if len(blob)<32 or blob[:8]!=MAGIC:raise ValueError('invalid order container')
    n,o,m,a,b,c=struct.unpack_from('<6I',blob,8)
    if 32+a+b+c!=len(blob):raise ValueError('invalid order framing')
    order=np.frombuffer(gzip.decompress(blob[32:32+a]),dtype='<u4').tolist() if a else list(range(n))
    if sorted(order)!=list(range(n)):raise ValueError('invalid paid permutation')
    lengths=np.frombuffer(gzip.decompress(blob[32+a:32+a+b]),dtype='<u4')
    if len(lengths)!=n:raise ValueError('invalid lengths')
    raw=pyppmd.decompress(blob[32+a+b:],max_order=o,mem_size=m,variant='I');pages=[None]*n;offset=0
    for i,k in zip(order,lengths):
        k=int(k);pages[i]=raw[offset:offset+k];offset+=k
    if offset!=len(raw):raise ValueError('invalid restored lengths')
    return pages
def graph_orders(pages,compress_payload=None):
    """Bounded-candidate directed search; no quadratic corpus-wide distance table."""
    if compress_payload is None:
        import pyppmd
        def compress_payload(data,max_order,mem_size):
            return pyppmd.compress(data,max_order=max_order,mem_size=mem_size,variant='I')
    n=len(pages);words=[set(WORD.findall(p.lower()))-CTORS for p in pages];inverted={}
    for i,ws in enumerate(words):
        for w in ws:inverted.setdefault(w,[]).append(i)
    # Degree caps bound the graph even if a collection contains boilerplate.
    postings={w:v for w,v in inverted.items() if len(v)<=64}
    candidates=[];scores=[]
    for i,ws in enumerate(words):
        count={}
        for w in sorted(ws,key=lambda w:(len(inverted[w]),w))[:64]:
            for j in postings.get(w,[]):
                if i!=j:count[j]=count.get(j,0.)+1./len(inverted[w])
        for j in range(max(0,i-2),min(n,i+3)):
            if j!=i:count.setdefault(j,0.)
        for shift in (7,19,43,71):
            j=(i+shift)%n
            if j!=i:count.setdefault(j,0.)
        cs=sorted(count,key=lambda j:(-count[j],j))[:8];candidates.append(cs);scores.append(count)
    costs={};conditional_pairs=0
    standalone=[len(compress_payload(p[:4096],max_order=8,mem_size=8<<20)) for p in pages]
    for i,cs in enumerate(candidates):
        prefix=pages[i][-4096:]
        base=len(compress_payload(prefix,max_order=8,mem_size=8<<20))
        for j in cs[:4]:
            # Subtract the target's standalone cost so greedy choices do not
            # mechanically prefer short pages. This remains a directed proxy.
            costs[i,j]=len(compress_payload(prefix+pages[j][:4096],max_order=8,mem_size=8<<20))-base-standalone[j]
            conditional_pairs+=1
    def travel(conditional):
        unused=set(range(n));current=0;result=[]
        while unused:
            result.append(current);unused.remove(current)
            if not unused:break
            cs=[j for j in candidates[current] if j in unused and (not conditional or (current,j) in costs)]
            if cs:current=min(cs,key=lambda j:(costs[current,j],j) if conditional else (-scores[current][j],j))
            else:current=min(unused)
        return result
    return {'rare_word_graph':travel(False),'conditional_ppmd_graph':travel(True)},conditional_pairs
