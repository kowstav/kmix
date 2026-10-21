"""Diagnose actual lexth11c native final-coder costs, including spelling relations.

Observed outcomes may define diagnostic buckets; they are never free predictor
inputs. All recurrence/related-word sources precede the diagnosed occurrence.
No neural probabilities, new compression savings or global first-use claims.
"""
import pathlib,json,re,hashlib,collections,numpy as np
from research_round7_wrt import load_dictionary,decode_wrt,encoded_span
from research_round7_field_screen import SEP,literal_wrt
out=pathlib.Path('/kaggle/working/hp_round7');pre=out/'preserved';dest=out/'lex_residual_atlas';dest.mkdir(exist_ok=False)
dictionary=load_dictionary(pre/'gen/.dict'); separator=literal_wrt(SEP,dictionary)
records={r['slice']:r for r in json.loads((out/'lex_native_2m/results.json').read_text())}
def relation_key(word,kind):
    if len(word)<4:return None
    if kind=='prefix4':return word[:4]
    if kind=='suffix4':return word[-4:]
    return ''.join(sorted(word)) if len(word)<=32 else None
def add_relation(table,key,word):
    if key is None:return
    # Two distinct words suffice to answer whether a distinct donor exists.
    row=table.setdefault(key,[])
    if word not in row and len(row)<2:row.append(word)
def related(table,key,word):return key is not None and any(w!=word for w in table.get(key,()))
for n in 'abcd':
    inp=pre/'slices'/(n+'2m.bin') if n in 'ab' else out/(n+'2m.bin')
    raw=inp.read_bytes();assert hashlib.sha256(raw).hexdigest()==records[n]['input_sha256']
    costs=np.fromfile(out/'lex_native_2m'/(n+'_cost.f32'),'<f4').astype(np.float64);assert costs.size==len(raw)==2000000
    offset=raw.find(separator);assert offset>=0
    text,starts,ends,_=decode_wrt(raw[offset:],dictionary)
    csum=np.r_[0.,np.cumsum(costs)];bounds=np.array([m.start()+len(SEP) for m in re.finditer(re.escape(SEP),text)])
    categories=collections.defaultdict(lambda:[0,0.]);stats={};expensive=[];seen=set();local={};current=-1
    relations={k:{} for k in ['prefix4','suffix4','anagram']};local_relations={k:{} for k in relations}
    assigned=np.zeros(len(raw),bool);word_total=0.;word_occurrences=0
    for m in re.finditer(rb'[A-Za-z]+',text):
        word=m.group().decode('ascii');key=word.lower();article=int(np.searchsorted(bounds,m.start(),side='right')-1)
        if article!=current:current=article;local={};local_relations={k:{} for k in relations}
        a,b=encoded_span(starts,ends,m.start(),m.end());a+=offset;b+=offset
        bits=float(csum[b]-csum[a]);assigned[a:b]=True;word_total+=bits;word_occurrences+=1
        group='first_in_diagnosed_slice' if key not in seen else 'known_in_slice_first_in_article' if key not in local else 'article_repeat'
        buckets=[group]
        if key in local:
            distance=a-local[key]
            buckets.append('article_repeat_'+('under_1024' if distance<1024 else '1024_to_4096' if distance<4096 else '4096_to_16384' if distance<16384 else 'over_16384'))
        coded=any(v>=128 for v in raw[a:b]);buckets.append('dictionary_word' if coded else 'literal_spelling_word')
        for kind in relations:
            rkey=relation_key(key,kind)
            if related(relations[kind],rkey,key):buckets.append('distinct_earlier_slice_word_'+kind)
            if related(local_relations[kind],rkey,key):buckets.append('distinct_earlier_article_word_'+kind)
        for bucket in buckets:categories[bucket][0]+=1;categories[bucket][1]+=bits
        row=stats.setdefault(key,[0,0.,0.]);row[0]+=1;row[1]+=bits;row[2]=max(row[2],bits)
        if bits>=24:expensive.append({'word':word,'encoded_start':a,'final_bits':bits,'recurrence':group,'context':text[max(0,m.start()-80):min(len(text),m.end()+80)].decode('utf-8','replace')})
        seen.add(key);local[key]=b
        for kind in relations:
            rkey=relation_key(key,kind);add_relation(relations[kind],rkey,key);add_relation(local_relations[kind],rkey,key)
    rows=[{'word':w,'occurrences':r[0],'final_bits':r[1],'bits_per_occurrence':r[1]/r[0],'max_occurrence_bits':r[2]} for w,r in stats.items()]
    result={'slice':n,'scope':'Actual lexth11c checkpoint/config, original FX2-ordered2M WRT slice, cold neural/classical histories; diagnostic only',
            'input_bytes':len(raw),'unscored_prefix_bytes':offset,'input_sha256':records[n]['input_sha256'],
            'baseline_ideal_bytes':float(costs.sum()/8),'ascii_word_occurrences':word_occurrences,'ascii_word_types':len(stats),
            'word_share_all_final_bits':word_total/csum[-1],'assigned_word_partition_error_bits':float(word_total-costs[assigned].sum()),
            'neural_costs_separately_available':False,
            'warning':'Categories overlap; XML tags count as ASCII words; first in slice is not globally new; spelling relation is not a free selector or predicted word',
            'categories':{k:{'occurrences':v[0],'final_bits':v[1],'share_all_final_bits':v[1]/csum[-1]} for k,v in categories.items()},
            'top_total_words':sorted(rows,key=lambda r:r['final_bits'],reverse=True)[:80],
            'hard_repeated_words':sorted((r for r in rows if r['occurrences']>=5),key=lambda r:r['bits_per_occurrence'],reverse=True)[:80],
            'top_occurrences':sorted(expensive,key=lambda r:r['final_bits'],reverse=True)[:80]}
    assert abs(result['assigned_word_partition_error_bits'])<1e-4,'Overlapping word attribution: inspect before acceptance'
    (dest/(n+'.json')).write_text(json.dumps(result,indent=2))
    print(json.dumps({'slice':n,'word_share_all_final_bits':result['word_share_all_final_bits'],'categories':result['categories'],'hard_words':[r['word'] for r in result['hard_repeated_words'][:12]]}),flush=True)
print('LEX_RESIDUAL_ATLAS_COMPLETE',flush=True)
