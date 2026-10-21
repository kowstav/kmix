"""I01/I02/I03: dictionary-derived relations and causal echo controls.

No fitted offline graph, future donor, neural SGD or unnormalized bit bonus.
Charges all post-marker bytes, including truncated code/escape prefixes at EOF.
"""
import pathlib,json,time,hashlib,re,collections,types,resource,numpy as np
from research_round7_wrt import load_dictionary,inverse_byte
from research_round7_field_screen import literal_wrt,SEP,TEND
from research_round7_word_association_screen import Mixture

GRAPH_CACHE={}
def lcp(a,b):
    i=0
    while i<min(len(a),len(b)) and a[i]==b[i]:i+=1
    return i

def graph(words):
    key=tuple(words)
    if key in GRAPH_CACHE:return GRAPH_CACHE[key]
    started=time.monotonic();N=len(words);index={w:i for i,w in enumerate(words)}
    pref=collections.defaultdict(list);suff=collections.defaultdict(list);big=collections.defaultdict(list);dele=collections.defaultdict(list);bags=collections.defaultdict(list)
    def add(d,k,i):
        if len(d[k])<64:d[k].append(i)
    feats=np.zeros((N,3,26),np.float32)
    for i,w in enumerate(words):
        for n in [2,3]:
            if len(w)>=n:add(pref,w[:n],i);add(suff,w[-n:],i)
        for j in range(len(w)-1):add(big,w[j:j+2],i)
        for j in range(len(w)):add(dele,w[:j]+w[j+1:],i)
        add(bags,bytes(sorted(w)),i)
        for j,c in enumerate(w):
            if 97<=c<=122:
                u=(j+1)/len(w);feats[i,:,c-97]+=[1,u,u*u]
    norms=np.linalg.norm(feats,axis=2,keepdims=True);feats/=np.maximum(norms,1e-20)
    graphs=[[],[],[],[]];capped=0
    for i,w in enumerate(words):
        pp=set();ee=set();mm=set(bags[bytes(sorted(w))])
        for n in [2,3]:
            if len(w)>=n:pp.update(pref[w[:n]]);pp.update(suff[w[-n:]])
        for j in range(len(w)-1):mm.update(big[w[j:j+2]])
        ee.update(dele[w])
        for j in range(len(w)):
            s=w[:j]+w[j+1:];ee.update(dele[s])
            if s in index:ee.add(index[s])
        for c in [pp,ee,mm]:c.discard(i)
        if max(len(pp),len(ee),len(mm),0)>128:capped+=1
        pp=sorted(pp)[:128];ee=sorted(ee)[:128];mm=sorted(mm|set(pp)|set(ee))[:128]
        def pscore(v):return (lcp(w,words[v])+lcp(w[::-1],words[v][::-1]))/max(len(w),len(words[v]),1)
        def escore(v):return 1/(1+abs(len(w)-len(words[v])))
        def mscore(v):return float(np.sum(np.sum(feats[i]*feats[v],axis=1)*[.5,.3,.2]))
        for channel,pool,score in [(0,pp,pscore),(1,ee,escore),(2,mm,mscore)]:
            ranked=sorted(((v,max(score(v),1e-6)) for v in pool),key=lambda z:(-z[1],z[0]))[:8]
            z=sum(s for _,s in ranked);graphs[channel].append([(v,s/z) for v,s in ranked] if z else [])
        # Deterministic control, coarse-rank/length matched to moment neighbors.
        random=[];used={i}
        for v,weight in graphs[2][-1]:
            lo=v//256*256;hi=min(N,lo+256);pool=[j for j in range(lo,hi) if j not in used and abs(len(words[j])-len(words[v]))<=1]
            if not pool:pool=[j for j in range(N) if j not in used]
            if not pool:break
            d=int.from_bytes(hashlib.blake2s(w+v.to_bytes(4,'little')+b'control42',digest_size=4).digest(),'little')
            t=pool[d%len(pool)];used.add(t);random.append((t,weight))
        z=sum(s for _,s in random);graphs[3].append([(v,s/z) for v,s in random] if z else [])
    examples={}
    for s in [b'no',b'know',b'now',b'diamond',b'the']:
        if s in index:examples[s.decode()]={name:[words[v].decode('ascii',errors='replace') for v,_ in graphs[c][index[s]]] for c,name in enumerate(['prefix_suffix','deletion_signature','letter_moments','matched_random'])}
    meta={'dictionary_words':N,'K':8,'posting_cap':64,'candidate_cap':128,'capped_source_words':capped,
          'startup_seconds':time.monotonic()-started,'feature_array_bytes':feats.nbytes,'graph_edges':sum(len(row) for g in graphs for row in g),
          'examples':examples,'note':'Bounded dictionary-derived neighbors; no exhaustive-search recall claim, corpus-fit edges or geometry input'}
    GRAPH_CACHE[key]=(graphs,meta);return graphs,meta

