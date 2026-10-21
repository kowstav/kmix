"""Residual budgets by word recurrence and prefix-available context.

This attributes observed costs; its target word is NOT a predictor input.
Word classifications describe diagnosed spans, not free decoder side channels.
"""
import json,re,argparse,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from research_round7_wrt import decode_wrt,load_dictionary
from research_round7_field_screen import SEP,literal_wrt


def inspect(name,out):
    raw=Path(f'/root/hp/slices/{name}2m.bin').read_bytes()
    cost_path=f'/root/hp/runs/lex_{name}/cost.f32' if name in ['a','b'] else str(out/f'baseline_{name}/cost.f32')
    cost=np.fromfile(cost_path,'<f4')
    if len(cost)!=len(raw):raise ValueError('Cost dump incomplete')
    dictionary=load_dictionary('/root/hp/gen/.dict')
    offset=raw.find(literal_wrt(SEP,dictionary))
    if offset<0:raise ValueError('No article sync')
    text,starts,ends,_=decode_wrt(raw[offset:],dictionary)
    prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)]
    boundaries=np.asarray([m.start()+len(SEP) for m in re.finditer(re.escape(SEP),text)],np.int64)
    articles={};global_seen={};article_seen={};by=defaultdict(lambda:[0,0.,0])
    total=0.;assigned=np.zeros(len(raw),np.bool_);previous='';pairs=defaultdict(Counter)
    current=-1
    def add(category,bits,n):
        row=by[category];row[0]+=1;row[1]+=bits;row[2]+=n
    for match in re.finditer(rb'[A-Za-z]+',text):
        article=int(np.searchsorted(boundaries,match.start(),side='right')-1)
        if article!=current:article_seen={};current=article;previous=''
        word=match.group().decode('ascii').lower()
        lo=offset+int(starts[match.start()]);hi=offset+int(ends[match.end()-1])
        bits=float(prefix[hi]-prefix[lo]);n=hi-lo;total+=bits;assigned[lo:hi]=True
        if word not in global_seen:
            cls='first_in_decoded_prefix'
        elif word not in article_seen:
            cls='known_word_first_in_current_article'
        else:
            distance=lo-article_seen[word]
            cls='article_repeat_'+('under_1024' if distance<1024 else '1024_to_4096' if distance<4096 else '4096_to_16384' if distance<16384 else 'over_16384')
        add(cls,bits,n)
        if bits>=16:add('hard_word_'+cls,bits,n)
        if previous:
            followers=pairs[previous]
            if word in followers:
                top=followers.most_common(5)
                rank='top1' if top[0][0]==word else 'top5' if any(w==word for w,c in top) else 'outside_top5'
                add('seen_after_previous_word_'+rank,bits,n)
            else:add('unseen_after_previous_word',bits,n)
            followers[word]+=1
        previous=word;global_seen[word]=hi;article_seen[word]=hi
    result={'slice':name,'raw_bytes':len(raw),'unscored_prefix_bytes':offset,
        'baseline_ideal_bytes':float(prefix[-1]/8.),'word_bits':total,
        'word_share_baseline':total/prefix[-1],
        'assigned_word_bits_check':float(total-cost[assigned].astype(np.float64).sum()),
        'distinct_words_in_slice':len(global_seen),'article_count':len(boundaries),
        'contract':'cold history at slice start; observed span attribution only; categories overlap; no oracle savings claimed',
        'categories':{k:{'occurrences':r[0],'final_bits':r[1],'encoded_bytes':r[2],
                         'share_total_bits':r[1]/prefix[-1],'bits_per_occurrence':r[1]/r[0]}
                      for k,r in by.items()}}
    (out/(name+'_word_context_atlas.json')).write_text(json.dumps(result,indent=2))
    print(json.dumps(result),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--slice',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    inspect(args.slice,Path(args.out))
