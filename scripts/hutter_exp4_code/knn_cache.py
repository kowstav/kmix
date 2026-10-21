"""Context miner #1: a cache of the model's OWN past hidden states (decoder-replicable, zero archive cost).

For every already-decoded position j we keep (key = transformer state that predicted byte j, value = byte j).
At position t the current state is compared with the cached states of the last S positions; the bytes that
followed the most similar states form p_cache. It is injected with a weight lambda that depends on how
uncertain the model is (entropy bucket) and how close the best match is (similarity bucket):
    p = (1 - lambda) * p_model + lambda * p_cache
lambda is learned ONLINE while decoding (a running per-bucket estimate), so the decoder can do exactly the same.
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


@torch.no_grad()
def states(model, data, ctx, dev, batch=48):
    """Sliding windows (stride ctx/2): per-position normalised hidden state and log-probs."""
    n = len(data)
    arr = torch.as_tensor(np.frombuffer(data, np.uint8).astype(np.int64))
    d = model.cfg['d']
    K = torch.zeros(n, d, dtype=torch.float16)
    LP = torch.zeros(n, 256, dtype=torch.float16)
    half = ctx // 2
    LP[0] = math.log(1 / 256)
    last = max(0, n - ctx - 1)
    wins = list(range(0, last + 1, half))
    if wins[-1] != last:
        wins.append(last)
    covered = 1
    for i in range(0, len(wins), batch):
        ws = wins[i:i + batch]
        inp = torch.stack([arr[w:w + ctx] for w in ws]).to(dev)        # output j predicts byte w+1+j (as in training)
        with torch.autocast('cuda', torch.float16):
            h = model.tok(inp) + model.pos.weight[:inp.shape[1]]
            for b in model.blocks:
                h = b(h)
            h = model.norm(h)
            lg = model.head(h)
        lp = lg.float().log_softmax(-1)
        for j, w in enumerate(ws):
            lo = max(covered, 1 if w == 0 else w + 1 + half)
            hi = min(w + 1 + ctx, n)
            if hi <= lo:
                continue
            K[lo:hi] = h[j, lo - w - 1:hi - w - 1].half().cpu()
            LP[lo:hi] = lp[j, lo - w - 1:hi - w - 1].half().cpu()
            covered = max(covered, hi)
    return K, LP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='f288')
    ap.add_argument('--S', type=int, default=16384, help='cache length (positions back)')
    ap.add_argument('--topk', type=int, default=64)
    ap.add_argument('--taus', default='0.03,0.06,0.12')
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--save_probs', action='store_true')
    ap.add_argument('--save_mix', action='store_true', help='write the final mixed distribution (for blending with the CM)')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    ck = torch.load(E2 / 'runs' / a.run / 'model.pt', map_location='cpu')
    c = ck['cfg']
    model = LM(c['d'], c['layers'], c['ctx']).to(dev)
    model.load_state_dict(ck['state'])
    model.eval()
    test = (E2 / 'data/test.bin').read_bytes()
    n = len(test)
    t0 = time.time()
    K, LP = states(model, test, c['ctx'], dev)
    x = torch.as_tensor(np.frombuffer(test, np.uint8).astype(np.int64))
    base = -LP.float().gather(1, x[:, None])[:, 0] / math.log(2)
    print('states', round(time.time() - t0), 's; model alone bpb', float(base.mean()), flush=True)
    Kn = F.normalize(K.float(), dim=-1).half().to(dev)
    xs = x.to(dev)
    ent = -(LP.float().exp() * LP.float()).sum(-1)                # nats
    NB_E, NB_S = 12, 8
    res = {'model_alone_bpb': float(base.mean())}
    for tau in [float(v) for v in a.taus.split(',')]:
        # pass 1: cache distribution per position (top-k over the last S positions, causal)
        Q = 2048
        pc_true = torch.zeros(n)          # p_cache(true byte)
        pm_true = LP.float().gather(1, x[:, None])[:, 0].exp()
        simmax = torch.zeros(n)
        probs_cache = np.lib.format.open_memmap(str(E4 / f'pcache_tau{tau}.npy'), 'w+', np.float16, (n, 256)) if a.save_probs else None
        for q0 in range(1, n, Q):
            q1 = min(n, q0 + Q)
            c0 = max(0, q0 - a.S)
            sims = Kn[q0:q1].float() @ Kn[c0:q1].float().T                  # [Q, C]
            jpos = torch.arange(c0, q1, device=dev)[None, :]
            tpos = torch.arange(q0, q1, device=dev)[:, None]
            sims = sims.masked_fill(jpos >= tpos, -1e4)                     # only strictly earlier positions
            k = min(a.topk, sims.shape[1])
            tv, ti = sims.topk(k, dim=-1)
            w = torch.softmax(tv / tau, -1) * (tv > -1e3)
            w = w / w.sum(-1, keepdim=True).clamp_min(1e-9)
            vals = xs[c0 + ti]                                               # [Q, k] bytes that followed
            pc = torch.zeros(q1 - q0, 256, device=dev).scatter_add_(1, vals, w)
            pc_true[q0:q1] = pc.gather(1, xs[q0:q1, None])[:, 0].cpu()
            simmax[q0:q1] = tv[:, 0].clamp(-1, 1).cpu()
            if probs_cache is not None:
                probs_cache[q0:q1] = pc.half().cpu().numpy()
        # pass 2: ONLINE per-bucket lambda (decoder-replicable): grid of lambdas, pick the running best per bucket
        eb = torch.clamp((ent / 0.35).long(), 0, NB_E - 1)
        sb = torch.clamp(((simmax + 1) / 2 * NB_S).long(), 0, NB_S - 1)
        bucket = (eb * NB_S + sb).numpy()
        lams = torch.tensor([0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8])
        mix = torch.log2((1 - lams)[None, :] * pm_true[:, None] + lams[None, :] * pc_true[:, None] + 1e-12).numpy()   # [n, L]
        acc = np.zeros((NB_E * NB_S, len(lams)))
        total = 0.0
        chunk = 4096
        lam_pos = np.zeros(n, np.float32)
        for s0 in range(0, n, chunk):                 # lambda for a chunk uses statistics of earlier chunks only
            s1 = min(n, s0 + chunk)
            bk = bucket[s0:s1]
            choice = acc[bk].argmax(1)
            lam_pos[s0:s1] = lams.numpy()[choice]
            total += -mix[np.arange(s0, s1), choice].sum()
            np.add.at(acc, bk, mix[s0:s1])
        if a.save_mix:                                 # recompute p_cache and write the decoder-replicable mixture
            out = np.lib.format.open_memmap(str(E4 / f'pmix_S{a.S}_tau{tau}{a.tag}.npy'), 'w+', np.float16, (n, 256))
            out[0] = 1 / 256
            lp_t = torch.as_tensor(lam_pos)
            for q0 in range(1, n, Q):
                q1 = min(n, q0 + Q)
                c0 = max(0, q0 - a.S)
                sims = Kn[q0:q1].float() @ Kn[c0:q1].float().T
                jpos = torch.arange(c0, q1, device=dev)[None, :]
                tpos = torch.arange(q0, q1, device=dev)[:, None]
                sims = sims.masked_fill(jpos >= tpos, -1e4)
                tv, ti = sims.topk(min(a.topk, sims.shape[1]), dim=-1)
                w = torch.softmax(tv / tau, -1) * (tv > -1e3)
                w = w / w.sum(-1, keepdim=True).clamp_min(1e-9)
                pc = torch.zeros(q1 - q0, 256, device=dev).scatter_add_(1, xs[c0 + ti], w)
                lam = lp_t[q0:q1].to(dev)[:, None]
                pmx = (1 - lam) * LP[q0:q1].float().exp().to(dev) + lam * pc
                out[q0:q1] = (pmx / pmx.sum(-1, keepdim=True)).half().cpu().numpy()
            out.flush()
        online_bpb = total / n
        best_fixed = float((-mix).mean(0).min())
        res[f'tau{tau}'] = {'online_lambda_bpb': online_bpb, 'best_single_lambda_bpb': best_fixed,
                            'gain_vs_model_pct': 100 * (1 - online_bpb / float(base.mean())),
                            'mean_lambda_chosen': float(lams[acc.argmax(1)].mean())}
        print(json.dumps({f"tau{tau}": res[f"tau{tau}"]}, default=float), flush=True)
    res['S'] = a.S
    res['topk'] = a.topk
    (E4 / f"knn_cache_S{a.S}.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == '__main__':
    main()
