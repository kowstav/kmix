"""Online ensemble of two complete systems that share the dictionary token space.
Candidates: linear (1-w) pA + w pB and geometric pA^(1-w) pB^w / Z for w on a grid; the candidate is chosen per
bucket (entropy of A x entropy of B) from already-coded statistics only (decoder-replicable).
usage: ens.py pmixA.npy pmixB.npy out.npy
"""
import sys, json
import numpy as np
import torch

E4 = '/kaggle/working/hutter_lab/exp4'
NBYTES = 2293540
A = np.load(sys.argv[1], mmap_mode='r'); B = np.load(sys.argv[2], mmap_mode='r')
te = torch.as_tensor(np.fromfile(f'{E4}/distrib_test.u16', np.uint16).astype(np.int64))
nt = len(te)
dev = torch.device('cuda:0')
W = torch.tensor([0, 0.15, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0], device=dev)
TAU = (0.9, 1.0, 1.1)                                       # geometric candidates also get a temperature
NC = len(W) * (1 + len(TAU))


def cands(pa, pb):
    lin = (1 - W)[None, :, None] * pa[:, None] + W[None, :, None] * pb[:, None]
    lg = (1 - W)[None, :, None] * pa.log()[:, None] + W[None, :, None] * pb.log()[:, None]
    return torch.cat([lin] + [torch.softmax(t * lg, -1) for t in TAU], 1)     # [n, NC, V]


costs = np.zeros((nt, NC)); bucket = np.zeros(nt, np.int64)
C = 4096
for s in range(0, nt, C):
    pa = torch.as_tensor(np.asarray(A[s:s + C], np.float32), device=dev) + 1e-7
    pb = torch.as_tensor(np.asarray(B[s:s + C], np.float32), device=dev) + 1e-7
    pa /= pa.sum(-1, keepdim=True); pb /= pb.sum(-1, keepdim=True)
    y = te[s:s + C].to(dev)
    pc = cands(pa, pb)
    costs[s:s + len(y)] = (-pc.gather(2, y[:, None, None].expand(-1, NC, 1))[..., 0].log2()).cpu().numpy()
    ea = -(pa * pa.log()).sum(-1); eb = -(pb * pb.log()).sum(-1)
    bucket[s:s + len(y)] = (torch.clamp((ea / 0.5).long(), 0, 7) * 8 + torch.clamp((eb / 0.5).long(), 0, 7)).cpu().numpy()
res = {'A_bpb': float(costs[:, 0].sum() / NBYTES), 'B_bpb': float(costs[:, len(W) - 1].sum() / NBYTES)}
best_fixed = costs.sum(0)
res['best_fixed'] = float(best_fixed.min() / NBYTES); res['best_fixed_idx'] = int(best_fixed.argmin())
acc = np.zeros((64, NC)); ch_all = np.zeros(nt, np.int64); tot = 0.0
for s0 in range(0, nt, 2048):
    s1 = min(nt, s0 + 2048)
    bk = bucket[s0:s1]
    ch = acc[bk].argmin(1)
    ch_all[s0:s1] = ch
    tot += costs[np.arange(s0, s1), ch].sum()
    np.add.at(acc, bk, costs[s0:s1])
res['online_bpb'] = float(tot / NBYTES)
print(json.dumps(res), flush=True)
out = np.lib.format.open_memmap(sys.argv[3], 'w+', np.float16, (nt, 768))
chg = torch.as_tensor(ch_all, device=dev)
for s in range(0, nt, C):
    pa = torch.as_tensor(np.asarray(A[s:s + C], np.float32), device=dev) + 1e-7
    pb = torch.as_tensor(np.asarray(B[s:s + C], np.float32), device=dev) + 1e-7
    pa /= pa.sum(-1, keepdim=True); pb /= pb.sum(-1, keepdim=True)
    pc = cands(pa, pb)
    sel = pc[torch.arange(len(pa), device=dev), chg[s:s + C]]
    out[s:s + len(pa)] = (sel / sel.sum(-1, keepdim=True)).half().cpu().numpy()
out.flush()
