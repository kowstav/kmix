"""Online adaptation + hidden-state cache miner for the dictionary-coded transformer (dtok.py models).
Decoder-replicable: constraints, cache and mixture weights use only already-decoded tokens.
Reports bits per ORIGINAL byte on the held-out test.
"""
import sys, math, json, time, argparse, pickle
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, '/kaggle/working/hutter_lab/exp4')
from dtok import TokLM, allowed_mask, V, G, M

E4 = Path('/kaggle/working/hutter_lab/exp4')
DATA = Path('/kaggle/working/hutter_lab/exp2/data')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scheme', required=True)
    ap.add_argument('--lr', type=float, default=1e-5)
    ap.add_argument('--S', type=int, default=12000, help='cache length in tokens (~16K bytes)')
    ap.add_argument('--tau', type=float, default=0.03)
    ap.add_argument('--topk', type=int, default=64)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--stride', type=int, default=0, help='sliding-window stride for the adaptive pass (default ctx/2)')
    ap.add_argument('--tag', default='')
    ap.add_argument('--run', default='', help='run dir under exp4/runs (default dtok_<scheme>)')
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    run = a.run or f'dtok_{a.scheme}'
    ck = torch.load(E4 / 'runs' / run / 'model.pt', map_location='cpu')
    code, _, te_tok, te_orig = pickle.loads((E4 / f'dtok_{a.scheme}.pkl').read_bytes())
    words = [b''] * (G * M)
    for w, (g_, m_) in code.items():
        words[g_ * M + m_] = w
    model = TokLM(**{k: ck['cfg'][k] for k in ('d', 'layers', 'ctx')}, charemb=ck['cfg'].get('charemb', False), words=words).to(dev)
    model.load_state_dict(ck['state'])
    gsize = np.zeros(G, np.int64)
    for g, m in code.values():
        gsize[g] = max(gsize[g], m + 1)
    nbytes = len((DATA / 'test.bin').read_bytes())
    BOS = V
    T = torch.as_tensor(np.concatenate([[BOS], te_tok.astype(np.int64)]))    # T[i+1] = token i
    nt = len(te_tok)
    ctx, half = model.cfg['ctx'], model.cfg['ctx'] // 2
    d = model.cfg['d']
    K = torch.zeros(nt, d, dtype=torch.float16)
    PT = torch.zeros(nt)                       # model prob of the true token (constrained)
    ENT = torch.zeros(nt)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr) if a.lr > 0 else None
    last = max(0, nt - ctx)
    st = a.stride or half
    starts = list(range(0, last + 1, st)) + ([last] if last % st else [])
    covered = 0
    t0 = time.time()
    for s in starts:
        prev = T[s:s + ctx].to(dev)[None]
        y = T[s + 1:s + 1 + ctx].to(dev)[None]
        model.eval()
        with torch.no_grad(), torch.autocast('cuda', torch.float16):
            hh = model.tok(prev) + model.pos.weight[:prev.shape[1]]
            if model.charemb:
                hh = hh + model.letters(prev)
            for b in model.blocks:
                hh = b(hh)
            hh = model.norm(hh)
            lg = model.head(hh).float()
        lg = lg.masked_fill(~allowed_mask(prev, gsize, dev), -1e30)
        lp = lg.log_softmax(-1)
        end = min(s + ctx, nt)
        if end > covered:
            lo, hi = covered - s, end - s
            K[covered:end] = hh[0, lo:hi].half().cpu()
            PT[covered:end] = lp[0, lo:hi].gather(-1, y[0, lo:hi, None])[:, 0].exp().cpu()
            ENT[covered:end] = -(lp[0, lo:hi].exp() * lp[0, lo:hi].clamp_min(-1e4)).sum(-1).cpu()
            covered = end
        if opt is not None:
            model.train()
            with torch.autocast('cuda', torch.float16):
                loss = F.cross_entropy(model(prev).float().reshape(-1, V), y.reshape(-1))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    adapted_bits = float(-(PT.clamp_min(1e-12)).log2().sum())
    print(json.dumps({'scheme': a.scheme, 'lr': a.lr, 'adapted_bpb': adapted_bits / nbytes, 'min': round((time.time() - t0) / 60, 1)}), flush=True)
    # ---- cache over the model's own past states (values = the token that followed) ----
    Kn = F.normalize(K.float(), dim=-1).half().to(dev)
    tok = torch.as_tensor(te_tok.astype(np.int64)).to(dev)
    prevall = T[:-1].to(dev)                  # token before position i
    pc_true = torch.zeros(nt); simmax = torch.zeros(nt)
    Q = 2048
    for q0 in range(1, nt, Q):
        q1 = min(nt, q0 + Q)
        c0 = max(0, q0 - a.S)
        sims = Kn[q0:q1].float() @ Kn[c0:q1].float().T
        sims = sims.masked_fill(torch.arange(c0, q1, device=dev)[None, :] >= torch.arange(q0, q1, device=dev)[:, None], -1e4)
        tv, ti = sims.topk(min(a.topk, sims.shape[1]), dim=-1)
        w = torch.softmax(tv / a.tau, -1) * (tv > -1e3)
        pc = torch.zeros(q1 - q0, V, device=dev).scatter_add_(1, tok[c0 + ti], w)
        ok = allowed_mask(prevall[q0:q1][None], gsize, dev)[0]
        pc = pc * ok
        pc = pc / pc.sum(-1, keepdim=True).clamp_min(1e-9)
        pc_true[q0:q1] = pc.gather(1, tok[q0:q1, None])[:, 0].cpu()
        simmax[q0:q1] = tv[:, 0].cpu()
    NB_E, NB_S = 12, 8
    bucket = (torch.clamp((ENT / 0.35).long(), 0, NB_E - 1) * NB_S + torch.clamp(((simmax + 1) / 2 * NB_S).long(), 0, NB_S - 1)).numpy()
    lams = np.array([0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8])
    mix = np.log2((1 - lams)[None] * PT.numpy()[:, None] + lams[None] * pc_true.numpy()[:, None] + 1e-12)
    acc = np.zeros((NB_E * NB_S, len(lams)))
    tot = 0.0
    for s0 in range(0, nt, 4096):
        s1 = min(nt, s0 + 4096)
        bk = bucket[s0:s1]
        ch = acc[bk].argmax(1)
        tot += -mix[np.arange(s0, s1), ch].sum()
        np.add.at(acc, bk, mix[s0:s1])
    res = {'scheme': a.scheme, 'lr': a.lr, 'adapted_bpb': adapted_bits / nbytes, 'adapted_plus_cache_bpb': tot / nbytes,
           'S_tokens': a.S, 'tau': a.tau}
    print(json.dumps(res), flush=True)
    res['run'] = run
    (E4 / f'dyn_cache_tok_{run}{a.tag}.json').write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
