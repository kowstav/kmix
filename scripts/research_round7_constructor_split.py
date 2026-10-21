"""I11: raw-byte-reversible constructor/content two-stream screen.

No parser, neural retraining, learned noun labels, or free future context.
Fixed explicit function-word lexicon; all other ASCII words are anchors.
Case controls, separators, markup, partial EOF and original WRT headers survive
as exact raw bytes. Both channels and every table/length/order bit are paid.
zlib/LZMA results are matched-codec screens, never cmix archive improvements.
"""
import argparse,collections,hashlib,itertools,json,lzma,math,pathlib,resource,time,zlib
import numpy as np
import re
from research_round7_wrt import load_dictionary,decode_wrt,encoded_span,inverse_byte
from research_round7_field_screen import literal_wrt,SEP

LEXICON=tuple(sorted(set(b'''a an the and or but nor so yet if unless because although though while whereas
as than that whether until once when whenever where wherever before after since
of to in on at by for from with without within into onto upon over under above
below between among through across around against along toward towards about
off out up down past beyond beside besides during except despite per via
i me my mine myself we us our ours ourselves you your yours yourself yourselves
he him his himself she her hers herself it its itself they them their theirs themselves
who whom whose which what this these those each either neither every all any some
no none both many few several much more most less least such same other another
be am is are was were been being do does did have has had having can could may
might must shall should will would not never only also even just very too quite
rather almost perhaps here there then now ever still already again else'''.split())))
LEXSET=set(LEXICON)
ROOT=pathlib.Path('/kaggle/working/hp_round7')
DEST=ROOT/'constructor_split_v1'

def vu(n):
    assert n>=0
    b=bytearray()
    while n>=128:b.append((n&127)|128);n>>=7
    b.append(n);return bytes(b)

def blob(b):return vu(len(b))+b

class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def integer(self):
        n=0;s=0
        while True:
            assert self.i<len(self.b),'truncated integer'
            c=self.b[self.i];self.i+=1;n|=(c&127)<<s
            if c<128:return n
            s+=7;assert s<1000000
    def blob(self):
        n=self.integer();assert self.i+n<=len(self.b)
        b=self.b[self.i:self.i+n];self.i+=n;return b
    def done(self):assert self.i==len(self.b),'unconsumed bytes'

def ways(words):
    v=math.factorial(len(words))
    for c in collections.Counter(words).values():v//=math.factorial(c)
    return v

def rank_multiset(seq):
    c=collections.Counter(seq);symbols=sorted(c);w=ways(seq);n=len(seq);rank=0
    for x in seq:
        for a in symbols:
            if a>=x:break
            if c[a]:rank+=w*c[a]//n
        w=w*c[x]//n;c[x]-=1;n-=1
    assert w==1;return rank

def unrank_multiset(bag,rank):
    c=collections.Counter(bag);symbols=sorted(c);w=ways(bag);n=len(bag);seq=[]
    assert 0<=rank<w
    while n:
        for a in symbols:
            if not c[a]:continue
            block=w*c[a]//n
            if rank>=block:rank-=block;continue
            seq.append(a);w=block;c[a]-=1;n-=1;break
        else:raise AssertionError('invalid permutation rank')
    assert rank==0;return tuple(seq)

