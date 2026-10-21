"""Online two-way linear blend: neural system (cache+kNN mixture) and the token-level classical coder.
p = (1 - lam) p_nn + lam p_cm, lam chosen per bucket (nn entropy x previous-token class) from a grid using only
already-coded statistics (decoder-replicable). Both are normalized distributions, so only true-token probs are needed.
usage: blend2.py pmix.npy tcm_prefix
"""
import sys, json
import numpy as np

E4 = '/kaggle/working/hutter_lab/exp4'
NBYTES = 2293540
P = np.load(sys.argv[1], mmap_mode='r')
pre = sys.argv[2]
te = np.fromfile(f'{E4}/distrib_test.u16', np.uint16).astype(np.int64)
nt = len(te)
cm_bits = np.fromfile(f'{pre}_cm.f32', np.float32).astype(np.float64)
mx_bits = np.fromfile(f'{pre}_mix.f32', np.float32).astype(np.float64)
pn = np.zeros(nt); ent = np.zeros(nt); pmax = np.zeros(nt)
for s in range(0, nt, 100000):
    p = np.asarray(P[s:s + 100000], np.float32) + 1e-8
    p /= p.sum(1, keepdims=True)
    k = len(p)
    pn[s:s + k] = p[np.arange(k), te[s:s + k]]
    ent[s:s + k] = -(p * np.log(p)).sum(1)
    pmax[s:s + k] = p.max(1)
prev = np.concatenate([[0], te[:-1]])
cls = np.where(prev < 256, 0, np.where(prev < 512, 1, 2))
lams = np.array([0, 0.005, 0.01, 0.02, 0.04, 0.07, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6])


def online(pa, pb, bucket):
    mix = np.log2((1 - lams)[None] * pa[:, None] + lams[None] * pb[:, None] + 1e-15)
    acc = np.zeros((bucket.max() + 1, len(lams)))
    tot = 0.0
    for s0 in range(0, nt, 2048):
        s1 = min(nt, s0 + 2048)
        bk = bucket[s0:s1]
        ch = acc[bk].argmax(1)
        tot += -mix[np.arange(s0, s1), ch].sum()
        np.add.at(acc, bk, mix[s0:s1])
    return tot


res = {'nn_bpb': float(-np.log2(pn).sum() / NBYTES), 'cm_bpb': float(cm_bits.sum() / NBYTES), 'tcm_mixer_bpb': float(mx_bits.sum() / NBYTES)}
eb = np.clip((ent / 0.3).astype(int), 0, 15)
mb = np.clip((pmax * 8).astype(int), 0, 7)
for name, pb in (('cm', 2 ** -cm_bits), ('tcm_mixer', 2 ** -mx_bits)):
    for bname, bucket in (('ent', eb), ('ent_cls', eb * 3 + cls), ('ent_cls_pmax', (eb * 3 + cls) * 8 + mb)):
        res[f'nn+{name}|{bname}'] = float(online(pn, pb, bucket) / NBYTES)
print(json.dumps(res, indent=1))
