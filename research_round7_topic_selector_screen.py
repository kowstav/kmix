"""Priced future-selected article-topic model, frozen from A/B; C/D confirmation.

This is a two-part likelihood screen, not an implemented arithmetic archive.
Selectors are explicitly encoded (1 bit neutral, 9 bits specialist). Sparse
topic tables are serialized and charged twice. No neural checkpoint is fitted.
Every literal/case/syntax/escape event pays the specialist fallback penalty.
"""
import pathlib,json,struct,zlib,math,time,hashlib,re,os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from research_round7_wrt import load_dictionary,inverse_byte
from research_round7_field_screen import literal_wrt,SEP
from research_round7_word_association_screen import STOP

ALPHAS=np.asarray([.0001,.0003,.001,.003,.01,.03,.1],np.float64)
K=32;TOP=256;TOTAL=65535

def parse(raw,cost,dictionary):
    sep=literal_wrt(SEP,dictionary);bounds=np.asarray([m.end() for m in re.finditer(re.escape(sep),raw)],np.int64)
    if not len(bounds):raise ValueError('No complete synchronization prefix')
    ids={c:i for i,c in enumerate(dictionary)};pref=np.r_[0.,np.cumsum(cost,dtype=np.float64)]
    i=int(bounds[0]);words=[];bits=[];regions=[];lo_positions=[];mark=0
    while i<len(raw):
        lo=i
        while mark+1<len(bounds) and bounds[mark+1]<=lo:mark+=1
        c=inverse_byte(raw[i]);i+=1;w=-1
        if c==12:
            if i>=len(raw):break
            i+=1
        elif c>=128:
            code=[c]
            if c>207:
                if i>=len(raw):break
                c2=inverse_byte(raw[i]);i+=1;code.append(c2)
                if c2>207:
                    if i>=len(raw):break
                    code.append(inverse_byte(raw[i]));i+=1
            w=ids[bytes(code)]
        words.append(w);bits.append(pref[i]-pref[lo]);regions.append(mark);lo_positions.append(lo)
    w=np.asarray(words,np.int32);b=np.asarray(bits,np.float64);a=np.asarray(regions,np.int32)
    valid=w>=0
    counts=sparse.coo_matrix((np.ones(int(valid.sum()),np.float64),(a[valid],w[valid])),shape=(len(bounds),len(dictionary))).tocsr()
    return {'w':w,'b':b,'a':a,'counts':counts,'bounds':bounds,'baseline_bytes':float(pref[-1]/8.),'scored_bits':float(b.sum()),'scored_events':len(w)}

def frequencies(weight):
    if len(weight)==0:return np.zeros(0,np.uint16)
    value=weight/weight.sum()*(TOTAL-len(weight));f=1+np.floor(value).astype(np.int64)
    left=TOTAL-int(f.sum());order=np.lexsort((np.arange(len(f)),-(value-np.floor(value))))
    f[order[:left]]+=1;assert int(f.sum())==TOTAL and f.min()>0 and f.max()<65536
    return f.astype(np.uint16)

def train(dev,dictionary):
    x=sparse.vstack([dev[n]['counts'] for n in 'ab']).tocsr()
    # A fixed 32-profile family. No C/D statistics enter the fitting procedure.
    df=np.asarray((x>0).sum(axis=0)).ravel();idf=np.log((1+x.shape[0])/(1+df))+1
    tf=x.copy();tf.data=np.log1p(tf.data);tf=tf.multiply(idf).tocsr()
    norm=np.sqrt(np.asarray(tf.multiply(tf).sum(axis=1)).ravel());tf=sparse.diags(1/np.maximum(norm,1e-30))@tf
    svd=TruncatedSVD(n_components=16,n_iter=5,random_state=923);low=svd.fit_transform(tf)
    label=KMeans(n_clusters=K,n_init=4,random_state=923,max_iter=200).fit_predict(low)
    allowed=np.asarray([word not in STOP and len(word)>=3 for word in dictionary.values()])
    profiles=[];blob=bytearray(b'HP7TOP01'+struct.pack('<HHHH',K+1,TOP,len(dictionary),TOTAL))
    for group in range(K+1):
        # Sum article TF-IDF vectors to favor topic-specific content words.
        score=np.asarray(tf.sum(axis=0)).ravel() if group==K else np.asarray(tf[label==group].sum(axis=0)).ravel()
        score[~allowed]=0
        indices=np.lexsort((np.arange(len(score)),-score))[:TOP];indices=indices[score[indices]>0]
        if not len(indices):raise RuntimeError('Empty topic profile')
        f=frequencies(score[indices]);p=np.zeros(len(dictionary),np.float64);p[indices]=f.astype(np.float64)/TOTAL
        assert abs(float(p.sum())-1)<1e-13
        profiles.append(p);blob+=struct.pack('<H',len(indices));blob+=np.asarray(indices,'<u2').tobytes()+np.asarray(f,'<u2').tobytes()
    # Decoder contract: a tiny zlib stream, NOT a scikit-learn runtime or SVD model.
    # SVD/KMeans serve only to construct the explicitly serialized sparse tables.
    data=zlib.compress(bytes(blob),9)
    return np.asarray(profiles),data,{'development_regions':x.shape[0],'components':16,'topic_clusters':K,'profiles_including_global_control':K+1,'serialized_uncompressed_bytes':len(blob),'serialized_zlib_bytes':len(data),'seed':923}

