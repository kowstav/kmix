"""Optimistic bound on changing probability precision, with predictor fixed.

Encoder Discretize is unsigned(1+65534*p); transmitted branch probability is
n/65536. Allow +/-0.02 in its float intermediate (conservative vs f32 ULP at
65535), and use the most favorable true p inside each bin for the observed bit.
Take positive part to permit an unpaid choice to retain old precision per bit.
This is an UPPER BOUND, not a coding gain or usable target-based selector.
"""
import pathlib,json,numpy as np
out=pathlib.Path('/kaggle/working/hp_round7');pre=out/'preserved'
results=[]
for name in 'ab':
    raw=np.memmap(pre/f'slices/{name}2m.bin',dtype='u1',mode='r')
    trace=np.memmap(out/f'trace_{name}/final_p.u16',dtype='<u2',mode='r')
    if len(trace)!=8*len(raw):raise RuntimeError('Trace shape mismatch')
    bound=0.;signed=0.;baseline=0.;bins={}
    for pos in range(0,len(raw),65536):
        stop=min(len(raw),pos+65536);bits=np.unpackbits(np.asarray(raw[pos:stop])).astype(bool)
        n=np.asarray(trace[8*pos:8*stop],dtype=np.float64)
        if n.min()<1 or n.max()>65535:raise RuntimeError('Invalid probability code')
        q=np.where(bits,n/65536.,1.-n/65536.)
        maxp=np.where(bits,np.minimum(1.,(n+.02)/65534.),1.-np.maximum(0.,(n-1.-.02)/65534.))
        gain=np.log2(maxp/q);bound+=float(np.maximum(gain,0.).sum());signed+=float(gain.sum());baseline+=float((-np.log2(q)).sum())
    row={'slice':name,'raw_bytes':len(raw),'baseline_ideal_bytes':baseline/8.,'optimistic_positive_precision_bound_bytes':bound/8.,'bound_fraction_of_baseline':bound/baseline,'signed_best_inside_bin_bound_bytes':signed/8.,'contract':'fixed predictor; conservative f32 rounding margin; unpaid per-bit upper bound only; no model calibration or decoder change measured'}
    results.append(row);print(json.dumps(row))
(out/'precision_only_bounds.json').write_text(json.dumps(results,indent=2))
