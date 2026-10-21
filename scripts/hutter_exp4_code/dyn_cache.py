"""Online adaptation + hidden-state cache miner, in one decoder-replicable pass.

Windows of ctx bytes, stride ctx/2, in stream order. For each window: score the new half with the CURRENT weights
(recording the hidden states), then take one Adam step on the window (the decoder knows those bytes now).
Afterwards the cache miner mixes in p_cache with online per-bucket weights, as in knn_cache.py.
"""
import sys, math, json, time, argparse
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
from lm import LM

E2 = Path('/kaggle/working/hutter_lab/exp2')
E4 = Path('/kaggle/working/hutter_lab/exp4')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='f288')
    ap.add_argument('--lr', type=float, default=1e-5)
    ap.add_argument('--S', type=int, default=16384)
    ap.add_argument('--tau', type=float, default=0.03)
    ap.add_argument('--topk', type=int, default=64)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--save_mix', action='store_true')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    ck = torch.load(E2 / 'runs' / a.run / 'model.pt', map_location='cpu')
    c = ck['cfg']
    model = LM(c['d'], c['layers'], c['ctx']).to(dev)
    model.load_state_dict(ck['state'])
    opt = torch.optim.Adam(model.parameters(), lr=a.lr) if a.lr > 0 else None
    test = (E2 / 'data/test.bin').read_bytes()
    n = len(test)
    arr = torch.as_tensor(np.frombuffer(test, np.uint8).astype(np.int64))
    ctx, half = c['ctx'], c['ctx'] // 2
    K = torch.zeros(n, c['d'], dtype=torch.float16)
    LP = torch.zeros(n, 256, dtype=torch.float16)
    LP[0] = math.log(1 / 256)
    last = n - ctx - 1
    starts = list(range(0, last + 1, half)) + ([last] if last % half else [])
    covered = 1
    t0 = time.time()
    for s in starts:
        x = arr[s:s + ctx + 1].to(dev)[None]
        model.eval()
        with torch.no_grad(), torch.autocast('cuda', torch.float16):
            h = model.tok(x[:, :-1]) + model.pos.weight[:ctx]
            for b in model.blocks:
                h = b(h)
            h = model.norm(h)
            lg = model.head(h)
        lo, hi = max(covered, s + 1), min(s + 1 + ctx, n)
        if hi > lo:
            K[lo:hi] = h[0, lo - s - 1:hi - s - 1].half().cpu()
            LP[lo:hi] = lg[0, lo - s - 1:hi - s - 1].float().log_softmax(-1).half().cpu()
            covered = hi
        if opt is not None:
            model.train()
            with torch.autocast('cuda', torch.float16):
                loss = F.cross_entropy(model(x[:, :-1]).float().reshape(-1, 256), x[:, 1:].reshape(-1))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    xs = arr.to(dev)
    pm_true = LP.float().gather(1, arr[:, None])[:, 0].exp()
    adapted = float((-pm_true.clamp_min(1e-12).log2()).mean())
    print(json.dumps({'adapted_model_bpb': adapted, 'lr': a.lr, 'min': round((time.time() - t0) / 60, 1)}), flush=True)
    # ---- cache miner on top ----
    Kn = F.normalize(K.float(), dim=-1).half().to(dev)
    ent = -(LP.float().exp() * LP.float()).sum(-1)
    pc_true = torch.zeros(n); simmax = torch.zeros(n)
    Q = 2048

    def cache_dist(q0, q1):
        c0 = max(0, q0 - a.S)
        sims = Kn[q0:q1].float() @ Kn[c0:q1].float().T
        sims = sims.masked_fill(torch.arange(c0, q1, device=dev)[None, :] >= torch.arange(q0, q1, device=dev)[:, None], -1e4)
        tv, ti = sims.topk(min(a.topk, sims.shape[1]), dim=-1)
        w = torch.softmax(tv / a.tau, -1) * (tv > -1e3)
        w = w / w.sum(-1, keepdim=True).clamp_min(1e-9)
        return torch.zeros(q1 - q0, 256, device=dev).scatter_add_(1, xs[c0 + ti], w), tv[:, 0]

    for q0 in range(1, n, Q):
        q1 = min(n, q0 + Q)
        pc, sm = cache_dist(q0, q1)
        pc_true[q0:q1] = pc.gather(1, xs[q0:q1, None])[:, 0].cpu()
        simmax[q0:q1] = sm.cpu()
    NB_E, NB_S = 12, 8
    bucket = (torch.clamp((ent / 0.35).long(), 0, NB_E - 1) * NB_S + torch.clamp(((simmax + 1) / 2 * NB_S).long(), 0, NB_S - 1)).numpy()
    lams = np.array([0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8])
    mix = np.log2((1 - lams)[None] * pm_true.numpy()[:, None] + lams[None] * pc_true.numpy()[:, None] + 1e-12)
    acc = np.zeros((NB_E * NB_S, len(lams)))
    tot = 0.0
    lam_pos = np.zeros(n, np.float32)
    for s0 in range(0, n, 4096):
        s1 = min(n, s0 + 4096)
        bk = bucket[s0:s1]
        ch = acc[bk].argmax(1)
        lam_pos[s0:s1] = lams[ch]
        tot += -mix[np.arange(s0, s1), ch].sum()
        np.add.at(acc, bk, mix[s0:s1])
    res = {'model': a.run, 'lr': a.lr, 'adapted_model_bpb': adapted, 'adapted_plus_cache_bpb': tot / n, 'S': a.S, 'tau': a.tau}
    print(json.dumps(res), flush=True)
    if a.save_mix:
        out = np.lib.format.open_memmap(str(E4 / f'pmix_dyncache{a.tag}.npy'), 'w+', np.float16, (n, 256))
        out[0] = 1 / 256
        lt = torch.as_tensor(lam_pos)
        for q0 in range(1, n, Q):
            q1 = min(n, q0 + Q)
            pc, _ = cache_dist(q0, q1)
            lam = lt[q0:q1].to(dev)[:, None]
            pmx = (1 - lam) * LP[q0:q1].float().exp().to(dev) + lam * pc
            out[q0:q1] = (pmx / pmx.sum(-1, keepdim=True)).half().cpu().numpy()
        out.flush()
    (E4 / f'dyn_cache{a.tag}.json').write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
