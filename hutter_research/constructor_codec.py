"""Exact paid constructor/anchor factorization for finite CPU proxy experiments.

No neural model or POS oracle. ASCII lexical words are classified by an explicit
paid lexicon. Unicode, punctuation, case, literal words and every boundary survive.
Future literal anchors are available only because that channel is encoded first.
"""
import gzip
import re
import struct
from .native_weights import BinEncoder, BinDecoder

WORDS=tuple(sorted(set('a an the and or but if then than that this these those as at by for from in into of on onto out over to under up upon with without about after before between through during is am are was were be been being do does did have has had can could may might must shall should will would not no nor so too very it its he him his she her hers they them their theirs we us our ours you your yours i me my mine who whom whose which what when where why how there here now all any each either neither some such both few many most much other another same own only also even just more less once again'.split())))
TOKEN=re.compile(rb"[A-Za-z]+(?:'[A-Za-z]+)*")
MODES={'unigram':0,'markov':1,'anchors':2,'wrong_anchors':3,'bag':4,
       'coarse_right':5,'coarse_wrong':6,'coarse_left':7,
       'bag_markov0':8,'bag_markov1':9,'bag_right0':10,'bag_right1':11,
       'bag_wrong0':12,'bag_wrong1':13,'bag_left0':14,'bag_left1':15}

def is_bag(mode):return mode=='bag' or mode.startswith('bag_')

def bag_context_mode(mode):
    return {'markov':'markov','right':'coarse_right','wrong':'coarse_wrong',
            'left':'coarse_left'}[mode[4:-1]]

def varint(n):
    assert n>=0
    out=bytearray()
    while n>=128: out.append((n&127)|128); n>>=7
    out.append(n); return bytes(out)

def get_varint(data,offset):
    n=shift=0
    while True:
        if offset>=len(data) or shift>63: raise ValueError('invalid varint')
        b=data[offset]; offset+=1; n|=(b&127)<<shift
        if b<128: return n,offset
        shift+=7

def hashed(word):
    value=14695981039346656037
    for c in word.lower(): value=((value^c)*1099511628211)&((1<<64)-1)
    return value

def case_of(raw,word):
    if raw==word: return 0
    if raw==word[:1].upper()+word[1:]: return 1
    if raw==word.upper(): return 2
    return None

def prepare(raw,words):
    lex={w.encode():i for i,w in enumerate(words)}
    gaps=bytearray(); flags=bytearray(); literals=bytearray(); cases=bytearray(); ids=[]; literal_words=[]
    end=0
    for match in TOKEN.finditer(raw):
        gap=raw[end:match.start()]; gaps+=varint(len(gap))+gap
        word=match.group(); normalized=word.lower(); idx=lex.get(normalized)
        case=case_of(word,normalized) if idx is not None else None
        if case is None:
            flags.append(0); literals+=varint(len(word))+word; ids.append(None); literal_words.append(word)
        else:
            flags.append(1); cases.append(case); ids.append(idx); literal_words.append(None)
        end=match.end()
    gap=raw[end:]; gaps+=varint(len(gap))+gap
    return bytes(gaps),bytes(flags),bytes(literals),bytes(cases),ids,literal_words

def anchors(flags,literal_words):
    n=len(flags); left=[b'']*n; right=[b'']*n; last=b''
    for i in range(n):
        left[i]=last
        if not flags[i]: last=literal_words[i]
    last=b''
    for i in range(n-1,-1,-1):
        right[i]=last
        if not flags[i]: last=literal_words[i]
    return left,right,[w for w in literal_words if w is not None]