class Echo:
    def __init__(self):self.mass={};self.total=0.
    def reset(self):self.mass.clear();self.total=0.
    def update(self,edges):
        for v in list(self.mass):
            value=self.mass[v]*(127/128)
            if value<1e-12:del self.mass[v]
            else:self.mass[v]=value
        for v,s in edges:self.mass[v]=self.mass.get(v,0.)+s
        while len(self.mass)>128:
            v=min(self.mass,key=lambda v:(self.mass[v],v));del self.mass[v]
        self.total=sum(self.mass.values())

class Words:
    last=None
    def __init__(self,codes,spellings):
        self.words=spellings;self.graphs,self.graph_meta=graph(spellings)
        self.rank=1/(np.arange(len(codes),dtype=np.float64)+16);self.rank/=self.rank.sum()
        self.global_counts=np.ones(len(codes),np.int64);self.global_total=0
        self.family_names=['rank_prior','global_rank64','exact_decay128','prefix_suffix_decay128',
                           'deletion_signature_decay128','letter_moment_decay128','matched_random_decay128']
        self.echo=[Echo() for _ in range(5)];self.clock=0;self.diagnostics={};self.in_title=True
        self.reset();Words.last=self
    def reset(self):
        self.article=types.SimpleNamespace(counts=collections.Counter());self.article_events=0;self.in_title=True
        for e in self.echo:e.reset()
        self.last_source=collections.deque();self.clock=0
    def predictions(self,w,conditional=False):
        assert not conditional
        r=self.rank[w];p=[r,(self.global_counts[w]-1+64*r)/(self.global_total+64)]
        p.extend((e.mass.get(w,0.)+64*r)/(e.total+64) for e in self.echo)
        return np.asarray(p,np.float64)
    def prefix_predictions(self,ids):return sum((self.predictions(w) for w in ids),np.zeros(len(self.family_names)))
    def update(self,w):
        self.echo[0].update([(w,1.)])
        for e,g in zip(self.echo[1:],self.graphs):e.update(g[w])
        self.global_counts[w]+=1;self.global_total+=1;self.article.counts[w]+=1;self.article_events+=1
        self.clock+=1;self.last_source.append((self.clock,w))
        while self.last_source and self.clock-self.last_source[0][0]>256:self.last_source.popleft()
    def coverage(self,w,baseline,cls):
        # Observational diagnostic only; never chooses a predictor or gate.
        for c,g in enumerate(self.graphs):
            bins=set()
            for t,u in self.last_source:
                d=self.clock+1-t
                if any(v==w for v,_ in g[u]):bins.add(0 if d<=4 else 1 if d<=16 else 2 if d<=64 else 3)
            for b in bins:
                k=(c,b,cls);row=self.diagnostics.setdefault(k,[0,0.]);row[0]+=1;row[1]+=baseline

