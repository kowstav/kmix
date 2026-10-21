"""I05 pilot: normalized, quantized bit residuals relative to a word prior.

Uses actual FINAL native integer probabilities, not neural logits. Expert
features are computed before each bit; word state changes only on completed
dictionary codes. Every post-synchronization bit, including literals and EOF,
is scored. Root word-type probabilities cancel in the expert/prior contrast.
"""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

import argparse,hashlib,json,math,pathlib,time
import numpy as np
from research_round7_directed_lag_screen import Words,LAGS
from research_round7_wrt import inverse_byte,load_dictionary
from research_round7_field_screen import literal_wrt,SEP

STRENGTHS=(-1.,-.5,-.125,.125,.5,1.)


class Tree:
    def __init__(self,dictionary,words):
        self.child=[[-1,-1]];self.leaf={};self.paths=[];self.rank=[0.]
        for w,code in enumerate(dictionary):
            path=[0];node=0
            for c in code:
                b=inverse_byte(c)
                for j in range(7,-1,-1):
                    bit=(b>>j)&1
                    if self.child[node][bit]<0:
                        self.child[node][bit]=len(self.child);self.child.append([-1,-1]);self.rank.append(0.)
                    node=self.child[node][bit];path.append(node)
            assert node not in self.leaf and self.child[node]==[-1,-1]
            self.leaf[node]=w;self.paths.append(path)
            for v in path:self.rank[v]+=float(words.rank[w])
        self.rank=np.asarray(self.rank,np.float64);self.global_mass=np.zeros(len(self.child),np.int64)
        self.lo=np.zeros(len(self.child),np.int32);self.hi=np.zeros(len(self.child),np.int32);self.position=np.zeros(len(dictionary),np.int32)
        counter=0
        def visit(node):
            nonlocal counter
            self.lo[node]=counter
            if node in self.leaf:self.position[self.leaf[node]]=counter;counter+=1
            else:
                for c in self.child[node]:
                    if c>=0:visit(c)
            self.hi[node]=counter
        visit(0);assert counter==len(dictionary)

    def mass(self,node,words):
        if node<0:return np.zeros(len(words.family_names))
        g=(self.global_mass[node]+64*self.rank[node])/(words.global_total+64)
        result=[self.rank[node],g]
        lo,hi=int(self.lo[node]),int(self.hi[node])
        for j,d in enumerate(LAGS):
            row=words.rows.get((j,words.recent[-d])) if len(words.recent)>=d else None
            if row is None:result.append(g)
            else:
                count=sum(c for w,c in row.counts.items() if lo<=self.position[w]<hi)
                result.append((count+32*g)/(row.total+32))
        result.append(sum(a*p for a,p in zip((.5,.25,.125,.0625,.03125,.03125),result[2:])))
        return np.asarray(result,np.float64)

    def probabilities(self,node,words):
        if node<0:return np.full(len(words.family_names),.5),False
        zero,one=self.child[node];a,b=self.mass(zero,words),self.mass(one,words)
        den=a+b
        if not np.all(den>0):return np.full(len(words.family_names),.5),False
        return b/den,True

    def observe_word(self,w):
        for node in self.paths[w]:self.global_mass[node]+=1


def logit(x):
    x=np.clip(x,1/65536,65535/65536)
    return np.log(x)-np.log1p(-x)


def screen(raw,p0,dictionary,strengths=STRENGTHS):
    begun=time.monotonic();assert len(p0)==8*len(raw) and np.all((p0>=1)&(p0<=65535))
    sep=literal_wrt(SEP,dictionary)
    first=raw.find(sep);assert first>=0
    offset=first+len(sep)
    markers=set();k=raw.find(sep)
    while k>=0:markers.add(k+len(sep));k=raw.find(sep,k+1)
    codes=list(dictionary);ids={c:i for i,c in enumerate(codes)}
    words=Words(codes,list(dictionary.values()));tree=Tree(dictionary,words)
    families=words.family_names[2:];models=[('neutral',0.)]+[(name,s) for name in families for s in strengths]
    factors=np.asarray([s for _,s in models]);prior=np.full(len(models),math.log(.5/max(len(models)-1,1)));prior[0]=math.log(.5) if len(models)>1 else 0.
    post={};fixed=np.zeros(len(models));gain=0.;base_bits=0.;node=0;code=[];escape=False;previous=3;trace=hashlib.sha256();events=0
    for i in range(offset,len(raw)):
        if i in markers:words.reset()
        # The parser category derives only from previously completed bytes.
        age=0 if words.article_events<16 else 1 if words.article_events<64 else 2 if words.article_events<256 else 3
        for j in range(8):
            pb=int(p0[8*i+j]);p=pb/65536.
            experts,valid=tree.probabilities(node,words) if not escape else (np.full(len(words.family_names),.5),False)
            delta=np.clip(logit(experts[2:])-logit(experts[1]),-8.,8.) if valid else np.zeros(len(families))
            residual=np.r_[0.,np.repeat(delta,len(strengths))]*factors
            scores=logit(p)+residual
            q=1/(1+np.exp(-scores));ints=np.clip(np.floor(q*65536+.5),1,65535).astype(np.uint16);ints[0]=pb
            # An exact zero correction returns the old integer probability.
            ints[residual==0]=pb
            ctx=(j,min(len(code),2),age,previous)
            lp=post.setdefault(ctx,prior.copy());weight=np.exp(lp-np.max(lp));weight/=weight.sum()
            selected=int(np.clip(math.floor(float(weight@ints.astype(np.float64))+.5),1,65535))
            y=(raw[i]>>(7-j))&1
            probs=(ints.astype(np.float64) if y else 65536.-ints.astype(np.float64))/65536.
            actual=(selected if y else 65536-selected)/65536.
            old=(pb if y else 65536-pb)/65536.
            improvement=math.log2(actual/old);gain+=improvement;base_bits-=math.log2(old)
            logs=np.log(probs);lp+=logs;lp-=np.max(lp);fixed+=np.log2(probs/old)
            trace.update(selected.to_bytes(2,'little'));events+=1
            if not escape and node>=0:node=tree.child[node][y]
        c=inverse_byte(raw[i])
        if escape:escape=False;node=0;code=[]
        elif not code and c==12:escape=True;node=-1
        elif not code and c<128:
            node=0;previous=0 if c in (32,9,10,13) else 1 if c in (7,64) else 3
        else:
            code.append(c)
            complete=len(code)==1 and c<=207 or len(code)==2 and c<=207 or len(code)==3
            if complete:
                logical=bytes(code);assert logical in ids,('Invalid completed code',i,logical)
                w=ids[logical];tree.observe_word(w);words.update(w);code=[];node=0;previous=2
        if (i-offset+1)%8192==0:print(json.dumps({'processed_bytes':i-offset+1,'saving_bytes':gain/8,'wall_seconds':time.monotonic()-begun}),flush=True)
    assert events==8*(len(raw)-offset)
    return {'raw_bytes':len(raw),'unscored_prefix_bytes':offset,'scored_bits':events,'baseline_scored_bits':base_bits,
            'prequential_quantized_saving_bytes':gain/8,'context_count':len(post),'model_count':len(models),
            'fixed_models':[{'family':n,'strength':s,'saving_bytes':float(fixed[i]/8)} for i,(n,s) in enumerate(models)],
            'selected_probability_trace_sha256':trace.hexdigest(),'word_memory':words.memory(),
            'tree_nodes':len(tree.child),'wall_seconds':time.monotonic()-begun,
            'contract':'Actual final uint16 baseline; causal word expert/global-prior log-odds contrasts; each model and final selection quantized; all post-marker bits scored; not native archive or global word tilt',
            'neural_training':False,'paid_rental_usd':0,'deletions':[]}