def context(mode,left,right,variables,pos,previous,runpos):
    if mode=='unigram': return 0
    if mode=='markov': return previous+1
    if mode in ('coarse_right','coarse_wrong','coarse_left'):
        if mode=='coarse_wrong':
            right=variables[(pos*1103515245+12345)%len(variables)] if variables else b''
        # Shared morphology classes replace exact-word hash collisions. The
        # parent remains the previous constructor, with deterministic backoff.
        word=left if mode=='coarse_left' else right
        lower=word.lower()
        length=min(len(lower)//4,3)
        shape=int(bool(lower) and lower[:1] in b'aeiou')+2*int(lower.endswith(b's'))+4*int(word[:1].isupper())
        return (previous+1,length*8+shape)
    if mode=='wrong_anchors':
        # Deterministic unrelated paid literal, rather than a bijective relabel
        # of the same informative context. No unknown target is inspected.
        right=variables[(pos*1103515245+12345)%len(variables)] if variables else b''
    a,b=hashed(left),hashed(right)
    return (a^(b>>17)^(b<<11)^((previous+1)*104729)^(min(runpos,7)*65537))&2047

class ConditionalModel:
    def __init__(self,alphabet,alpha):
        self.k=alphabet; self.alpha=alpha; self.global_counts=[0]*alphabet; self.contexts={}
    def select(self,key):
        self.local=self.contexts.setdefault(key,[0]*self.k)
        g=self.global_counts; c=self.local
        if isinstance(key,tuple):
            # Same previous-constructor model as Markov. Only the added paid
            # anchor class differs from its left/unrelated-anchor controls.
            self.parent=self.contexts.setdefault(('parent',key[0]),[0]*self.k)
            dp=2*sum(self.parent)+self.k;dg0=2*sum(g)+self.k
            g=[1+16384*((2*x+1)*dp+(2*y+1)*dg0)//(2*dg0*dp) for x,y in zip(g,self.parent)]
        else:self.parent=None
        dg=2*sum(g)+self.k; dc=2*sum(c)+self.k
        # Positive integer frequencies, all outcomes normalized by their exact
        # sum by the range coder. alpha is a paid numerator over eight.
        self.cnt=[1+16384*((8-self.alpha)*(2*x+1)*dc+self.alpha*(2*y+1)*dg)//(8*dg*dc) for x,y in zip(g,c)]
        self.tot=sum(self.cnt)
    def update(self,s):
        for counts in [self.global_counts,self.local]+([self.parent] if self.parent is not None else []):
            counts[s]+=1
            if sum(counts)>32768:
                counts[:]=[x//2 for x in counts]

class RemainingModel:
    def __init__(self,counts):
        self.active=[i for i,n in enumerate(counts) if n]
        self.cnt=[counts[i] for i in self.active]; self.k=len(self.cnt); self.tot=sum(self.cnt)
    def update(self,s):
        self.cnt[s]-=1; self.tot-=1
        if not self.cnt[s]: self.cnt.pop(s); self.active.pop(s); self.k-=1

class ConditionalRemainingModel:
    """Finite multiset law: positive frequencies on exactly remaining symbols.

    The paid bag restricts support. Neither the current target nor an unpaid
    future word determines these frequencies. Counts and base update after decode.
    """
    def __init__(self,counts,base,beta):
        self.counts=counts;self.base=base
        self.active=[i for i,n in enumerate(counts) if n]
        self.cnt=[base.cnt[i]*(counts[i] if beta else 1) for i in self.active]
        # Prevent the integer range coder's interval from collapsing on long
        # all-constructor runs. Positivity and determinism survive rescaling.
        while sum(self.cnt)>32768:self.cnt=[max(1,n//2) for n in self.cnt]
        self.k=len(self.cnt);self.tot=sum(self.cnt)
    def update(self,s):
        symbol=self.active[s];self.counts[symbol]-=1;self.base.update(symbol)

def run_bags(flags,ids,alphabet):
    result=[]; i=0
    while i<len(flags):
        if not flags[i]: i+=1; continue
        j=i; counts=[0]*alphabet
        while j<len(flags) and flags[j]: counts[ids[j]]+=1; j+=1
        result.append((i,j,counts)); i=j
    return result

def encode(raw,mode='unigram',alpha=0,words=WORDS):
    if mode not in MODES or type(alpha) is not int or not 0<=alpha<=8: raise ValueError('invalid model')
    if mode in ['unigram','bag'] and alpha: raise ValueError('noncontext mode requires zero alpha')
    if not words or list(words)!=sorted(set(words)) or len(words)>255: raise ValueError('invalid lexicon')
    gaps,flags,literals,cases,ids,literal_words=prepare(raw,words)
    left,right,variables=anchors(flags,literal_words)
    enc=BinEncoder(); bag_data=bytearray(); alphabet=len(words)
    if is_bag(mode):
        base=ConditionalModel(alphabet,alpha) if mode!='bag' else None
        for i,j,counts in run_bags(flags,ids,alphabet):
            active=[(s,c) for s,c in enumerate(counts) if c]
            bag_data+=varint(len(active))
            for s,c in active: bag_data+=varint(s)+varint(c)
            if base is None:
                model=RemainingModel(counts)
                for pos in range(i,j):enc.encode_adapt(model,model.active.index(ids[pos]))
                assert model.tot==0
            else:
                previous=-1
                for pos in range(i,j):
                    base.select(context(bag_context_mode(mode),left[pos],right[pos],variables,pos,previous,pos-i))
                    model=ConditionalRemainingModel(counts,base,int(mode[-1]))
                    enc.encode_adapt(model,model.active.index(ids[pos]));previous=ids[pos]
                assert not any(counts)
    else:
        model=ConditionalModel(alphabet,alpha); previous=-1; runpos=0
        for pos,flag in enumerate(flags):
            if not flag: previous=-1; runpos=0; continue
            key=context(mode,left[pos],right[pos],variables,pos,previous,runpos)
            model.select(key); enc.encode_adapt(model,ids[pos]); previous=ids[pos]; runpos+=1
    lex=b'\n'.join(w.encode() for w in words)
    channels=[gzip.compress(c,mtime=0) for c in [lex,gaps,flags,literals,cases]]
    channels+=[enc.finish(),gzip.compress(bytes(bag_data),mtime=0) if is_bag(mode) else b'']
    return b'HPCTOR11'+struct.pack('<BBQI7I',MODES[mode],alpha,len(raw),len(flags),*[len(c) for c in channels])+b''.join(channels)

def decode(archive):
    if archive[:8]!=b'HPCTOR11' or len(archive)<50: raise ValueError('invalid container')
    mode_id,alpha,length,n,*sizes=struct.unpack_from('<BBQI7I',archive,8)
    reverse={v:k for k,v in MODES.items()}
    if mode_id not in reverse or alpha>8 or sum(sizes)+50!=len(archive): raise ValueError('invalid header')
    mode=reverse[mode_id]; offset=50; channels=[]
    for size in sizes: channels.append(archive[offset:offset+size]); offset+=size
    lex,gaps,flags,literals,cases=[gzip.decompress(c) for c in channels[:5]]
    words=lex.split(b'\n'); alphabet=len(words)
    if not words or len(words)>255 or words!=sorted(set(words)) or len(flags)!=n or any(f>1 for f in flags): raise ValueError('invalid structure')
    literal_words=[]; off=0
    for flag in flags:
        if flag: literal_words.append(None)
        else:
            size,off=get_varint(literals,off); word=literals[off:off+size]; off+=size
            if len(word)!=size: raise ValueError('truncated literal')
            literal_words.append(word)
    if off!=len(literals) or len(cases)!=sum(flags) or any(c>2 for c in cases): raise ValueError('invalid literal/case channel')
    left,right,variables=anchors(flags,literal_words)
    dec=BinDecoder(channels[5]); ids=[None]*n
    if is_bag(mode):
        if mode=='bag' and alpha: raise ValueError('invalid bag parameters')
        base=ConditionalModel(alphabet,alpha) if mode!='bag' else None
        bags=gzip.decompress(channels[6]); off=i=0
        while i<n:
            if not flags[i]: i+=1; continue
            j=i
            while j<n and flags[j]: j+=1
            count,off=get_varint(bags,off); counts=[0]*alphabet; previous=-1
            for _ in range(count):
                s,off=get_varint(bags,off); c,off=get_varint(bags,off)
                if not previous<s<alphabet or c<=0: raise ValueError('invalid bag')
                counts[s]=c; previous=s
            if sum(counts)!=j-i: raise ValueError('bag length mismatch')
            if base is None:
                model=RemainingModel(counts)
                for pos in range(i,j):
                    active=model.active[:];s=dec.decode_adapt(model);ids[pos]=active[s]
                assert model.tot==0
            else:
                previous=-1
                for pos in range(i,j):
                    base.select(context(bag_context_mode(mode),left[pos],right[pos],variables,pos,previous,pos-i))
                    model=ConditionalRemainingModel(counts,base,int(mode[-1]));active=model.active[:]
                    s=dec.decode_adapt(model);ids[pos]=active[s];previous=ids[pos]
                assert not any(counts)
            i=j
        if off!=len(bags): raise ValueError('trailing bags')
    else:
        if channels[6] or (mode=='unigram' and alpha): raise ValueError('invalid nonbag parameters')
        model=ConditionalModel(alphabet,alpha); previous=-1; runpos=0
        for pos,flag in enumerate(flags):
            if not flag: previous=-1; runpos=0; continue
            model.select(context(mode,left[pos],right[pos],variables,pos,previous,runpos))
            ids[pos]=dec.decode_adapt(model); previous=ids[pos]; runpos+=1
    result=bytearray(); off=ci=0
    for pos in range(n+1):
        size,off=get_varint(gaps,off); gap=gaps[off:off+size]; off+=size
        if len(gap)!=size: raise ValueError('truncated layout')
        result+=gap
        if pos==n: break
        if not flags[pos]: result+=literal_words[pos]
        else:
            word=words[ids[pos]]; case=cases[ci]; ci+=1
            result+=word if case==0 else word[:1].upper()+word[1:] if case==1 else word.upper()
    if off!=len(gaps) or len(result)!=length: raise ValueError('invalid reconstruction length')
    return bytes(result)

def inspect_sizes(archive):
    _,_,_,_,*sizes=struct.unpack_from('<BBQI7I',archive,8)
    return dict(zip(['lexicon','layout','flags','literals','case','constructor_sequence','bag_metadata'],sizes))
