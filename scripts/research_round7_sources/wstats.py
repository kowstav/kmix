# Weight statistics of the shipped int4 model: per-tensor entropy, level histograms,
# and how the entropy responds to scale inflation (post-training, no fine-tune).
import torch, numpy as np, math, json, sys
sd = torch.load('/root/hp/src/fx2-cmix-transformer-v1/models/6m-q4-fp32.tch', map_location='cpu')

def bf16(x):
    return x.to(torch.bfloat16).to(torch.float32)

def H(counts):
    c = np.asarray(counts, dtype=np.float64); c = c[c > 0]; p = c / c.sum()
    return float(-(p * np.log2(p)).sum())

rows = []
allq = []
tot_w = 0
for k, v in sd.items():
    if not k.endswith('.weight'):
        continue
    base = k[:-len('.weight')]
    sk = base + '.quantize_weight.scale'
    if sk not in sd:
        continue
    W = v.float(); s = bf16(sd[sk].float())
    if W.dim() == 2 and s.numel() == W.shape[0]:
        q = torch.clamp(torch.round(W / s[:, None]), -7, 7)
    else:
        print('skip shape', k, W.shape, s.shape); continue
    qi = q.to(torch.int64).flatten().numpy() + 7
    cnt = np.bincount(qi, minlength=15)
    allq.append(qi)
    clip = float(((W / s[:, None]).abs() > 7.5).float().mean())
    rows.append((k, tuple(W.shape), H(cnt), clip, cnt.tolist()))
    tot_w += W.numel()

allq = np.concatenate(allq)
cnt = np.bincount(allq, minlength=15)
print('total quantized weights', tot_w, 'global H', H(cnt), 'bits; bytes at H:', tot_w * H(cnt) / 8)
print('global hist', (cnt / cnt.sum()).round(4).tolist())
# per-tensor adaptive coding cost (sum of per-tensor entropies)
pt = sum(np.prod(r[1]) * r[2] for r in rows) / 8
print('sum per-tensor-entropy bytes', pt)
for r in rows[:200]:
    print(f'{r[0]:60s} {str(r[1]):12s} H={r[2]:.3f} clip={r[3]:.4f}')
# non-quantized params
nq = 0
for k, v in sd.items():
    if 'scale' in k: continue
    if k.endswith('.weight') and (k[:-7] + '.quantize_weight.scale') in sd: continue
    nq += v.numel();
print('non-quantized float params', nq)
