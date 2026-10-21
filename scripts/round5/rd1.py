# Post-training rate-distortion probe: inflate per-row scales by alpha (same 15 levels),
# measure global int4 entropy and transformer loss on an eval article set.
import sys, time, json, math
import numpy as np, torch
sys.path.insert(0, '/root/hp/tools')
import tfh

dev = 'cuda'
data = tfh.Data()
print('articles with priors:', data.n_art_avail, 'tokens', int(data.bounds[data.n_art_avail]))
# eval set: every 3rd article among the available ones, capped at ~1.5M tokens
arts = []
tot = 0
for a in range(0, data.n_art_avail, 3):
    L = int(data.bounds[a + 1] - data.bounds[a])
    arts.append(a); tot += L
    if tot > 1_500_000:
        break
print('eval articles', len(arts), 'tokens', tot)

base_sd = torch.load(tfh.REPO + '/models/6m-q4-fp32.tch', map_location='cpu')
model = tfh.load_model()

def entropy_bits(counts):
    c = counts[counts > 0].astype(np.float64); p = c / c.sum(); return float(-(p * np.log2(p)).sum())

def apply_alpha(alpha_fn):
    sd = {k: v.clone() for k, v in base_sd.items()}
    hist = np.zeros(15, np.int64); nw = 0
    for k in list(sd.keys()):
        if not k.endswith('.quantize_weight.scale'):
            continue
        wk = k.replace('.quantize_weight.scale', '.weight')
        a = alpha_fn(wk)
        s = sd[k].float() * a
        sd[k] = s
        W = sd[wk].float(); sb = s.to(torch.bfloat16).float()
        q = torch.clamp(torch.round(W / sb[:, None]), -7, 7).to(torch.int64) + 7
        hist += np.bincount(q.flatten().numpy(), minlength=15); nw += W.numel()
    model.load_state_dict(sd)
    return entropy_bits(hist), nw

def loss_now():
    res = tfh.eval_articles(model, data, arts)
    tot = sum(float(v.sum()) for v in res.values()); n = sum(len(v) for v in res.values())
    return tot / n, n

out = []
for alpha in [1.0, 1.05, 1.1, 1.2, 1.3, 1.5]:
    t0 = time.time()
    H, nw = apply_alpha(lambda k: alpha)
    L, n = loss_now()
    rec = dict(alpha=alpha, H=H, wbytes=H * nw / 8, loss_nats=L, n=n, sec=time.time() - t0)
    print(json.dumps(rec)); sys.stdout.flush(); out.append(rec)
json.dump(out, open('/root/hp/results/rd1.json', 'w'), indent=1)
