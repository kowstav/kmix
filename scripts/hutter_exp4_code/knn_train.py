"""Context miner #2: kNN retrieval over states the model produced on PREVIOUSLY DECODED articles, combined with
miner #1 (the in-stream cache). Decoder-replicable: the datastore is built from text the decoder already has.

datastore : model states at positions of the first --dbytes of the training text where the model was uncertain
            (entropy > --ent nats), value = the byte that followed.
query     : every test position. p_knn from the top-k most similar stored states.
mixture   : p = (1 - a - b) p_model + a p_cache + b p_knn, (a, b) chosen ONLINE per (entropy, similarity) bucket
            from a small grid using only already-coded statistics.
"""
import sys, math, json, time, argparse
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
sys.path.insert(0, '/kaggle/working/hutter_lab/exp4')
from lm import LM
from knn_cache import states

E2 = Path('/kaggle/working/hutter_lab/exp2')
E4 = Path('/kaggle/working/hutter_lab/exp4')


def topk_search(Qn, Kdb, k, qchunk=512, kblock=1_000_000, causal_offset=None):
    """Exact top-k cosine search, blocked over queries and keys. Returns (sims [nq,k], idx [nq,k])."""
    nq = Qn.shape[0]
    TV = torch.full((nq, k), -1e4, dtype=torch.float16)
    TI = torch.zeros((nq, k), dtype=torch.int64)
    for q0 in range(0, nq, qchunk):
        q1 = min(nq, q0 + qchunk)
        bv = None
        for k0 in range(0, Kdb.shape[0], kblock):
            k1 = min(Kdb.shape[0], k0 + kblock)
            s = Qn[q0:q1] @ Kdb[k0:k1].T
            v, i = s.topk(min(k, k1 - k0), dim=-1)
            i = i + k0
            if bv is None:
                bv, bi = v, i
            else:
                v2 = torch.cat([bv, v], 1); i2 = torch.cat([bi, i], 1)
                bv, j = v2.topk(k, dim=-1); bi = i2.gather(1, j)
        TV[q0:q1] = bv.cpu(); TI[q0:q1] = bi.cpu()
    return TV, TI


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='f288')
    ap.add_argument('--dbytes', type=int, default=40_000_000)
    ap.add_argument('--ent', type=float, default=1.0)
    ap.add_argument('--k', type=int, default=64)
    ap.add_argument('--tau_knn', type=float, default=0.015)
    ap.add_argument('--tau_cache', type=float, default=0.015)
    ap.add_argument('--S', type=int, default=16384)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--save_mix', action='store_true')
    ap.add_argument('--qent', type=float, default=0.5, help='only query positions with model entropy above this (nats)')
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    ck = torch.load(E2 / 'runs' / a.run / 'model.pt', map_location='cpu')
    c = ck['cfg']
    model = LM(c['d'], c['layers'], c['ctx']).to(dev)
    model.load_state_dict(ck['state'])
    model.eval()
    t0 = time.time()
    # ---- datastore from previously decoded text ----
    tr = (E2 / 'data/train.bin').read_bytes()[:a.dbytes]
    keys, vals, kept = [], [], 0
    seg = 4_000_000
    for s0 in range(0, len(tr), seg):                      # stream: keep only uncertain positions
        part = tr[max(0, s0 - c['ctx']):s0 + seg]
        off = s0 - max(0, s0 - c['ctx'])
        Kd, LPd = states(model, part, c['ctx'], dev)
        ent_d = -(LPd.float().exp() * LPd.float()).sum(-1)
        sel = torch.nonzero(ent_d > a.ent)[:, 0]
        sel = sel[sel >= max(1, off)]
        keys.append(F.normalize(Kd[sel].float(), dim=-1).half())
        vals.append(torch.as_tensor(np.frombuffer(part, np.uint8).astype(np.int64))[sel])
        kept += len(sel)
        del Kd, LPd
    keep = torch.arange(kept)
    Kdb = torch.cat(keys).to(dev)
    Vdb = torch.cat(vals).to(dev)
    del keys, vals
    print(json.dumps({'datastore_positions': int(len(keep)), 'from_bytes': a.dbytes, 'kept_share': float(len(keep) / len(tr)),
                      'min': round((time.time() - t0) / 60, 1)}), flush=True)
    # ---- test states ----
    test = (E2 / 'data/test.bin').read_bytes()
    n = len(test)
    K, LP = states(model, test, c['ctx'], dev)
    x = torch.as_tensor(np.frombuffer(test, np.uint8).astype(np.int64))
    xs = x.to(dev)
    pm_true = LP.float().gather(1, x[:, None])[:, 0].exp()
    base = float((-pm_true.log2()).mean())
    ent = -(LP.float().exp() * LP.float()).sum(-1)
    Qn = F.normalize(K.float(), dim=-1).half().to(dev)
    # ---- kNN over the datastore ----
    cache = E4 / f'knn_search_{a.dbytes // 1_000_000}MB_q{a.qent}.pt'
    qidx = torch.nonzero(ent > a.qent)[:, 0]
    if cache.exists():
        TVq, TIq = torch.load(cache)
    else:
        TVq, TIq = topk_search(Qn[qidx.to(dev)], Kdb, a.k)
        torch.save((TVq, TIq), cache)
    TV = torch.full((n, a.k), -1e4, dtype=torch.float16); TI = torch.zeros((n, a.k), dtype=torch.int64)
    TV[qidx] = TVq; TI[qidx] = TIq
    print('knn search done', int(len(qidx)), 'queries', round((time.time() - t0) / 60, 1), 'min', flush=True)

    def dist_from(tv, ti, values, tau, nrows):
        w = torch.softmax(tv.float() / tau, -1) * (tv.float() > -1e3)
        w = w / w.sum(-1, keepdim=True).clamp_min(1e-9)
        return torch.zeros(nrows, 256, device=dev).scatter_add_(1, values[ti], w)

    pk_true = torch.zeros(n); pc_true = torch.zeros(n); sk = torch.zeros(n); sc = torch.zeros(n)
    Q = 2048
    for q0 in range(1, n, Q):
        q1 = min(n, q0 + Q)
        pk = dist_from(TV[q0:q1].to(dev), TI[q0:q1].to(dev), Vdb, a.tau_knn, q1 - q0)
        pk_true[q0:q1] = pk.gather(1, xs[q0:q1, None])[:, 0].cpu()
        sk[q0:q1] = TV[q0:q1, 0].float()
        c0 = max(0, q0 - a.S)
        sims = Qn[q0:q1].float() @ Qn[c0:q1].float().T
        sims = sims.masked_fill(torch.arange(c0, q1, device=dev)[None, :] >= torch.arange(q0, q1, device=dev)[:, None], -1e4)
        tv, ti = sims.topk(min(64, sims.shape[1]), dim=-1)
        pc = dist_from(tv, ti, xs[c0:], a.tau_cache, q1 - q0)
        pc_true[q0:q1] = pc.gather(1, xs[q0:q1, None])[:, 0].cpu()
        sc[q0:q1] = tv[:, 0].cpu()
    # ---- online mixture weights per bucket (decoder-replicable) ----
    NB_E, NB_S = 12, 6
    eb = torch.clamp((ent / 0.35).long(), 0, NB_E - 1)
    sbk = torch.clamp(((torch.maximum(sk, sc) + 1) / 2 * NB_S).long(), 0, NB_S - 1)
    bucket = (eb * NB_S + sbk).numpy()
    grid = [(ac, bk) for ac in (0, 0.03, 0.08, 0.15, 0.3, 0.5) for bk in (0, 0.03, 0.08, 0.15, 0.3, 0.5) if ac + bk < 0.9]
    A = torch.tensor([g[0] for g in grid]); Bw = torch.tensor([g[1] for g in grid])
    mix = torch.log2((1 - A - Bw)[None] * pm_true[:, None] + A[None] * pc_true[:, None] + Bw[None] * pk_true[:, None] + 1e-12).numpy()
    res = {'model_alone_bpb': base}
    for name, cols in (('cache_only', [i for i, g in enumerate(grid) if g[1] == 0]), ('knn_only', [i for i, g in enumerate(grid) if g[0] == 0]),
                       ('cache_plus_knn', list(range(len(grid))))):
        acc = np.zeros((NB_E * NB_S, len(cols)))
        tot = 0.0
        for s0 in range(0, n, 4096):
            s1 = min(n, s0 + 4096)
            bk_ = bucket[s0:s1]
            ch = acc[bk_].argmax(1)
            tot += -mix[np.arange(s0, s1)[:, None], np.array(cols)[None, :]][np.arange(s1 - s0), ch].sum()
            np.add.at(acc, bk_, mix[s0:s1][:, cols])
        res[name] = {'bpb': float(tot / n), 'gain_vs_model_pct': float(100 * (1 - tot / n / base))}
        print(name, json.dumps(res[name]), flush=True)
    res.update({'datastore_positions': int(len(keep)), 'dbytes': a.dbytes, 'k': a.k, 'tau_knn': a.tau_knn, 'S': a.S,
                'minutes': round((time.time() - t0) / 60, 1)})
    (E4 / f'knn_train_{a.dbytes // 1_000_000}MB.json').write_text(json.dumps(res, indent=1, default=float))


if __name__ == '__main__':
    main()