def screen(raw,cost,dictionary,diagnostic=False):
    start=time.monotonic();codes=list(dictionary);ids={c:i for i,c in enumerate(codes)}
    sep=literal_wrt(SEP,dictionary);tend=literal_wrt(TEND,dictionary);first=raw.find(sep)
    assert first>=0;i=first+len(sep);offset=i;words=Words(codes,list(dictionary.values()));mix=Mixture(words.family_names)
    markers=sorted([(m.end(),'start') for m in re.finditer(re.escape(sep),raw)]+[(m.end(),'end') for m in re.finditer(re.escape(tend),raw)])
    marker=0;prev=3;events=0;atoms=0;classes={};trace=hashlib.sha256();prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)]
    while i<len(raw):
        lo=i
        while marker<len(markers) and markers[marker][0]<=lo:
            if markers[marker][1]=='start':words.reset()
            else:words.in_title=False
            marker+=1
        ctx=(prev,0 if words.article_events<16 else 1 if words.article_events<64 else 2 if words.article_events<256 else 3)
        c=inverse_byte(raw[i]);i+=1;w=None;cut=False;probs=np.zeros(len(words.family_names))
        if c==12:
            if i<len(raw):i+=1;cls='literal_escape'
            else:cut=True;cls='cut_escape_prefix'
        elif c>=128:
            code=[c]
            if c>207:
                if i==len(raw):cut=True
                else:
                    c2=inverse_byte(raw[i]);code.append(c2);i+=1
                    if c2>207:
                        if i==len(raw):cut=True
                        else:code.append(inverse_byte(raw[i]));i+=1
            code=bytes(code)
            if cut:
                probs=words.prefix_predictions([j for j,s in enumerate(codes) if s.startswith(code)]);cls='cut_dictionary_prefix'
            else:
                assert code in ids,'Invalid complete code';w=ids[code];probs=words.predictions(w)
                cls='first_in_slice' if words.global_counts[w]==1 else 'known_first_in_article' if w not in words.article.counts else 'article_repeat';atoms+=1
        else:cls='literal_syntax_or_case'
        baseline=float(prefix[i]-prefix[lo]);before=mix.total_gain;mix.score(probs,baseline,ctx)
        row=classes.setdefault(cls,{'events':0,'baseline_bits':0.,'saving_bytes':0.});row['events']+=1;row['baseline_bits']+=baseline;row['saving_bytes']+=(mix.total_gain-before)/8
        trace.update(np.asarray([lo,*ctx,*probs],'<f8').tobytes())
        if w is not None:
            if diagnostic:words.coverage(w,baseline,cls)
            words.update(w);prev=2
        else:prev=0 if c in (32,9,10,13) else 1 if c in (7,64) else 4 if 65<=c<=90 or 97<=c<=122 else 3
        events+=1
        if events%200000==0:print(json.dumps({'events':events,'position':i,'saving_bytes':mix.total_gain/8,'wall_seconds':time.monotonic()-start}),flush=True)
        if cut:break
    assert abs(sum(r['baseline_bits'] for r in classes.values())-(prefix[-1]-prefix[offset]))<1e-5,'Uncharged tail/prefix'
    return {'raw_bytes':len(raw),'baseline_ideal_bytes':float(prefix[-1]/8),'unscored_prefix_bytes':offset,'dictionary_atoms':atoms,
            'score':mix.result(),'by_class':classes,'graph':words.graph_meta,'memory_slots_per_family':128,'decay_per_dictionary_atom':'127/128',
            'coverage': [{'channel':k[0],'lag_bin':k[1],'class':k[2],'events':v[0],'baseline_bits':v[1]} for k,v in sorted(words.diagnostics.items())],
            'trace_sha256':trace.hexdigest(),'wall_seconds':time.monotonic()-start,'prototype_peak_rss_kbytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'contract':'Prefix-only additive root expert, all outcomes and EOF prefixes charged; not global P0 tilt, native archive, full package or20% result',
            'neural_training':False,'paid_rental_usd':0,'deletions':[]}

def tests():
    words=[b'no',b'know',b'now',b'king',b'queen',b'on'];codes=[bytes([128+i]) for i in range(len(words))];m=Words(codes,words)
    for j in range(100):
        assert np.allclose(sum(m.predictions(w) for w in range(len(words))),1,atol=1e-12,rtol=0)
        m.update(j%len(words))
        assert all(len(e.mass)<=128 and abs(e.total-sum(e.mass.values()))<1e-12 for e in m.echo)
    d={bytes([128]):b'page',bytes([129]):b'title',bytes([240,128]):b'pear',bytes([240,208,128]):b'fruit'}
    base=literal_wrt(SEP,d)+b' '+bytes([240,128])+b' '
    for tail in [b'',bytes([240]),bytes([240,208]),bytes([12]),bytes([12,255])]:
        raw=base+tail;r=screen(raw,np.full(len(raw),8.,np.float32),d)
        assert r['score']['baseline_suffix_bits']==(len(raw)-len(literal_wrt(SEP,d)))*8
    print(json.dumps({'tests':'normalization/eviction/deterministic graphs/mixed codes/full-marker/partial-code/escape EOF passed'}),flush=True)

if __name__=='__main__':
    tests();out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'idea_arch_screens_v1';dest.mkdir(exist_ok=False)
    dictionary=load_dictionary(out/'preserved/gen/.dict');rows=[]
    for n in 'abcd':
        p=out/'preserved/slices'/(n+'2m.bin') if n in 'ab' else out/(n+'2m.bin')
        raw=p.read_bytes();cost=np.fromfile(out/'lex_native_2m'/(n+'_cost.f32'),'<f4');assert len(raw)==len(cost)==2000000
        r=screen(raw,cost,dictionary,diagnostic=False)
        # Full256-lag diagnostic scans are deliberately separate: bounded echo
        # prediction stays inexpensive, and coverage is not a coding gain.
        (dest/(n+'.json')).write_text(json.dumps(r,indent=2));rows.append({'slice':n,'saving_bytes':r['score']['prequential_saving_bytes'],'wall_seconds':r['wall_seconds']})
        (dest/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[-1]),flush=True)
    print('IDEA_ARCH_SCREENS_V1_COMPLETE',flush=True)
