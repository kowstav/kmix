"""Causal new-mention variants of the word-association root predictor.

Exclude already decoded article atoms from a candidate DISTRIBUTION; never
activate using whether the unknown target is new. Repeated targets therefore
receive zero specialist mass and pay the neutral fallback. Both outcomes count.
"""
import argparse,json
from pathlib import Path
import numpy as np
import research_round7_word_association_root_screen as root
from research_round7_word_association_screen import Words
from research_round7_wrt import load_dictionary

class NewMentionWords(Words):
    def __init__(self,codes,spellings):
        super().__init__(codes,spellings)
        self.family_names+=['newglobal','newprev8','newprev128','newassoc4_8','newassoc4_128','newassoc16_8','newassoc16_128','newtitle8','newtitle128']
        self.unseen_total=self.global_total
    def reset(self):super().reset();self.unseen_total=self.global_total
    def update(self,w):
        if w not in self.article.counts:self.unseen_total-=self.global_counts[w]
        super().update(w)
    def predictions(self,w,conditional=False):
        if conditional:raise ValueError('This family is only defined for root predictions')
        original=super().predictions(w,conditional=False)
        if self.unseen_total<=0:return np.r_[original,np.full(9,self.global_counts[w]/self.global_total)]
        prior=self.global_counts[w]/self.unseen_total if w not in self.article.counts else 0.
        values=[prior];cache={}
        def part(s,kappa,graph):
            key=(id(graph),s)
            if key not in cache:
                row=graph.row(s)
                if row is None:cache[key]=(0.,0.)
                else:
                    total=sum(v for k,v in row.counts.items() if k not in self.article.counts)
                    weight=row.counts.get(w,0) if w not in self.article.counts else 0
                    cache[key]=(weight,total)
            weight,total=cache[key]
            return (weight+kappa*prior)/(total+kappa)
        for k in (8,128):values.append(part(self.prev,k,self.follows))
        for sources in (list(self.recent)[-4:],list(self.recent),self.title[:8]):
            sources=list(dict.fromkeys(sources))
            for k in (8,128):values.append(sum(part(s,k,self.assoc) for s in sources)/len(sources) if sources else prior)
        p=np.r_[original,values]
        if np.any(p<0) or np.any(p>1+1e-12):raise RuntimeError('Invalid new-mention mass')
        return p

def self_test():
    codes=[bytes([128+i]) for i in range(6)];m=NewMentionWords(codes,[b'apple',b'fruit',b'pear',b'queen',b'king',b'crown'])
    for w in [0,2,1,2,3,5,4,5]*20:m.update(w)
    m.reset();m.update(0);m.update(3)
    total=sum(m.predictions(w) for w in range(6))
    if not np.allclose(total,1.,rtol=0.,atol=1e-12):raise AssertionError('New-mention normalization')
    for w in (0,3):
        if np.any(m.predictions(w)[12:]):raise AssertionError('Article repeats must pay fallback')
    direct=sum(m.global_counts[w] for w in range(6) if w not in m.article.counts)
    if m.unseen_total!=direct:raise AssertionError('Unseen count accounting')
    for w in range(6):m.update(w)
    if not np.allclose(sum(m.predictions(w) for w in range(6)),1.,rtol=0.,atol=1e-12):raise AssertionError('Exhausted support fallback')
    root.Words=NewMentionWords;root.self_test()
    print(json.dumps({'new_mention_self_test':'passed','families':len(m.family_names),'normalization_max_error':float(np.max(np.abs(total-1.)))}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--raw');ap.add_argument('--cost');ap.add_argument('--dictionary');ap.add_argument('--out');a=ap.parse_args()
    if a.self_test:self_test()
    else:
        raw=Path(a.raw).read_bytes();cost=np.fromfile(a.cost,'<f4')
        if len(raw)!=len(cost):raise ValueError('Incomplete cost')
        root.Words=NewMentionWords;d=root.screen(raw,cost,load_dictionary(a.dictionary));d['contract']['newmention']='candidate masking by decoded article atoms; repeated targets pay fallback; no target-class activation';Path(a.out).write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d['score'].items() if k!='fixed_models'}))
