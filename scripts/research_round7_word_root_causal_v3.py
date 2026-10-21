"""Root version: predict a dictionary atom BEFORE observing its first byte.

Neutral fallback carries literal, syntax, case and escape events. Their loss is
charged. Activation contexts use only prior event category and article age;
unknown word, first byte, length and occurrence class never choose the context.
The dictionary's variable-length tree is prefix-free. Mixture ratios telescope
along the observed event; this is a likelihood screen, not native integration.
"""
import argparse,json,math,time,re,hashlib
from pathlib import Path
from collections import Counter
import numpy as np
from research_round7_word_association_screen import Words,Mixture,self_test as suffix_test
from research_round7_wrt import load_dictionary,inverse_byte
from research_round7_field_screen import literal_wrt,SEP,TEND

def screen(raw,cost,dictionary):
    started=time.monotonic();sep=literal_wrt(SEP,dictionary);tend=literal_wrt(TEND,dictionary);sync_start=raw.find(sep);offset=sync_start+len(sep) if sync_start>=0 else -1
    if offset<0:raise ValueError('No synchronization prefix')
    codes=list(dictionary);spellings=list(dictionary.values());ids={c:i for i,c in enumerate(codes)}
    words=Words(codes,spellings);mix=Mixture(words.family_names);prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)]
    markers=sorted([(m.start()+len(sep),'start') for m in re.finditer(re.escape(sep),raw)]+[(m.start()+len(tend),'end') for m in re.finditer(re.escape(tend),raw)])
    marker=0;i=offset;prev_kind=3;events=0;classes={};trace=hashlib.sha256();atoms=0
    while i<len(raw):
        lo=i
        # This runs BEFORE reading the current first byte, unlike the suffix
        # model. The available offset is the only way a marker can enter.
        while marker<len(markers) and markers[marker][0]<=lo:
            available,kind=markers[marker];assert available<=lo
            if kind=='start':words.reset()
            else:words.in_title=False
            marker+=1
        bucket=0 if words.article_events<16 else 1 if words.article_events<64 else 2 if words.article_events<256 else 3
        ctx=(prev_kind,bucket)  # Crucially excludes the upcoming code width.
        c=inverse_byte(raw[i]);i+=1;w=None
        if c==12:
            if i<len(raw):i+=1;cls='literal_escape'
            else:cls='partial_escape_EOF'
            probs=np.zeros(len(words.family_names))
        elif c>=128:
            code=[c];partial=False
            while code[-1]>207 and len(code)<3:
                if i>=len(raw):partial=True;break
                code.append(inverse_byte(raw[i]));i+=1
            code=bytes(code)
            if partial:
                matches=[j for j,p in enumerate(codes) if p.startswith(code)]
                probs=sum((words.predictions(j,conditional=False) for j in matches),np.zeros(len(words.family_names)))
                cls='partial_dictionary_EOF'
            else:
                if code not in ids:raise ValueError('Invalid code at '+str(lo))
                w=ids[code];probs=words.predictions(w,conditional=False)
                cls='first_in_slice' if words.global_counts[w]==1 else 'known_first_in_article' if w not in words.article.counts else 'article_repeat'
                atoms+=1
        else:probs=np.zeros(len(words.family_names));cls='literal_syntax_or_case'
        baseline=float(prefix[i]-prefix[lo]);before=mix.total_gain;mix.score(probs,baseline,ctx);gain=mix.total_gain-before
        r=classes.setdefault(cls,{'events':0,'baseline_bits':0.,'prequential_saving_bytes':0.});r['events']+=1;r['baseline_bits']+=baseline;r['prequential_saving_bytes']+=gain/8.
        trace.update(np.asarray([lo,ctx[0],ctx[1],*probs],dtype='<f8').tobytes())
        if w is not None:words.update(w);prev_kind=2
        else:prev_kind=0 if c in (32,9,10,13) else 1 if c in (7,64) else 4 if (65<=c<=90 or 97<=c<=122) else 3
        events+=1
        if events%200000==0:print(json.dumps({'events':events,'position':i,'saving_bytes':mix.total_gain/8.,'elapsed_seconds':time.monotonic()-started}),flush=True)
    return {'raw_bytes':len(raw),'baseline_ideal_bytes':float(prefix[-1]/8.),'unscored_prefix_bytes':offset,'dictionary_atoms':atoms,'contract':{'activation':'prefix-only previous event category and article age, BEFORE first byte','sources':'completed dictionary atoms and prefix-recognized markers','coverage':'root dictionary choice plus charged literal/syntax/case/escape fallback','normalization':'prefix-free word tree; uniform/global/causal count distributions normalize; neutral carries other outcomes','measurement':'ideal final-coder likelihood only; code/runtime/RSS/full-history not priced','neural_retraining':False,'EOF':'partial prefixes are scored by summed prefix mass; partial escapes pay fallback'},'by_occurrence_class':classes,'score':mix.result(),'memory':{'followers':words.follows.memory(),'associations':words.assoc.memory(),'rows_max_per_graph':4096,'edges_max_per_graph':4096*64},'probability_trace_sha256':trace.hexdigest(),'wall_seconds':time.monotonic()-started}

def self_test():
    suffix_test();codes=[bytes([128]),bytes([208,128]),bytes([240,128]),bytes([240,208,128])]
    model=Words(codes,[b'alpha',b'pear',b'fruit',b'queen']);model.reset()
    for w in [0,1,2,3]*15:model.update(w)
    total=sum(model.predictions(w,conditional=False) for w in range(len(codes)))
    if not np.allclose(total,1.,rtol=0.,atol=1e-12):raise AssertionError('Root normalization')
    fixture={bytes([128]):b'page',bytes([129]):b'title',bytes([240,128]):b'pear',bytes([240,208,128]):b'fruit'}
    raw=literal_wrt(SEP,fixture)+b' '+(bytes([240,128])+b' '+bytes([240,208,128])+b' ')*10+literal_wrt(TEND,fixture)
    result=screen(raw,np.full(len(raw),8.,np.float32),fixture)
    if result['score']['baseline_suffix_bits']!=(len(raw)-len(literal_wrt(SEP,fixture)))*8:raise AssertionError('Complete post-sync fixture byte accounting')
    sep=literal_wrt(SEP,fixture)
    for suffix in [bytes([240]),bytes([240,208]),bytes([12]),bytes([240,128]),bytes([240,208,128])]:
        fragment=sep+suffix
        got=screen(fragment,np.full(len(fragment),8.,np.float32),fixture)
        assert got['score']['baseline_suffix_bits']==len(suffix)*8,('EOF accounting',suffix)
    print(json.dumps({'root_self_test':'passed','root_normalization_max_error':float(np.max(np.abs(total-1.))),'fixture_events':result['score']['events']}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--raw');ap.add_argument('--cost');ap.add_argument('--dictionary');ap.add_argument('--out');args=ap.parse_args()
    if args.self_test:self_test()
    else:
        raw=Path(args.raw).read_bytes();cost=np.fromfile(args.cost,'<f4')
        if len(raw)!=len(cost):raise ValueError('Cost length mismatch')
        d=screen(raw,cost,load_dictionary(args.dictionary));Path(args.out).write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d['score'].items() if k!='fixed_models'}))
