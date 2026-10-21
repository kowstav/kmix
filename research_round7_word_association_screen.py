"""Normalized causal word-choice experts for the ORIGINAL WRT stream.

The first dictionary code byte is paid. It identifies a prefix-free subtree;
experts predict only its remaining bytes. Sources are completed prefix words,
article counts, a bounded follower graph and a bounded association graph.
No neural weights change. Likelihood screening only, not a qualifying archive.
"""
import argparse,json,math,re,time,hashlib
from pathlib import Path
from collections import OrderedDict,deque,Counter
import numpy as np
from research_round7_wrt import inverse_byte,load_dictionary
from research_round7_field_screen import literal_wrt,SEP,TEND

ALPHAS=(.001,.003,.01,.03,.1,.3,.7)
STOP=set(b'page title text the and of in to a is for on with as by an be are was from at it this that which not or has have his her its also'.split())

class Row:
    def __init__(self,groups,cap):
        self.counts={};self.groups=groups;self.group_counts=Counter();self.total=0;self.cap=cap
    def add(self,w):
        if w in self.counts:self.counts[w]+=1;self.group_counts[self.groups[w]]+=1;self.total+=1
        else:
            n=1
            if len(self.counts)>=self.cap:
                victim=min(self.counts,key=lambda k:(self.counts[k],k));old=self.counts.pop(victim)
                self.group_counts[self.groups[victim]]-=old;n=old+1
            self.counts[w]=n;self.group_counts[self.groups[w]]+=n;self.total+=1
        if self.counts[w]>=65535:
            self.counts={k:(v+1)//2 for k,v in self.counts.items()};self.group_counts=Counter()
            for k,v in self.counts.items():self.group_counts[self.groups[k]]+=v
            self.total=sum(self.counts.values())
    def conditional_parts(self,w,group,prior_word,prior_group,kappa):
        den=self.total+kappa
        return ((self.counts.get(w,0)+kappa*prior_word)/den,
                (self.group_counts.get(group,0)+kappa*prior_group)/den)

class Graph:
    def __init__(self,groups,max_rows=4096,neighbors=64):
        self.rows=OrderedDict();self.groups=groups;self.max_rows=max_rows;self.neighbors=neighbors
    def add(self,s,w):
        if s not in self.rows:
            if len(self.rows)>=self.max_rows:self.rows.popitem(last=False)
            self.rows[s]=Row(self.groups,self.neighbors)
        row=self.rows[s];row.add(w);self.rows.move_to_end(s)
    def row(self,s):return self.rows.get(s)
    def memory(self):return {'rows':len(self.rows),'edges':sum(len(r.counts) for r in self.rows.values())}

class Words:
    def __init__(self,codes,spellings):
        self.codes=codes;self.words=spellings;self.groups=np.asarray([c[0] for c in codes],np.int32)
        self.group_size=np.bincount(self.groups,minlength=256)
        self.global_counts=np.ones(len(codes),np.float64)
        self.global_groups=self.group_size.astype(np.float64);self.global_total=float(len(codes))
        self.article=Row(self.groups,65536);self.follows=Graph(self.groups);self.assoc=Graph(self.groups)
        self.prev=None;self.recent=deque(maxlen=16);self.title=[];self.in_title=False;self.article_events=0
        self.family_names=['uniform','global','article8','article128','prev8','prev128','assoc4_8','assoc4_128','assoc16_8','assoc16_128','title8','title128']
    def reset(self):
        self.article=Row(self.groups,65536);self.prev=None;self.recent.clear();self.title=[];self.in_title=True;self.article_events=0
    def predictions(self,w,conditional=True):
        # w is used ONLY as the observed outcome in probability lookup; all
        # sources and coefficients were determined by the decoded prefix.
        g=self.groups[w];pw=self.global_counts[w]/self.global_total;pg=self.global_groups[g]/self.global_total
        result=[1./(self.group_size[g] if conditional else len(self.codes)),pw/pg if conditional else pw]
        for kappa in (8,128):
            a,b=self.article.conditional_parts(w,g,pw,pg,kappa);result.append(a/b if conditional else a)
        previous=self.follows.row(self.prev)
        for kappa in (8,128):
            a,b=previous.conditional_parts(w,g,pw,pg,kappa) if previous else (pw,pg);result.append(a/b if conditional else a)
        for sources in (list(self.recent)[-4:],list(self.recent),self.title[:8]):
            sources=list(dict.fromkeys(sources))
            rows=[self.assoc.row(s) for s in sources]
            for kappa in (8,128):
                if not rows:result.append(pw/pg if conditional else pw);continue
                parts=[r.conditional_parts(w,g,pw,pg,kappa) if r else (pw,pg) for r in rows]
                result.append(sum(a for a,b in parts)/(sum(b for a,b in parts) if conditional else len(parts)))
        values=np.asarray(result,np.float64)
        if np.any(values<=0) or np.any(values>1+1e-12):raise RuntimeError('Invalid conditional probability')
        return values
    def update(self,w):
        if self.prev is not None:self.follows.add(self.prev,w)
        content=self.words[w] not in STOP and len(self.words[w])>=3
        if content:
            for s in dict.fromkeys(list(self.recent)[-4:]):
                if s!=w:self.assoc.add(s,w);self.assoc.add(w,s)
            self.recent.append(w)
            if self.in_title and w not in self.title and len(self.title)<16:self.title.append(w)
        self.article.add(w);self.article_events+=1;self.prev=w
        self.global_counts[w]+=1;self.global_groups[self.groups[w]]+=1;self.global_total+=1

def logsum(x):
    m=float(np.max(x));return m+math.log2(float(np.exp2(x-m).sum()))

class Mixture:
    def __init__(self,names):
        self.models=[('neutral',0.)]+[(name,a) for name in names for a in ALPHAS]
        self.alpha=np.asarray([a for name,a in self.models]);self.total_gain=0.;self.post={};self.fixed=np.zeros(len(self.models));self.events=0;self.covered=0.;self.oracle=0.
        self.prior=np.full(len(self.models),-math.log2(2*(len(self.models)-1)));self.prior[0]=-1.
    def score(self,probs,baseline_bits,ctx):
        pq=np.r_[1.,np.repeat(probs,len(ALPHAS))]
        # Stable log [(1-alpha) + alpha * P_expert/P_baseline].
        a=self.alpha
        logpq=np.full(len(pq),-np.inf);np.log2(pq,out=logpq,where=pq>0)
        gains=np.logaddexp2(np.log2(1-a),np.where(a>0,np.log2(np.maximum(a,1e-300))+logpq+baseline_bits,-np.inf))
        lp=self.post.setdefault(ctx,self.prior.copy());before=logsum(lp);g=logsum(lp+gains)-before
        lp+=gains;lp-=np.max(lp);self.total_gain+=g;self.fixed+=gains;self.events+=1;self.covered+=baseline_bits;self.oracle+=float(np.max(gains))
    def result(self):
        return {'events':self.events,'baseline_suffix_bits':self.covered,'prequential_saving_bytes':self.total_gain/8.,'context_count':len(self.post),'model_count':len(self.models),'unpaid_best_model_per_event_oracle_bytes':self.oracle/8.,'fixed_models':[{'family':name,'alpha':a,'saving_bytes':float(self.fixed[i]/8.)} for i,(name,a) in enumerate(self.models)]}

def self_test():
    codes=[bytes([240,128+i]) for i in range(2)]+[bytes([240,208,128])]+[bytes([209,128+i]) for i in range(3)]
    model=Words(codes,[b'apple',b'pear',b'fruit',b'king',b'crown',b'queen'])
    model.reset()
    for w in [0,2,1,2,0,2,4,3,5,3]*12:model.update(w)
    for g in (240,209):
        p=sum((model.predictions(w) for w in range(6) if codes[w][0]==g))
        if not np.allclose(p,1.,rtol=0.,atol=1e-12):raise AssertionError(('normalization',p))
    m=Mixture(model.family_names)
    for w in [2,2,3,5]*20:m.score(model.predictions(w),4.,(2,0));model.update(w)
    if not math.isfinite(m.total_gain):raise AssertionError('Mixture numerical failure')
    # The neutral expert has prior 1/2, hence <=1 bit regret per context.
    if m.total_gain<-1.-1e-10:raise AssertionError('Neutral regret bound')
    r=Row(model.groups,2)
    for w in [0,1,2,0,1,2]*100:r.add(w)
    if r.total!=sum(r.counts.values()) or r.total!=sum(r.group_counts.values()):raise AssertionError('Replacement accounting')
    r.counts={0:65534,1:7};r.total=65541;r.group_counts=Counter({240:65541});r.add(0)
    if r.total!=sum(r.counts.values()) or r.total!=sum(r.group_counts.values()):raise AssertionError('Rescale accounting')
    fixture={bytes([128]):b'page',bytes([129]):b'title',bytes([240,128]):b'pear',bytes([240,208,128]):b'fruit',bytes([208,128]):b'apple'}
    raw=literal_wrt(SEP,fixture)+b' '+(bytes([240,128])+b' '+bytes([240,208,128])+b' '+bytes([208,128])+b' ')*10+literal_wrt(TEND,fixture)
    tested=screen(raw,np.full(len(raw),8.,np.float32),fixture)
    if tested['score']['events']!=30:raise AssertionError('Mixed two/three-byte parser fixture')
    print(json.dumps({'self_test':'passed','family_count':len(model.family_names),'normalization_max_error':float(np.max(np.abs(p-1.))),'mixed_prefix_fixture_events':tested['score']['events']}))

def screen(raw,cost,dictionary):
    started=time.monotonic();sep=literal_wrt(SEP,dictionary);tend=literal_wrt(TEND,dictionary)
    offset=raw.find(sep)
    if offset<0:raise ValueError('No article synchronization prefix')
    codes=list(dictionary);spellings=list(dictionary.values());ids={c:i for i,c in enumerate(codes)}
    word=Words(codes,spellings);mixture=Mixture(word.family_names)
    thresholds=sorted([(m.start()+len(sep),'start') for m in re.finditer(re.escape(sep),raw)]+[(m.start()+len(tend),'end') for m in re.finditer(re.escape(tend),raw)])
    threshold=0;prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)];i=offset;tokens=0;diagnostic=Counter();by={};trace=hashlib.sha256()
    while i<len(raw):
        lo=i;c=inverse_byte(raw[i]);i+=1
        if c==12:i=min(i+1,len(raw));continue
        if c<128:continue
        width=1
        if c>207:
            if i>=len(raw):break
            width=2
            if inverse_byte(raw[i])>207:width=3
        end=lo+width
        if end>len(raw):break
        code=bytes(inverse_byte(b) for b in raw[lo:end]);i=end
        if code not in ids:raise ValueError('Invalid dictionary code at '+str(lo))
        while threshold<len(thresholds) and thresholds[threshold][0]<=lo+1:
            available,kind=thresholds[threshold];assert available<=lo+1
            if kind=='start':word.reset()
            else:word.in_title=False
            threshold+=1
        w=ids[code]
        if width>1:
            # First code byte is already decoded. The subtree is known; leaf
            # length may depend on the NEXT byte. Do not use width as context.
            probs=word.predictions(w)
            baseline=float(prefix[end]-prefix[lo+1])
            bucket=0 if word.article_events<16 else 1 if word.article_events<64 else 2 if word.article_events<256 else 3
            ctx=(int(c>=240),bucket)
            before=mixture.total_gain;mixture.score(probs,baseline,ctx)
            gain=mixture.total_gain-before
            cls='first_in_slice' if word.global_counts[w]==1 else 'known_first_in_article' if w not in word.article.counts else 'article_repeat'
            r=by.setdefault(cls,{'events':0,'baseline_suffix_bits':0.,'prequential_saving_bytes':0.})
            r['events']+=1;r['baseline_suffix_bits']+=baseline;r['prequential_saving_bytes']+=gain/8.
            # Probability trace is a reproducibility artifact, not a transmitted hint.
            trace.update(np.asarray([lo,*probs],dtype='<f8').tobytes())
        word.update(w);tokens+=1;diagnostic['code_width_'+str(width)]+=1
        if tokens%100000==0:print(json.dumps({'dictionary_atoms':tokens,'position':i,'saving_bytes':mixture.total_gain/8.,'elapsed_seconds':time.monotonic()-started}),flush=True)
    return {'raw_bytes':len(raw),'baseline_ideal_bytes':float(prefix[-1]/8.),'unscored_prefix_bytes':offset,'dictionary_atoms':tokens,'parser_counts':dict(diagnostic),'contract':{'first_byte':'paid before expert activation','probabilities':'normalized conditional distribution on the known code subtree','sources':'only completed prefix atoms and prefix-recognized article/title markers','mixture':'85 fixed experts including neutral; 1/2 initial mass on neutral; prefix-only posterior updates','neural_retraining':False,'measurement':'ideal final-coder likelihood; packed code, native runtime, RSS and whole-stream histories not measured','coverage':'dictionary code suffixes only, not first code bytes or literal spellings'},'memory':{'followers':word.follows.memory(),'associations':word.assoc.memory(),'row_cap_per_graph':4096,'neighbors_per_row':64,'counter_bits':16,'replacement':'deterministic space-saving per row; row LRU touched on updates','production_fixed_slot_edge_data_bytes_per_graph':4096*64*6},'probability_trace_sha256':trace.hexdigest(),'by_occurrence_class':by,'score':mixture.result(),'wall_seconds':time.monotonic()-started}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--raw');ap.add_argument('--cost');ap.add_argument('--dictionary');ap.add_argument('--out');args=ap.parse_args()
    if args.self_test:self_test()
    else:
        raw=Path(args.raw).read_bytes();cost=np.fromfile(args.cost,'<f4')
        if len(raw)!=len(cost):raise ValueError('Incomplete baseline costs')
        result=screen(raw,cost,load_dictionary(args.dictionary));Path(args.out).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='score'}));print(json.dumps({k:v for k,v in result['score'].items() if k!='fixed_models'}))
