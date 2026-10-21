"""Full ASCII-word lag diagnostic, including literal single-letter I/i.

DICT-event lags omit literal words. This separate diagnostic uses the checked
WRT inverse and observes case-folded ASCII words including markup, not a full
linguistic sentence model. Whole-slice counts never guide the codec.
"""
import collections,json,pathlib,re,time
import numpy as np
from research_round7_wrt import load_dictionary,decode_wrt,encoded_span
from research_round7_field_screen import literal_wrt,SEP

OUT=pathlib.Path('/kaggle/working/hp_round7');DEST=OUT/'ascii_placement_audit_v1'
LAGS=(1,2,3,4,5,6,7,8,16,32,64)
LABELS={b'no',b'now',b'know',b'diamond',b'the',b'of',b'and',b'is',b'was',b'with',b'to',b'in',b'i'}


def audit(raw,cost,dictionary):
    begun=time.monotonic();sep=literal_wrt(SEP,dictionary);first=raw.find(sep)
    assert first>=0;offset=first+len(sep)
    decoded,starts,ends,_=decode_wrt(raw[offset:],dictionary)
    boundaries=[m.end() for m in re.finditer(re.escape(SEP),decoded)]
    pointer=0;queue=[collections.deque(maxlen=64),collections.deque(maxlen=64)]
    counts=collections.Counter();pairs=collections.Counter();totals=collections.Counter();exposure=collections.Counter()
    prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)];last=0;n=0
    for m in re.finditer(rb'[A-Za-z]+',decoded):
        while pointer<len(boundaries) and boundaries[pointer]<=m.start():
            for q in queue:q.clear()
            pointer+=1
        if any(c in decoded[last:m.start()] for c in (b'.',b'!',b'?',b'\n')):queue[1].clear()
        w=m.group().lower();n+=1
        if w in LABELS:
            lo,hi=encoded_span(starts,ends,m.start(),m.end());counts[w]+=1;totals[w]+=float(prefix[offset+hi]-prefix[offset+lo])
        for mode,q in enumerate(queue):
            for d in LAGS:
                if len(q)<d:continue
                u=q[-d]
                if u in LABELS:
                    exposure[mode,u,d]+=1
                    if w in LABELS:pairs[mode,u,w,d]+=1
            q.append(w)
        last=m.end()
    return {'ascii_word_events':n,'word_stats':{w.decode():{'count':counts[w],'native_complete_span_bits':totals[w]} for w in sorted(LABELS)},
            'example_pairs':[{'scope':'article' if mode==0 else 'raw_punctuation_segment','source':u.decode(),'target':v.decode(),
                               'lag_ASCII_words':d,'pair_count':count,'source_exposures':exposure[mode,u,d]}
                              for (mode,u,v,d),count in sorted(pairs.items()) if u in [b'now',b'know',b'no'] and v in [b'now',b'know',b'no',b'i'] and u!=v],
            'wall_seconds':time.monotonic()-begun,
            'interpretation':'Full ASCII words including literal i and markup; observational counts, not a codec or a claim about grammatical sentences',
            'neural_training':False,'paid_rental_usd':0,'deletions':[]}


if __name__=='__main__':
    d={bytes([128]):b'page',bytes([129]):b'title',bytes([130]):b'now',bytes([131]):b'know'}
    raw=literal_wrt(SEP,d)+literal_wrt(b'now i know. i know now',d)
    t=audit(raw,np.full(len(raw),8.,np.float32),d)
    assert t['ascii_word_events']==6 and t['word_stats']['i']['count']==2
    assert any(v['source']=='now' and v['target']=='know' and v['lag_ASCII_words']==2 and v['pair_count']==1 for v in t['example_pairs'])
    print(json.dumps({'full_ASCII_word_lag_fixture':'PASS','literal_i_counted':True}),flush=True)
    DEST.mkdir(exist_ok=False);dp=OUT/'preserved/gen/.dict';dictionary=load_dictionary(dp);rows=[]
    for n in 'abcd':
        p=OUT/'preserved/slices'/(n+'2m.bin') if n in 'ab' else OUT/(n+'2m.bin');cp=OUT/'lex_native_2m'/(n+'_cost.f32')
        raw=p.read_bytes();cost=np.fromfile(cp,'<f4');assert len(raw)==len(cost)==2000000
        r=audit(raw,cost,dictionary);r['slice']=n;(DEST/(n+'.json')).write_text(json.dumps(r,indent=2));rows.append(r)
        (DEST/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'slice':n,'ascii_words':r['ascii_word_events'],'wall_seconds':r['wall_seconds']}),flush=True)
    print('ASCII_PLACEMENT_AUDIT_COMPLETE',flush=True)
