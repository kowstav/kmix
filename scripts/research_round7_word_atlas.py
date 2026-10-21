"""Attribute existing FINAL coder and neural probabilities to actual WRT words.
Run on Kaggle: python research_round7_word_atlas.py --out /kaggle/working/hp_round7
"""
import argparse, json, re, math, pathlib, time, csv
import numpy as np
from research_round7_wrt import load_dictionary,decode_wrt,encoded_span

def inspect_slice(name,raw_path,cost_path,prob_path,dictionary,out):
    raw=pathlib.Path(raw_path).read_bytes()
    costs=np.fromfile(cost_path,dtype=np.float32).astype(np.float64)
    if len(costs)!=len(raw): raise ValueError('Cost/byte alignment failure')
    skip=raw[:1]==b'\x07' and raw[5:6]==b'\x07'
    text,starts,ends,header=decode_wrt(raw,dictionary,skip_header=skip)
    if skip:
        with open('/root/hp/gen/.ready4cmix','rb') as f: expected=f.read(len(text))
        if text!=expected: raise ValueError('Inverse-WRT differs from reference preprocessing')
    cumulative=np.r_[0.,np.cumsum(costs,dtype=np.float64)]
    nb=np.zeros(len(raw),np.float64)
    if pathlib.Path(prob_path).exists():
        probs=np.memmap(prob_path,dtype=np.float16,mode='r',shape=(len(raw),205))
        vocab=np.fromfile('/root/hp/data/vocab.list',dtype=np.uint8)
        inverse=np.full(256,-1,np.int64); inverse[vocab]=np.arange(205)
        for a in range(1,len(raw),32768):
            b=min(len(raw),a+32768)
            # Row k predicts byte k+1; enforce the C++ reader's probability floor.
            p=np.maximum(np.asarray(probs[a-1:b-1],np.float64),1e-6)
            actual=p[np.arange(b-a),inverse[np.frombuffer(raw[a:b],np.uint8)]]
            nb[a:b]=-np.log2(actual/p.sum(axis=1))
    nc=np.r_[0.,np.cumsum(nb,dtype=np.float64)]
    stats={}; occurrences=[]; word_bits=0.; dictionary_bits=0.; assigned=np.zeros(len(raw),np.bool_)
    categories={}
    for match in re.finditer(rb'[A-Za-z]+',text):
        word=match.group().decode('ascii')
        a,b=encoded_span(starts,ends,match.start(),match.end())
        bits=float(cumulative[b]-cumulative[a]); nbits=float(nc[b]-nc[a])
        key=word.lower()
        r=stats.setdefault(key,[0,0.,0.,0.,0,0])
        r[0]+=1; r[1]+=bits; r[2]+=nbits; r[3]=max(r[3],bits)
        coded=any(c>=128 for c in raw[a:b]); r[4]+=coded; r[5]+=b-a
        word_bits+=bits; assigned[a:b]=True
        if coded: dictionary_bits+=bits
        if bits>=24:
            occurrences.append({'word':word,'encoded_start':a,'encoded_end':b,'final_bits':bits,'neural_bits':nbits,'context':text[max(0,match.start()-100):min(len(text),match.end()+100)].decode('utf-8','replace')})
        category='allcaps' if word.isupper() and len(word)>1 else 'capitalized' if word[:1].isupper() else 'lowercase'
        rcat=categories.setdefault(category,[0,0.,0.]); rcat[0]+=1; rcat[1]+=bits; rcat[2]+=nbits
    rows=[{'word':w,'occurrences':r[0],'final_bits':r[1],'neural_bits':r[2],'bits_per_occurrence':r[1]/r[0],'max_occurrence_bits':r[3],'dictionary_occurrences':r[4],'encoded_bytes':r[5]} for w,r in stats.items()]
    by_total=sorted(rows,key=lambda r:r['final_bits'],reverse=True)
    repeated=sorted((r for r in rows if r['occurrences']>=5),key=lambda r:r['bits_per_occurrence'],reverse=True)
    occurrences.sort(key=lambda r:r['final_bits'],reverse=True)
    summary={'slice':name,'encoded_bytes':len(raw),'decoded_bytes':len(text),'reference_prefix_verified':skip,'final_coder_bytes':float(costs.sum()/8),'neural_bits_per_byte':float(nb[1:].mean()),'ascii_word_occurrences':sum(r['occurrences'] for r in rows),'ascii_word_types':len(rows),'word_final_bytes':word_bits/8,'word_share_final_bits':word_bits/costs.sum(),'dictionary_word_final_bytes':dictionary_bits/8,'word_cost_partition_error_bits':float(word_bits-costs[assigned].sum()),'categories':categories,'top_total_bits':by_total[:100],'repeated_hard_words':repeated[:100],'top_occurrences':occurrences[:100]}
    (out/(name+'_word_atlas.json')).write_text(json.dumps(summary,indent=2))
    with (out/(name+'_words.csv')).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(by_total)
    (out/(name+'_decoded_preview.txt')).write_text(text[:10000].decode('utf-8','replace'))
    print(json.dumps({'slice':name,**{k:summary[k] for k in ['encoded_bytes','decoded_bytes','reference_prefix_verified','final_coder_bytes','neural_bits_per_byte','ascii_word_occurrences','ascii_word_types','word_share_final_bits','word_cost_partition_error_bits']},'top_words':[r['word'] for r in by_total[:15]],'hard_repeated_words':[r['word'] for r in repeated[:15]]}),flush=True)
    return summary

def main():
    p=argparse.ArgumentParser(); p.add_argument('--out',required=True); args=p.parse_args()
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    dictionary=load_dictionary('/root/hp/dic/dic.txt')
    for name in ['a','b']:
        inspect_slice(name,f'/root/hp/slices/{name}2m.bin',f'/root/hp/runs/lex_{name}/cost.f32',f'/root/hp/slices/{name}2m.probs.f16',dictionary,out)
    print('WORD_ATLAS_COMPLETE',flush=True)
if __name__=='__main__': main()
