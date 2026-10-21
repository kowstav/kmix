"""I02 diagnostic: causal donor availability, hypothetical perfect support only.

Uses the exact I03 dictionary-derived graph. Does not choose predictions,
encode a selector, or claim attainable compression from coverage.
"""
import pathlib,json,time,re,collections,resource,numpy as np
from research_round7_idea_arch_screen import graph
from research_round7_wrt import load_dictionary,inverse_byte
from research_round7_field_screen import literal_wrt,SEP,TEND

def measure(raw,cost,dictionary):
    started=time.monotonic();codes=list(dictionary);ids={c:i for i,c in enumerate(codes)}
    graphs,meta=graph(list(dictionary.values()));N=len(codes)
    # Candidate activation membership, not approximate/weighted probability.
    edges=[[np.asarray([v for v,_ in row],np.int32) for row in g] for g in graphs]
    counts=np.zeros((4,4,N),np.int32);history=collections.deque(maxlen=256)
    exact=np.zeros((4,N),np.int32);global_seen=set();article_seen=set()
    sep=literal_wrt(SEP,dictionary);tend=literal_wrt(TEND,dictionary)
    first=raw.find(sep);assert first>=0;i=first+len(sep);offset=i
    markers=sorted([(m.end(),'start') for m in re.finditer(re.escape(sep),raw)]+[(m.end(),'end') for m in re.finditer(re.escape(tend),raw)])
    mi=0;in_title=True;prefix=np.r_[0.,np.cumsum(cost,dtype=np.float64)];buckets={};atoms=0;union={};cut_bytes=0
    while i<len(raw):
        lo=i
        while mi<len(markers) and markers[mi][0]<=lo:
            if markers[mi][1]=='start':history.clear();counts[:]=0;exact[:]=0;article_seen.clear();in_title=True
            else:in_title=False
            mi+=1
        c=inverse_byte(raw[i]);i+=1
        if c==12:
            if i<len(raw):i+=1
            else:cut_bytes=1
            continue
        if c<128:continue
        code=[c];cut=False
        if c>207:
            if i==len(raw):cut=True
            else:
                c2=inverse_byte(raw[i]);code.append(c2);i+=1
                if c2>207:
                    if i==len(raw):cut=True
                    else:code.append(inverse_byte(raw[i]));i+=1
        if cut:cut_bytes=i-lo;break
        code=bytes(code);assert code in ids;w=ids[code];bits=float(prefix[i]-prefix[lo])
        cls='first_in_slice' if w not in global_seen else 'known_first_in_article' if w not in article_seen else 'article_repeat'
        phase='title' if in_title else 'body';atoms+=1
        for ch in range(5):
            present=exact[:,w]>0 if ch==4 else counts[ch,:,w]>0
            if np.any(present):
                k=(ch,cls,phase);r=union.setdefault(k,[0,0.]);r[0]+=1;r[1]+=bits
            for b in np.flatnonzero(present):
                k=(ch,int(b),cls,phase);r=buckets.setdefault(k,[0,0.]);r[0]+=1;r[1]+=bits
        # Shift only sources crossing a lag-bin edge; no256-source scan.
        for b,h in enumerate([4,16,64,256]):
            if len(history)>=h:
                u=history[-h];exact[b,u]-=1
                if b<3:exact[b+1,u]+=1
                for ch in range(4):
                    vs=edges[ch][u];counts[ch,b,vs]-=1
                    if b<3:counts[ch,b+1,vs]+=1
        exact[0,w]+=1
        for ch in range(4):counts[ch,0,edges[ch][w]]+=1
        history.append(w);global_seen.add(w);article_seen.add(w)
    assert np.all(counts>=0) and np.all(exact>=0),'Lag membership accounting failed'
    return {'raw_bytes':len(raw),'unscored_prefix_bytes':offset,'dictionary_atoms':atoms,
            'baseline_suffix_bits':float(prefix[-1]-prefix[offset]),'cut_tail_bytes':cut_bytes,
            'scope':'Hypothetical perfect prediction of covered complete dictionary-code spans only; excludes selection/fallback/code and may exceed128-slot support',
            'channels':['prefix_suffix','deletion_signature','letter_moment','matched_random','exact_word'],
            'lag_bins':['1-4','5-16','17-64','65-256'],'clock':'completed dictionary atoms','reset':'after complete decoded page marker',
            'union_no_double_count_by_channel':[{'channel':k[0],'class':k[1],'phase':k[2],'events':v[0],'baseline_bits':v[1]} for k,v in sorted(union.items())],
            'lag_categories_overlap':[{'channel':k[0],'lag_bin':k[1],'class':k[2],'phase':k[3],'events':v[0],'baseline_bits':v[1]} for k,v in sorted(buckets.items())],
            'graph':meta,'wall_seconds':time.monotonic()-started,'prototype_peak_rss_kbytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'achieved_compression_gain':None,'neural_training':False,'paid_rental_usd':0,'deletions':[]}

def tests():
    # Verify all boundary memberships against direct history, including duplicates.
    H=collections.deque(maxlen=256);a=np.zeros((4,7),np.int32)
    for t in range(600):
        expected=np.zeros_like(a)
        for d,u in enumerate(reversed(H),1):expected[0 if d<=4 else 1 if d<=16 else 2 if d<=64 else 3,u]+=1
        assert np.array_equal(a,expected),'Lag transition differs from direct history'
        if t==333:H.clear();a[:]=0
        w=(t*3)%7
        for b,h in enumerate([4,16,64,256]):
            if len(H)>=h:
                u=H[-h];a[b,u]-=1
                if b<3:a[b+1,u]+=1
        a[0,w]+=1;H.append(w)
    print('LAG_BOUNDARY_AND_RESET_TESTS_PASS',flush=True)

if __name__=='__main__':
    tests();out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'idea_arch_lag_budget_v1';dest.mkdir(exist_ok=False)
    dictionary=load_dictionary(out/'preserved/gen/.dict');rows=[]
    for n in 'abcd':
        p=out/'preserved/slices'/(n+'2m.bin') if n in 'ab' else out/(n+'2m.bin')
        raw=p.read_bytes();cost=np.fromfile(out/'lex_native_2m'/(n+'_cost.f32'),'<f4');assert len(raw)==len(cost)==2000000
        r=measure(raw,cost,dictionary);(dest/(n+'.json')).write_text(json.dumps(r,indent=2))
        row={'slice':n,'covered_bits_by_channel':{c:sum(x['baseline_bits'] for x in r['union_no_double_count_by_channel'] if x['channel']==c) for c in range(5)},
             'baseline_suffix_bits':r['baseline_suffix_bits'],'wall_seconds':r['wall_seconds'],'achieved_gain':None}
        rows.append(row);(dest/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
    print('IDEA_ARCH_LAG_BUDGET_COMPLETE',flush=True)
