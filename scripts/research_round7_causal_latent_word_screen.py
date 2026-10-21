"""Full-support causal latent word counts; no stored topic tables or neural SGD.

Every word/literal/case/escape choice is charged by the existing root scorer.
Topics and document posteriors learn only from completed decoded dictionary
atoms. Responsibilities are quantized to integers summing to4096.
"""
import pathlib,json,hashlib,types,collections,numpy as np
import research_round7_word_association_root_screen as root
from research_round7_wrt import load_dictionary

SCALE=4096
STOP=set(b'page title text the and of in to a is for on with as by an be are was from at it this that which not or has have his her its also'.split())
class EmptyGraph:
    def memory(self):return {'rows':0,'edges':0}
class Topic:
    def __init__(self,words,rank,k,decay_den):
        self.k=k;self.decay_den=decay_den;self.rank=rank;self.eta=1/16;self.kappa=64
        h=np.empty((len(words),k),np.int64)
        for w,word in enumerate(words):
            for z in range(k):
                b=hashlib.blake2s(word+z.to_bytes(2,'little'),digest_size=1).digest()[0]
                h[w,z]=256 if word in STOP else 128+b
        self.h=h;self.initial=np.sum(rank[:,None]*h,axis=0)
        self.c=np.zeros_like(h);self.total=np.zeros(k,np.int64);self.global_h=np.zeros(k,np.int64)
        self.doc=np.zeros(k,np.int64)
    def reset(self):self.doc[:]=0
    def components(self,w,global_count):
        numerator=self.c[w]+SCALE*self.eta*(global_count+self.kappa*self.rank[w])*self.h[w]
        denominator=self.total+SCALE*self.eta*(self.global_h+self.kappa*self.initial)
        theta=numerator/denominator
        phi=(self.doc+SCALE*.25)/(self.doc.sum()+self.k*SCALE*.25)
        return phi*theta
    def update(self,w,global_count,doc_weight):
        r=self.components(w,global_count);r=r/r.sum()
        scaled=r*SCALE;integer=np.floor(scaled).astype(np.int64)
        remainder=SCALE-int(integer.sum());order=np.argsort(-(scaled-integer),kind='stable')
        integer[order[:remainder]]+=1;assert integer.sum()==SCALE
        self.c[w]+=integer;self.total+=integer;self.global_h+=self.h[w]
        if self.decay_den:self.doc=self.doc*(self.decay_den-1)//self.decay_den
        self.doc+=integer*doc_weight
class CausalLatentWords:
    def __init__(self,codes,spellings):
        self.words=spellings;self.rank=1/(np.arange(len(codes),dtype=np.float64)+16)
        self.rank/=self.rank.sum();self.global_counts=np.ones(len(codes),np.int64);self.global_total=len(codes)
        self.family_names=['rank_prior','global_rank64','topic8_article','topic8_ttl128','topic16_article','topic16_ttl256']
        self.topics=[Topic(spellings,self.rank,8,0),Topic(spellings,self.rank,8,128),Topic(spellings,self.rank,16,0),Topic(spellings,self.rank,16,256)]
        self.follows=EmptyGraph();self.assoc=EmptyGraph();self.in_title=False;self.reset()
    def reset(self):
        self.article=types.SimpleNamespace(counts=collections.Counter());self.article_events=0;self.in_title=True
        for topic in self.topics:topic.reset()
    def predictions(self,w,conditional=False):
        assert not conditional,'Root prediction before first byte only'
        g=int(self.global_counts[w]-1);total=self.global_total-len(self.words)
        values=[self.rank[w],(g+64*self.rank[w])/(total+64)]
        values.extend(float(topic.components(w,g).sum()) for topic in self.topics)
        p=np.asarray(values,np.float64);assert np.all(p>=0) and np.all(p<=1+1e-12)
        return p
    def update(self,w):
        g=int(self.global_counts[w]-1);weight=0 if self.words[w] in STOP else 3 if self.in_title else 1
        for topic in self.topics:topic.update(w,g,weight)
        self.global_counts[w]+=1;self.global_total+=1;self.article.counts[w]+=1;self.article_events+=1
    def memory_bytes(self):
        return self.rank.nbytes+self.global_counts.nbytes+sum(t.h.nbytes+t.initial.nbytes+t.c.nbytes+t.total.nbytes+t.global_h.nbytes+t.doc.nbytes for t in self.topics)
def tests():
    codes=[bytes([128+i]) for i in range(6)];m=CausalLatentWords(codes,[b'apple',b'pear',b'fruit',b'king',b'crown',b'queen'])
    maximum=0.
    for j in range(160):
        if j%16==0:m.reset()
        p=sum(m.predictions(w) for w in range(6));maximum=max(maximum,float(np.max(np.abs(p-1))))
        assert np.allclose(p,1,atol=1e-12,rtol=0),'Latent distributions not normalized'
        m.update([0,2,1,2,4,3,5,3][j%8])
        for t in m.topics:
            assert np.array_equal(t.c.sum(axis=0),t.total),'Integer topic mass accounting'
    root.Words=CausalLatentWords;root.self_test()
    print(json.dumps({'causal_latent_normalization_max_error':maximum,'responsibility_mass':SCALE,'root_literal_case_escape_accounting':'passed'}),flush=True)
if __name__=='__main__':
    tests();out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'causal_latent_words';dest.mkdir(exist_ok=False)
    dictionary=load_dictionary(out/'preserved/gen/.dict');rows=[]
    for n in 'bcad':
        inp=out/'preserved/slices'/(n+'2m.bin') if n in 'ab' else out/(n+'2m.bin')
        raw=inp.read_bytes();cost=np.fromfile(out/'lex_native_2m'/(n+'_cost.f32'),'<f4');assert len(raw)==len(cost)==2000000
        root.Words=CausalLatentWords;r=root.screen(raw,cost,dictionary)
        r['contract'].update(families='rank prior, prefix global counts,8/16 latent topics with article or128/256-token posterior TTL',
            latent_learning='Completed prefix dictionary atoms only; integer4096 responsibility mass; no neural SGD or offline topic tables',
            all_root_choices_charged=True,baseline='Actual lexical checkpoint native final-coder cold2M cost trace',
            memory='Full-support word/topic counter arrays, derived hashes/rank priors; production subtree aggregates/code/runtime unmeasured')
        prototype=CausalLatentWords(list(dictionary),list(dictionary.values()));r['prototype_array_bytes']=prototype.memory_bytes();del prototype
        (dest/(n+'.json')).write_text(json.dumps(r,indent=2));rows.append({'slice':n,'saving_bytes_before_native_code_cost':r['score']['prequential_saving_bytes'],'wall_seconds':r['wall_seconds']})
        (dest/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[-1]),flush=True)
    print('CAUSAL_LATENT_WORDS_COMPLETE',flush=True)