def tests():
    d={bytes([128]):b'page',bytes([129]):b'title',bytes([240,128]):b'pear',bytes([240,208,128]):b'fruit'}
    words=Words(list(d),list(d.values()));t=Tree(d,words)
    for w in [2,3,2,3,0,1]*10:t.observe_word(w);words.update(w)
    for w,path in enumerate(t.paths):
        product=np.ones(len(words.family_names))
        for node,nxt in zip(path,path[1:]):
            p,valid=t.probabilities(node,words);assert valid
            product*=p if t.child[node][1]==nxt else 1-p
        assert np.allclose(product,words.predictions(w),atol=1e-12,rtol=0),('Tree mass mismatch',w)
    raw=literal_wrt(SEP,d)+b' '+bytes([240,128])+b' '+bytes([12,255])+bytes([240,208])
    p0=np.full(len(raw)*8,32768,np.uint16);r=screen(raw,p0,d,strengths=(0.,))
    assert r['prequential_quantized_saving_bytes']==0.
    offset=r['unscored_prefix_bytes'];assert r['selected_probability_trace_sha256']==hashlib.sha256(p0[8*offset:].astype('<u2').tobytes()).hexdigest()
    print(json.dumps({'self_tests':'PASS','tree_word_mass_equivalence':True,'integer_identity':True,'literal_escape_and_partial_EOF_all_bits':True}),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--local-pilot',action='store_true');args=ap.parse_args();tests()
    if args.self_test:raise SystemExit(0)
    root=project_root(__file__) if args.local_pilot else pathlib.Path('/kaggle/working/hp_round7')
    dest=project_path('bit_placement_residual_pilot_v1', base=root);dest.mkdir(exist_ok=False)
    gate=json.loads((project_path('research_round7_lex_finalbit_trace_v2_results.json', base=root) if args.local_pilot else project_path('lex_finalbit_trace_v2/results.json', base=root)).read_text());assert gate['status']=='PASS'
    dp=project_path('research_round7_wrt_dictionary.bin', base=root) if args.local_pilot else project_path('preserved/gen/.dict', base=root)
    assert hashlib.sha256(dp.read_bytes()).hexdigest()=='4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a'
    dictionary=load_dictionary(dp)
    rows=[]
    for n in 'ab':
        inp=project_path('research_round7_lex_finalbit_'+n+'32k.bin', base=root) if args.local_pilot else project_path('lex_finalbit_trace_v2', base=root)/(n+'32k.bin')
        trace=project_path('research_round7_lex_finalbit_'+n+'32k_p.u16', base=root) if args.local_pilot else project_path('lex_finalbit_trace_v2', base=root)/(n+'_trace')/'final_p.u16'
        control=next(v for v in gate['controls'] if v['slice']==n)
        assert hashlib.sha256(inp.read_bytes()).hexdigest()==control['input_sha256']
        assert hashlib.sha256(trace.read_bytes()).hexdigest()==control['bit_trace_sha256']
        result=screen(inp.read_bytes(),np.fromfile(trace,'<u2'),dictionary)
        result.update(input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),baseline_trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
        (dest/(n+'.json')).write_text(json.dumps(result,indent=2));rows.append({'slice':n,'saving_bytes':result['prequential_quantized_saving_bytes'],'wall_seconds':result['wall_seconds']})
        (dest/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[-1]),flush=True)
    print('BIT_PLACEMENT_RESIDUAL_PILOT_COMPLETE',flush=True)
