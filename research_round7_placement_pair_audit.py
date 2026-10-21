"""Observational direction/lag counts for the user's examples and common words.

Whole-slice frequencies are diagnostics ONLY, never causal selector features.
Counts do not measure residual compression. A punctuation segment is a raw
literal boundary heuristic, not a linguistic sentence parser.
"""
import argparse,collections,hashlib,json,pathlib,time
import numpy as np
from research_round7_wrt import inverse_byte,load_dictionary
from research_round7_field_screen import literal_wrt,SEP

OUT=pathlib.Path('/kaggle/working/hp_round7')
DEST=OUT/'placement_pair_audit_v1'
LAGS=(1,2,3,4,5,6,7,8,16,32,64)
LABELS=(b'no',b'now',b'know',b'diamond',b'the',b'of',b'and',b'is',b'was',b'with',b'to',b'in')


def audit(raw,cost,dictionary):
    started=time.monotonic();codes=list(dictionary);spellings=list(dictionary.values());ids={c:i for i,c in enumerate(codes)}
    names={i:w.decode() for i,w in enumerate(spellings) if w in LABELS}
    targets=set(names);sep=literal_wrt(SEP,dictionary);markers=set();p=raw.find(sep)
    while p>=0:markers.add(p+len(sep));p=raw.find(sep,p+1)
    if not markers:raise ValueError('No article synchronization marker')
    i=min(markers);prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)];previous=[collections.deque(maxlen=64),collections.deque(maxlen=64)]
    exposures=collections.Counter();pairs=collections.Counter();pairbits=collections.Counter();words=collections.Counter();bits=collections.Counter();total=0
    while i<len(raw):
        lo=i
        if lo in markers:
            for q in previous:q.clear()
        c=inverse_byte(raw[i]);i+=1;w=None
        if c==12:
            if i<len(raw):i+=1
        elif c>=128:
            code=[c]
            if c>207:
                if i==len(raw):break
                c2=inverse_byte(raw[i]);i+=1;code.append(c2)
                if c2>207:
                    if i==len(raw):break
                    code.append(inverse_byte(raw[i]));i+=1
            w=ids[bytes(code)]
        else:
            if c in (46,33,63,10):previous[1].clear()
        if w is None:continue
        total+=1
        if w in targets:
            words[w]+=1;bits[w]+=float(prefix[i]-prefix[lo])
        for mode,q in enumerate(previous):
            for d in LAGS:
                if len(q)<d:continue
                u=q[-d]
                if u in targets:
                    exposures[mode,u,d]+=1
                    if w in targets:
                        pairs[mode,u,w,d]+=1;pairbits[mode,u,w,d]+=float(prefix[i]-prefix[lo])
            q.append(w)
    records=[]
    for (mode,u,v,d),count in sorted(pairs.items()):
        exposure=exposures[mode,u,d];pglobal=words[v]/total
        records.append({'scope':'article' if mode==0 else 'raw_punctuation_segment','source':names[u],
                        'target':names[v],'lag_DICT_events':d,'pair_count':count,'source_exposures':exposure,
                        'empirical_conditional_probability':count/exposure,
                        'unconditioned_global_target_probability':pglobal,
                        'unconditioned_frequency_lift':(count/exposure)/pglobal,
                        'actual_native_target_code_bits_sum':pairbits[mode,u,v,d]})
    return {'complete_DICT_atoms':total,'word_stats':{names[w]:{'count':words[w],'native_complete_code_bits':bits[w]} for w in names},
            'records':records,'missing_dictionary_examples':[w.decode() for w in LABELS if w not in spellings],
            'wall_seconds':time.monotonic()-started,
            'interpretation':'Descriptive whole-slice frequencies; lifts not conditioned on baseline/syntax/topic, not predictive bits saved; no future-derived table used by codec',
            'neural_training':False,'paid_rental_usd':0,'deletions':[]}


def tests():
    words=[b'page',b'title',b'now',b'the',b'know'];d={bytes([128+i]):w for i,w in enumerate(words)}
    raw=literal_wrt(SEP,d)+literal_wrt(b'now the know. now the know',d)
    r=audit(raw,np.full(len(raw),8.,np.float32),d)
    rows=[v for v in r['records'] if v['source']=='now' and v['target']=='know' and v['lag_DICT_events']==2]
    assert len(rows)==2 and all(v['pair_count']==2 for v in rows)
    backwards=[v for v in r['records'] if v['source']=='know' and v['target']=='now' and v['lag_DICT_events']==1]
    assert len(backwards)==1 and backwards[0]['scope']=='article' and backwards[0]['pair_count']==1
    assert r['complete_DICT_atoms']==6
    print(json.dumps({'placement_pair_parser_tests':'PASS','direction_and_gap_counts':True,'punctuation_boundary_control':True}),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args();tests()
    if args.self_test:raise SystemExit(0)
    DEST.mkdir(exist_ok=False);dp=OUT/'preserved/gen/.dict';dictionary=load_dictionary(dp);summary=[]
    for n in 'abcd':
        p=OUT/'preserved/slices'/(n+'2m.bin') if n in 'ab' else OUT/(n+'2m.bin');cp=OUT/'lex_native_2m'/(n+'_cost.f32')
        raw=p.read_bytes();cost=np.fromfile(cp,'<f4');assert len(raw)==len(cost)==2000000
        result=audit(raw,cost,dictionary);result.update(slice=n,input_sha256=hashlib.sha256(raw).hexdigest(),cost_sha256=hashlib.sha256(cp.read_bytes()).hexdigest())
        (DEST/(n+'.json')).write_text(json.dumps(result,indent=2));summary.append({'slice':n,'dictionary_atoms':result['complete_DICT_atoms'],'wall_seconds':result['wall_seconds'],'word_stats':result['word_stats']})
        (DEST/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary[-1]),flush=True)
    print('PLACEMENT_PAIR_AUDIT_COMPLETE',flush=True)