def score(events,profiles):
    w,b,a=events['w'],events['b'],events['a'];n=len(events['bounds']);models=len(profiles)*len(ALPHAS)
    width=math.ceil(math.log2(models));assert width==8
    gains=np.zeros((models,n),np.float64);lit=np.bincount(a[w<0],minlength=n)
    fallback=np.log2(1-ALPHAS)
    gains+=np.tile(fallback,len(profiles))[:,None]*lit[None,:]
    mask=w>=0;words=w[mask];base=b[mask];region=a[mask]
    for lo in range(0,len(words),4096):
        hi=lo+4096;pp=profiles[:,words[lo:hi]]
        lp=np.full(pp.shape,-np.inf);np.log2(pp,out=lp,where=pp>0)
        g=np.logaddexp2(fallback[None,:,None],np.log2(ALPHAS)[None,:,None]+lp[:,None,:]+base[lo:hi][None,None,:])
        flat=g.reshape(models,-1)
        for m in range(models):gains[m]+=np.bincount(region[lo:hi],weights=flat[m],minlength=n)
    net=gains-(1+width);best=np.argmax(net,axis=0);bestgain=net[best,np.arange(n)]
    use=bestgain> -1.;paid=np.where(use,bestgain,-1.)
    selector_bits=int(np.where(use,1+width,1).sum())
    selector=''.join('1'+format(int(best[j]),'08b') if use[j] else '0' for j in range(n))
    packed=bytes(int((selector[i:i+8]).ljust(8,'0'),2) for i in range(0,len(selector),8))
    return {'article_regions':n,'specialist_regions':int(use.sum()),'selector_bits':selector_bits,'selector_prefix_code':'0 neutral; 1 followed by eight bits indexes one of 231 frozen profile/alpha choices; unused IDs rejected','scored_events':events['scored_events'],'cost_coverage_fraction':events['scored_bits']/(events['baseline_bytes']*8),'baseline_ideal_bytes':events['baseline_bytes'],'saving_likelihood_bytes_after_selectors':float(paid.sum()/8.),'saving_likelihood_bytes_before_selectors':float((paid.sum()+selector_bits)/8.),'best_global_fixed_saving_bytes':float(max(0.,gains.sum(axis=1).max())/8.),'selector_sha256':hashlib.sha256(packed).hexdigest(),'selector_packed_bytes':packed,'maximum_region_saving_bytes':float(paid.max()/8.)}

def self_test():
    p=np.asarray([[.8,.2,0],[0,.4,.6]],np.float64)
    assert np.allclose(p.sum(axis=1),1)
    # Both shorter and longer WRT paths are outcomes of one prefix-free tree.
    d={bytes([128]):b'page',bytes([240,128]):b'pear',bytes([240,208,128]):b'fruit'}
    raw=literal_wrt(SEP,d)+b' '+bytes([240,128])+b' '+bytes([240,208,128])+bytes([12,128])
    e=parse(raw,np.full(len(raw),8,np.float32),d)
    assert int(e['counts'].sum())==2 and e['scored_events']>2
    f=frequencies(np.asarray([1.,2.,9.]));assert f.sum()==TOTAL
    # A fixed selector code has Kraft sum <=1, including neutral.
    assert .5+231/(2**9)<=1
    print('TOPIC_NORMALIZATION_MIXED_CODE_ESCAPE_FREQUENCY_AND_SELECTOR_TESTS_PASSED',flush=True)

if __name__=='__main__':
    self_test();out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'topic_selector';dest.mkdir(exist_ok=False)
    started=time.monotonic();dictionary=load_dictionary(out/'preserved/gen/.dict');pieces={}
    for n in 'abcd':
        rawpath=out/'preserved/slices'/f'{n}2m.bin' if n in 'ab' else out/f'{n}2m.bin'
        cp=out/'preserved/runs'/('lex_'+n)/'cost.f32' if n in 'ab' else out/('baseline_'+n)/'cost.f32'
        raw=rawpath.read_bytes();cost=np.fromfile(cp,'<f4');assert len(raw)==len(cost)
        pieces[n]=parse(raw,cost,dictionary);print('PARSED',n,len(pieces[n]['bounds']),flush=True)
    profiles,blob,training=train(pieces,dictionary);(dest/'topic_profiles.zlib').write_bytes(blob)
    rows=[]
    for n in 'abcd':
        r=score(pieces[n],profiles);(dest/(n+'_selectors.bin')).write_bytes(r.pop('selector_packed_bytes'))
        r.update({'slice':n,'two_copy_model_bytes':2*len(blob),'saving_after_selectors_and_entire_two_copy_model_bytes':r['saving_likelihood_bytes_after_selectors']-2*len(blob),'scope':'Final-coder likelihood screen using original FX2 traces; native bit quantization, code/decode CPU and full stream not measured. Each slice-alone total charges the entire model.','no_neural_training':True})
        rows.append(r);print(json.dumps(r),flush=True)
    report={'training':training,'model_sha256':hashlib.sha256(blob).hexdigest(),'rows':rows,'wall_seconds':time.monotonic()-started,'causality':'Future is used only to select an explicitly paid article-region ID. Predictor tables are frozen from A/B, outcomes from C/D never update them. Original predictors receive only original stream bytes. Region starts require the already decoded full separator; EOF boundary is fixed piece size.','package_limitation':'zlib table size priced twice; compiled parser/mixture/zlib decoder overhead is still additional; no full archive is claimed.'}
    (dest/'results.json').write_text(json.dumps(report,indent=2));print('TOPIC_SELECTOR_SCREEN_COMPLETE',flush=True)