class Bits:
    def __init__(self,b=None):self.data=bytearray() if b is None else b;self.n=0
    def put(self,v,k):
        assert 0<=v<(1<<k) if k else v==0
        for i in range(k):
            if self.n%8==0:self.data.append(0)
            self.data[self.n//8]|=((v>>i)&1)<<(self.n%8);self.n+=1
    def get(self,k):
        assert self.n+k<=len(self.data)*8
        v=0
        for i in range(k):v|=((self.data[self.n//8]>>(self.n%8))&1)<<i;self.n+=1
        return v

def split_raw(raw,dictionary):
    first=raw.find(literal_wrt(SEP,dictionary));assert first>=0
    offset=first+len(literal_wrt(SEP,dictionary))
    decoded,starts,ends,_=decode_wrt(raw[offset:],dictionary)
    anchors=[];gaps=[];seps=[];words=[];labels=[];spans=[];last=0;word_count=0
    # Raw spans are disjoint; nothing is reconstructed through an approximate inverse.
    for m in re.finditer(rb'[A-Za-z]+',decoded):
        lo,hi=encoded_span(starts,ends,m.start(),m.end());lo+=offset;hi+=offset
        assert last<=lo<hi<=len(raw),'overlapping word/control spans'
        seps.append(raw[last:lo]);payload=raw[lo:hi];word_count+=1
        if m.group().lower() in LEXSET:
            words.append(payload);labels.append(m.group().lower());spans.append((lo,hi))
        else:
            gaps.append((tuple(words),tuple(seps),tuple(labels)));anchors.append(payload)
            words=[];seps=[];labels=[]
        last=hi
    seps.append(raw[last:]);gaps.append((tuple(words),tuple(seps),tuple(labels)))
    assert len(gaps)==len(anchors)+1
    assert reconstruct(anchors,[(w,s) for w,s,_ in gaps])==raw
    return anchors,gaps,spans,word_count,offset

def reconstruct(anchors,gaps):
    out=bytearray()
    for i,(w,s) in enumerate(gaps):
        assert len(s)==len(w)+1
        for j,x in enumerate(w):out.extend(s[j]);out.extend(x)
        out.extend(s[-1])
        if i<len(anchors):out.extend(anchors[i])
    return bytes(out)

def encode(anchors,gaps,mode):
    content=vu(len(anchors))+b''.join(blob(w) for w in anchors)
    dst=bytearray(b'CG1'+bytes([mode]));dst.extend(vu(len(gaps)))
    table=[];lookup={};bits=Bits()
    if mode:
        for words,_,_ in gaps:
            key=words if mode==1 else tuple(sorted(words))
            if key not in lookup:lookup[key]=len(table);table.append(key)
            if mode==2:bits.put(rank_multiset(words),(ways(key)-1).bit_length())
        dst.extend(vu(len(table)))
        for key in table:dst.extend(vu(len(key)));dst.extend(b''.join(blob(w) for w in key))
        if mode==2:dst.extend(vu(bits.n));dst.extend(blob(bytes(bits.data)))
    for words,seps,_ in gaps:
        if mode:dst.extend(vu(lookup[words if mode==1 else tuple(sorted(words))]))
        else:dst.extend(vu(len(words)));dst.extend(b''.join(blob(w) for w in words))
        dst.extend(b''.join(blob(s) for s in seps))
    return content,bytes(dst),{'raw_template_count':len(table),'permutation_stream_bits':bits.n,
                              'template_table_bytes':len(vu(len(table)))+sum(len(vu(len(k)))+sum(len(blob(w)) for w in k) for k in table) if mode else 0}

def decode(content,grammar):
    c=Reader(content);anchors=[c.blob() for _ in range(c.integer())];c.done()
    assert grammar[:3]==b'CG1' and grammar[3] in (0,1,2)
    mode=grammar[3];g=Reader(grammar);g.i=4;n=g.integer();assert n==len(anchors)+1
    table=[];bits=None
    if mode:
        for _ in range(g.integer()):table.append(tuple(g.blob() for _ in range(g.integer())))
        if mode==2:
            bit_count=g.integer();bits=Bits(g.blob());assert len(bits.data)==(bit_count+7)//8
    gaps=[]
    for _ in range(n):
        if mode:
            key=table[g.integer()]
            words=key if mode==1 else unrank_multiset(key,bits.get((ways(key)-1).bit_length()))
        else:words=tuple(g.blob() for _ in range(g.integer()))
        gaps.append((words,tuple(g.blob() for _ in range(len(words)+1))))
    g.done()
    if mode==2:
        assert bits.n==bit_count
        if bit_count%8:assert bits.data[-1]>>(bit_count%8)==0,'nonzero padding'
    return reconstruct(anchors,gaps)

def package(c,g,codec):
    compress=(lambda b:zlib.compress(b,9)) if codec=='zlib9' else (lambda b:lzma.compress(b,preset=6))
    return b'CTP1'+bytes([codec=='lzma6'])+blob(compress(c))+blob(compress(g))

def unpack(p):
    assert p[:4]==b'CTP1' and p[4] in (0,1)
    decompress=zlib.decompress if p[4]==0 else lzma.decompress
    r=Reader(p);r.i=5;c=decompress(r.blob());g=decompress(r.blob());r.done();return decode(c,g)

def entropy_bits(counter):
    n=sum(counter.values());return sum(v*math.log2(n/v) for v in counter.values()) if n else 0.

def selftest():
    # Distinct permutations, repeated words, empty constructors and byte framing.
    for seq in itertools.product((b'a',b'b',b'c'),repeat=5):
        rank=rank_multiset(seq);assert unrank_multiset(tuple(sorted(seq)),rank)==seq
    d={bytes([128]):b'page',bytes([129]):b'title',bytes([130]):b'the',bytes([131]):b'of',bytes([132]):b'and'}
    fixtures=[b'The camel is there. A camel was there.',b'of of and, and of of! CAMEL &amp; camel\n',
              b"there stood a camel. There appeared another camel; '\x00\xff' camel",b'the and of',b'Camel']
    for text in fixtures:
        # Literal fixture encoder deliberately retains uppercase and escapes
        # control/high bytes; literal_wrt is only a lower-case marker helper.
        payload=bytearray()
        for c in text:
            if c in (6,7,12,64) or c>=128:payload.append(inverse_byte(12))
            payload.append(inverse_byte(c))
        raw=literal_wrt(SEP,d)+bytes(payload)+b'\xf0' # retain partial EOF verbatim
        a,g,_,_,_=split_raw(raw,d)
        for mode in (0,1,2):
            c,s,_=encode(a,g,mode);assert decode(c,s)==raw
            for codec in ('zlib9','lzma6'):assert unpack(package(c,s,codec))==raw
    print(json.dumps({'I11_selftest':'PASS','multiset_rank_unrank_sequences':243,'raw_case_punctuation_binary_EOF_roundtrip':True}),flush=True)

def audit(raw,cost,dictionary):
    t=time.monotonic();cpu=time.process_time();anchors,gaps,spans,nwords,offset=split_raw(raw,dictionary)
    prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)]
    constructor_bits=sum(float(prefix[b]-prefix[a]) for a,b in spans)
    ordered=collections.Counter(labels for _,_,labels in gaps);bags=collections.Counter(tuple(sorted(labels)) for _,_,labels in gaps)
    nonempty=sum(v for k,v in ordered.items() if k);multi=sum(v for k,v in ordered.items() if len(k)>=2)
    order_information=entropy_bits(ordered)-entropy_bits(bags)
    seq_sizes=collections.Counter(len(w) for w,_,_ in gaps)
    rows=[]
    baselines={'zlib9':len(zlib.compress(raw,9)),'lzma6':len(lzma.compress(raw,preset=6))}
    for mode,label in enumerate(('direct','ordered_templates','multiset_plus_order')):
        c,g,meta=encode(anchors,gaps,mode);assert decode(c,g)==raw
        for codec in ('zlib9','lzma6'):
            begun=time.monotonic();packet=package(c,g,codec);assert unpack(packet)==raw
            rows.append({'representation':label,'codec':codec,'candidate_archive_bytes':len(packet),
                         'matched_original_archive_bytes':baselines[codec],
                         'bytes_saved_before_incremental_decoder':baselines[codec]-len(packet),
                         'content_serialized_bytes':len(c),'grammar_serialized_bytes':len(g),**meta,
                         'packet_sha256':hashlib.sha256(packet).hexdigest(),'roundtrip':'PASS',
                         'encode_plus_decode_wall_seconds':time.monotonic()-begun})
    return {'input_bytes':len(raw),'ASCII_words_after_first_page_marker':nwords,'content_anchor_count':len(anchors),
            'constructor_occurrences':len(spans),'constructor_gap_count':len(gaps),'nonempty_gaps':nonempty,'gaps_with_two_or_more_constructors':multi,
            'constructor_length_counts':dict(sorted(seq_sizes.items())),'fixed_lexicon_count':len(LEXICON),
            'fixed_lexicon_sha256':hashlib.sha256(b' '.join(LEXICON)).hexdigest(),'ordered_casefold_templates':len(ordered),
            'multiset_casefold_templates':len(bags),'distinct_template_count_reduction_fraction':1-len(bags)/len(ordered),
            'casefold_uniform_permutation_information_bits':sum(v*math.log2(ways(k)) for k,v in ordered.items()),
            'casefold_empirical_conditional_order_bits_in_sample_only':order_information,
            'constructor_native_span_bits':constructor_bits,'all_native_bits':float(prefix[-1]),
            'constructor_native_span_share':constructor_bits/float(prefix[-1]),'unclassified_prefix_bytes':offset,
            'screen_rows':rows,'input_sha256':hashlib.sha256(raw).hexdigest(),
            'cost_sha256':hashlib.sha256(cost.astype('<f4',copy=False).tobytes()).hexdigest(),
            'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-t,
            'prototype_peak_RSS_KiB_process_to_date':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'interpretation':'Exact raw WRT roundtrip and paid two-stream packet; matched zlib/LZMA screening only. Native span bits are observational budgets, not a new cmix codelength. Whole-slice template/entropy counts are not free causal model features.',
            'neural_training':False,'paid_rental_usd':0,'deletions':[]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--selftest',action='store_true');args=p.parse_args();selftest()
    if not args.selftest:
        DEST.mkdir(exist_ok=False)
        dictionary=load_dictionary(ROOT/'preserved/gen/.dict');rows=[]
        manifest={'status':'RUNNING','experiment':'I11 constructor/content raw-reversible matched-codec screen',
                  'fixed_before_run':['explicit function lexicon','direct/ordered/multiset+order','zlib9/lzma6','all ABCD2M'],
                  'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'neural_training':False,'paid_rental_usd':0,'deletions':[]}
        (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2))
        try:
            for n in 'abcd':
                ip=ROOT/'preserved/slices'/(n+'2m.bin') if n in 'ab' else ROOT/(n+'2m.bin')
                cp=ROOT/'lex_native_2m'/(n+'_cost.f32');raw=ip.read_bytes();cost=np.fromfile(cp,'<f4')
                assert len(raw)==len(cost)==2000000
                r=audit(raw,cost,dictionary);r['slice']=n;rows.append(r)
                (DEST/(n+'.json')).write_text(json.dumps(r,indent=2));(DEST/'summary.json').write_text(json.dumps(rows,indent=2))
                print(json.dumps({'slice':n,'constructors':r['constructor_occurrences'],'native_share':r['constructor_native_span_share'],
                                  'screen_saved_bytes':[v['bytes_saved_before_incremental_decoder'] for v in r['screen_rows']],
                                  'wall_seconds':r['wall_seconds']}),flush=True)
            manifest['status']='COMPLETE'
        except BaseException as exc:
            manifest['status']='FAILED';manifest['error']=repr(exc);raise
        finally:(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2))
        print('CONSTRUCTOR_SPLIT_SCREEN_COMPLETE',flush=True)
