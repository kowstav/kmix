"""Frozen NN distribution calibration; no checkpoint or optimizer is changed."""
import argparse,json,math,time
from pathlib import Path
import numpy as np
import torch

TAUS=np.asarray([.6,.7,.8,.9,1.,1.1,1.2,1.3,1.5],np.float64)

def logsum2(x):
    m=x.max(axis=1)
    return m+np.log2(np.exp2(x-m[:,None]).sum(axis=1))

def evaluate(name,out,device):
    raw=np.fromfile(f'/root/hp/slices/{name}2m.bin','u1')
    vocab=np.fromfile('/root/hp/data/vocab.list','u1')
    inverse=np.full(256,-1,np.int64);inverse[vocab]=np.arange(205)
    probs=np.memmap(f'/root/hp/slices/{name}2m.probs.f16','<f2',mode='r',shape=(len(raw),205))
    likelihoods=np.zeros((len(raw)-1,len(TAUS)),np.float64)
    entropies=np.zeros(len(raw)-1,np.float64)
    taus=torch.tensor(TAUS,device=device,dtype=torch.float32)
    with torch.no_grad():
        for s in range(1,len(raw),8192):
            e=min(len(raw),s+8192)
            p=torch.tensor(np.asarray(probs[s-1:e-1],np.float32),device=device).clamp_min(1e-6)
            p=p/p.sum(-1,keepdim=True)
            lp=p.log()
            target=torch.tensor(inverse[raw[s:e]],device=device)
            if bool((target<0).any()):raise RuntimeError('Target outside neural vocabulary')
            entropy=-(p*lp).sum(-1)/math.log(2)
            entropies[s-1:e-1]=entropy.cpu().numpy()
            actual=lp.gather(1,target[:,None])[:,0]
            # Power calibration normalized over all 205 symbols, not just target.
            adjusted=actual[:,None]*taus[None,:]-torch.logsumexp(lp[:,:,None]*taus[None,None,:],dim=1)
            likelihoods[s-1:e-1]=adjusted.cpu().numpy()/math.log(2)
    base_index=list(TAUS).index(1.)
    baseline=-float(likelihoods[:,base_index].sum())
    totals=-likelihoods.sum(axis=0)
    results=[]
    for contextual in [False,True]:
        contexts=np.minimum(7,entropies.astype(np.int64)) if contextual else np.zeros(len(entropies),np.int64)
        bits=0.;regret=0.;counts=[]
        for c in range(8 if contextual else 1):
            use=np.flatnonzero(contexts==c)
            if not len(use):continue
            # Exact Bayesian sequence mixture; initial tau index costs log2(K).
            # The cumulative expression equals filtering tau weights AFTER each
            # consumed symbol and can be implemented by the independent decoder.
            final=likelihoods[use].sum(axis=0)
            z=float(logsum2(final[None,:])[0]-math.log2(len(TAUS)))
            bits-=z
            regret+=math.log2(len(TAUS))
            counts.append({'context':c,'symbols':len(use)})
        results.append({'entropy_contexts':contextual,'saving_bytes':(baseline-bits)/8.,
                        'ideal_bits_per_symbol':bits/len(likelihoods),'neutral_regret_bound_bits':regret,
                        'counts':counts})
    r={'slice':name,'frozen_checkpoint':True,'symbols':len(likelihoods),
       'baseline_ideal_bytes':baseline/8.,'baseline_bits_per_symbol':baseline/len(likelihoods),
       'contract':'standalone NN likelihood only, float32 GPU normalization; native final coder and package unmeasured',
       'fixed_temperatures':[{'tau':float(t),'saving_bytes':float((baseline-total)/8.),'relative_gain':float((baseline-total)/baseline)} for t,total in zip(TAUS,totals)],
       'prequential_mixtures':results}
    (out/(name+'_neural_temperature.json')).write_text(json.dumps(r,indent=2))
    print(json.dumps(r),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--slice',required=True);ap.add_argument('--out',required=True);ap.add_argument('--device',default='cuda:0');args=ap.parse_args()
    torch.set_num_threads(1)
    evaluate(args.slice,Path(args.out),args.device)
