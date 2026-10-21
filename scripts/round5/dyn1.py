# Online (test-time) adaptation of the output head, simulated on GPU from frozen hidden states.
# The decoder can do exactly this: after each token it knows the true byte and can take a
# gradient step on a small delta added to the unembedding.
import sys, time, json, math
import numpy as np, torch
sys.path.insert(0, '/root/hp/tools')
import tfh

dev = 'cuda'
NTOK = int(sys.argv[1]) if len(sys.argv) > 1 else 4_000_000
data = tfh.Data()
model = tfh.load_model()
b = data.bounds
# articles in stream order
arts = []
tot = 0
a = 0
while tot < NTOK and a < data.n_art_avail:
    arts.append(a); tot += int(b[a + 1] - b[a]); a += 1
print('articles', len(arts), 'tokens', tot); sys.stdout.flush()

# capture final normed activation (input of unembedding) -> quantized activation used by unembedding
H_list, T_list, L_list, ART = [], [], [], []
def hook(key, lp, tgt):
    pass

feats = {}
def fwd_capture(arts):
    res_h, res_t, res_lp = [], [], []
    with torch.no_grad():
        batch = []; blen = 0
        def flush():
            nonlocal batch, blen
            if not batch: return
            toks = np.concatenate([x[1] for x in batch]); pri = np.concatenate([x[2] for x in batch])
            cu = np.cumsum([0] + [len(x[1]) for x in batch]).astype(np.int32)
            x = torch.from_numpy(toks).to(dev)[None]; p = torch.from_numpy(pri).to(dev)[None]
            cuq = torch.from_numpy(cu).to(dev)[None]
            h = model.compute_last_activation(x, p, cuq)            # [1,T,192] normed
            lg = model.last_activation_to_logits(h, p)[0].float()
            lp = torch.log_softmax(lg, -1)
            for i, (key, t, _) in enumerate(batch):
                s, e = int(cu[i]), int(cu[i + 1])
                res_h.append(h[0, s:e - 1].half())
                res_t.append(torch.from_numpy(t[1:]).to(dev))
                res_lp.append(lp[s:e - 1].gather(1, res_t[-1][:, None])[:, 0])
                ART.append(key[0])
            batch = []; blen = 0
        for a in arts:
            t, P = data.article(a)
            for (s, e) in tfh.pieces_of(len(t)):
                if e - s < 2: continue
                if blen + (e - s) > (1 << 17): flush()
                batch.append(((a, s), t[s:e], P[s:e])); blen += e - s
        flush()
    return res_h, res_t, res_lp

t0 = time.time()
Hs, Ts, LPs = fwd_capture(arts)
print('captured', sum(len(x) for x in Ts), 'positions in', time.time() - t0); sys.stdout.flush()
base = -torch.cat(LPs).sum().item() / sum(len(x) for x in Ts)
print('base loss nats', base)

# unembedding pieces
U = model.unembedding
Wq = U.weight.detach().float()
ws = U.quantize_weight.scale.detach().float().to(torch.bfloat16).float()
Wd = torch.clamp(torch.round(Wq / ws[:, None]), -7, 7) * ws[:, None]       # dequantized weight [205,192]
asc = U.quantize_activation.scale.detach().float().to(torch.bfloat16).float()

def head_logits(h, dW, db):
    xq = torch.clamp(torch.round(h.float() / asc), -128, 127) * asc
    lg = xq @ (Wd + dW).t() + db
    return 15.0 * torch.tanh(lg / 15.0), xq

def run(lr, C=16, wd=0.0, carry=True, lr_b=None, mom=0.0):
    lr_b = lr if lr_b is None else lr_b
    dW = torch.zeros_like(Wd); db = torch.zeros(205, device=dev)
    vW = torch.zeros_like(Wd); vb = torch.zeros(205, device=dev)
    tot = 0.0; n = 0; last_art = None
    for h, t, art in zip(Hs, Ts, ART):
        if not carry and art != last_art:
            dW.zero_(); db.zero_()
        last_art = art
        for s in range(0, len(t), C):
            hh = h[s:s + C]; tt = t[s:s + C]
            lg, xq = head_logits(hh, dW, db)
            lp = torch.log_softmax(lg, -1)
            tot -= lp.gather(1, tt[:, None]).sum().item(); n += len(tt)
            # gradient of CE wrt pre-softcap logits
            p = lp.exp(); p[torch.arange(len(tt)), tt] -= 1
            g = p * (1 - torch.tanh(head_logits_pre(xq, dW, db) / 15.0) ** 2)
            gW = g.t() @ xq; gb = g.sum(0)
            vW.mul_(mom).add_(gW); vb.mul_(mom).add_(gb)
            dW.mul_(1 - wd).sub_(lr * vW); db.mul_(1 - wd).sub_(lr_b * vb)
    return tot / n

def head_logits_pre(xq, dW, db):
    return xq @ (Wd + dW).t() + db

out = dict(base=base)
for cfg in [dict(lr=0.0), dict(lr=1e-4), dict(lr=3e-4), dict(lr=1e-3), dict(lr=3e-3),
            dict(lr=1e-3, carry=False), dict(lr=3e-3, wd=1e-4), dict(lr=1e-2, wd=1e-3)]:
    t0 = time.time()
    L = run(**cfg)
    print(json.dumps(dict(cfg=cfg, loss=L, rel=(L / base - 1) * 100, sec=time.time() - t0))); sys.stdout.flush()
