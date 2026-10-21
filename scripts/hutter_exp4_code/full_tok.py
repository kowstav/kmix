"""Complete decoder-side system for a dictionary-coded transformer (zero archive cost beyond the model):
  1. online adaptation while decoding,
  2. hidden-state cache over the current stream (context miner #1),
  3. kNN over the model's states on previously decoded articles (context miner #2),
mixed per (entropy, similarity) bucket with weights chosen online from already-coded statistics.
Reports bits per ORIGINAL byte on the held-out test.
"""
import sys, math, json, time, argparse, pickle
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, '/kaggle/working/hutter_lab/exp4')
from dtok import TokLM, allowed_mask, V, G, M
from knn_train import topk_search

E4 = Path('/kaggle/working/hutter_lab/exp4')
DATA = Path('/kaggle/working/hutter_lab/exp2/data')


def forward_states(model, prev):
    h = model.tok(prev) + model.pos.weight[:prev.shape[1]]
    if model.charemb:
        h = h + model.letters(prev)
    for b in model.blocks:
        h = b(h)
    h = model.norm(h)
    return h, model.head(h)


def ship(model, bits):
    """Replace the trained weights by exactly what would be stored: QLinear weights as their b-bit codes x scale,
    token/position tables as per-row 8-bit, everything else fp16. The decoder starts from this model."""
    sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
    from lm import QLinear
    with torch.no_grad():
        for m in model.modules():
            if isinstance(m, QLinear):
                m.qbits = bits
                c, sc = m.codes()
                m.weight.copy_(c.float() * sc)
                m.qbits = 0
        qn = {n + '.weight' for n, m in model.named_modules() if isinstance(m, QLinear)}
        for n, p in model.named_parameters():
            if n in qn:
                continue
            if p.dim() >= 2:                      # embedding-like tables and the output head: per-row 8-bit
                sc = p.abs().amax(-1, keepdim=True).clamp_min(1e-8) / 127
                p.copy_((p / sc).round().clamp(-127, 127) * sc)
            else:
                p.copy_(p.half().float())


def ship_bytes(model, bits):
    """Stored size of the shipped model: entropy of the b-bit codes (+fp16 scales) for QLinear weights, entropy of the
    8-bit codes (+fp16 per-row scales) for other matrices, fp16 for vectors."""
    sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
    from lm import QLinear, quant_params
    import math as _m
    def ent(c):
        cnt = np.bincount(c - c.min()).astype(float); pr = cnt[cnt > 0] / cnt.sum()
        return c.size * float(-(pr * np.log2(pr)).sum())
    total = 0.0
    qn = set()
    with torch.no_grad():
        for n, m in model.named_modules():
            if isinstance(m, QLinear):
                qn.add(n + '.weight')
                sc, q = quant_params(m.weight, bits)
                c = (m.weight / sc).round().clamp(-q, q).flatten().cpu().numpy().astype(np.int64)
                total += ent(c) + sc.numel() * 16
        for n, p in model.named_parameters():
            if n in qn:
                continue
            if p.dim() >= 2:
                sc = p.abs().amax(-1, keepdim=True).clamp_min(1e-8) / 127
                c = (p / sc).round().clamp(-127, 127).flatten().cpu().numpy().astype(np.int64)
                total += ent(c) + sc.numel() * 16
            else:
                total += p.numel() * 16
    return int(total / 8)


def group_topk(sc, k, G=16):
    """Exact top-k per row: the k best entries lie inside the k groups (of G columns) with the largest maxima."""
    q, nb = sc.shape
    nbg = nb // G * G
    if nbg < G * k:
        return sc.topk(min(k, nb), dim=-1)
    sg = sc[:, :nbg].view(q, nbg // G, G)
    _, gi = sg.amax(-1).topk(k, dim=-1)
    cand = sg.gather(1, gi[..., None].expand(-1, -1, G)).reshape(q, -1)
    cidx = (gi[..., None] * G + torch.arange(G, device=sc.device)).reshape(q, -1)
    if nbg < nb:
        cand = torch.cat([cand, sc[:, nbg:]], 1)
        cidx = torch.cat([cidx, torch.arange(nbg, nb, device=sc.device).expand(q, -1)], 1)
    v, j = cand.topk(k, dim=-1)
    return v, cidx.gather(1, j)


def topk_outer(Qn, blocks, k, dev, qchunk=512):
    """Exact top-k cosine search with the datastore held in CPU blocks; each block is moved to the GPU once."""
    nq = Qn.shape[0]
    TV = torch.full((nq, k), -1e4, dtype=torch.float16, device=dev)
    TI = torch.zeros((nq, k), dtype=torch.int64, device=dev)
    off = 0
    for blk in blocks:
        Kb = blk.to(dev)
        nb = Kb.shape[0]
        for q0 in range(0, nq, qchunk):
            q1 = min(nq, q0 + qchunk)
            v, i = (Qn[q0:q1] @ Kb.T).topk(min(k, nb), dim=-1)
            v2 = torch.cat([TV[q0:q1], v], 1); i2 = torch.cat([TI[q0:q1], i + off], 1)
            bv, j = v2.topk(k, dim=-1)
            TV[q0:q1] = bv; TI[q0:q1] = i2.gather(1, j)
        off += nb
        del Kb
    return TV.cpu(), TI.cpu()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scheme', required=True)
    ap.add_argument('--run', required=True)
    ap.add_argument('--lr', type=float, default=1e-5)
    ap.add_argument('--S', type=int, default=12000)
    ap.add_argument('--tau_c', type=float, default=0.03)
    ap.add_argument('--tau_k', type=float, default=0.02)
    ap.add_argument('--dfrom', type=int, default=0, help='datastore: start token (use with --base_ret to extend a datastore)')
    ap.add_argument('--reuse_ret', default='', help='use saved retrievals instead of building/searching a datastore')
    ap.add_argument('--base_ret', default='', help='saved retrievals over tokens [0, dfrom) to merge with')
    ap.add_argument('--dtokens', type=int, default=14_000_000, help='datastore: first N training tokens')
    ap.add_argument('--ent', type=float, default=1.0)
    ap.add_argument('--qent', type=float, default=0.5)
    ap.add_argument('--k', type=int, default=64)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--stride', type=int, default=0, help='sliding-window stride for the adaptive pass (default ctx/2)')
    ap.add_argument('--tag', default='')
    ap.add_argument('--save_mix', action='store_true')
    ap.add_argument('--cpu_store', action='store_true', help='keep the datastore in CPU blocks (large datastores)')
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    ck = torch.load(E4 / 'runs' / a.run / 'model.pt', map_location='cpu')
    code, tr_tok, te_tok, te_orig = pickle.loads((E4 / f'dtok_{a.scheme}.pkl').read_bytes())
    words = [b''] * (G * M)
    for w, (g_, m_) in code.items():
        words[g_ * M + m_] = w
    gsize = np.zeros(G, np.int64)
    for g_, m_ in code.values():
        gsize[g_] = max(gsize[g_], m_ + 1)
    model = TokLM(**{k: ck['cfg'][k] for k in ('d', 'layers', 'ctx')}, charemb=ck['cfg'].get('charemb', False), words=words).to(dev)
    model.load_state_dict(ck['state'])
    import re
    qm = re.search(r'_q(\d+)', a.run)
    if qm:
        ship(model, int(qm.group(1)))
        print('shipped model: weights replaced by their stored', qm.group(1), 'bit form', flush=True)
    model.eval()
    ctx, half, d = model.cfg['ctx'], model.cfg['ctx'] // 2, model.cfg['d']
    BOS = V
    t0 = time.time()
    # ---------- datastore from previously decoded text (frozen model) ----------
    tr = np.concatenate([[BOS], tr_tok[:a.dtokens].astype(np.int64)]) if a.dfrom == 0 else tr_tok[a.dfrom - 1:a.dtokens].astype(np.int64)
    Tr = torch.as_tensor(tr)
    keys, vals, blocks, pend = [], [], [], 0
    with torch.no_grad():
        last = len(tr) - ctx - 1
        wins = list(range(0, last + 1, ctx))            # non-overlapping windows are enough for a datastore
        for i in range(0, len(wins), 32):
            ws = wins[i:i + 32]
            prev = torch.stack([Tr[w:w + ctx] for w in ws]).to(dev)
            y = torch.stack([Tr[w + 1:w + 1 + ctx] for w in ws]).to(dev)
            with torch.autocast('cuda', torch.float16):
                h, lg = forward_states(model, prev)
            lp = lg.float().log_softmax(-1)
            ent = -(lp.exp() * lp).sum(-1)
            sel = ent > a.ent
            kk = F.normalize(h[sel].float(), dim=-1).half()
            if a.cpu_store:
                keys.append(kk.cpu()); vals.append(y[sel].cpu()); pend += len(kk)
                if pend >= 1_000_000:
                    blocks.append(torch.cat(keys)); keys = []; pend = 0
            else:
                keys.append(kk); vals.append(y[sel])
    if a.cpu_store:
        if keys:
            blocks.append(torch.cat(keys))
        Kdb = None; Vdb = torch.cat(vals)
    else:
        Kdb = torch.cat(keys); Vdb = torch.cat(vals)
    del keys
    print(json.dumps({'datastore': int(len(Vdb)), 'from_tokens': a.dtokens, 'min': round((time.time() - t0) / 60, 1)}), flush=True)
    # ---------- adaptive pass over the test stream ----------
    nbytes = len((DATA / 'test.bin').read_bytes())
    T = torch.as_tensor(np.concatenate([[BOS], te_tok.astype(np.int64)]))
    nt = len(te_tok)
    K = torch.zeros(nt, d, dtype=torch.float16)
    PT = torch.zeros(nt); ENT = torch.zeros(nt)
    LPF = torch.zeros(nt, V, dtype=torch.float16) if a.save_mix else None
    opt = torch.optim.Adam(model.parameters(), lr=a.lr) if a.lr > 0 else None
    last = max(0, nt - ctx)
    st = a.stride or half
    starts = list(range(0, last + 1, st)) + ([last] if last % st else [])
    covered = 0
    for s in starts:
        prev = T[s:s + ctx].to(dev)[None]
        y = T[s + 1:s + 1 + ctx].to(dev)[None]
        model.eval()
        with torch.no_grad(), torch.autocast('cuda', torch.float16):
            h, lg = forward_states(model, prev)
        lg = lg.float().masked_fill(~allowed_mask(prev, gsize, dev), -1e30)
        lp = lg.log_softmax(-1)
        end = min(s + ctx, nt)
        if end > covered:
            lo, hi = covered - s, end - s
            K[covered:end] = h[0, lo:hi].half().cpu()
            PT[covered:end] = lp[0, lo:hi].gather(-1, y[0, lo:hi, None])[:, 0].exp().cpu()
            ENT[covered:end] = -(lp[0, lo:hi].exp() * lp[0, lo:hi].clamp_min(-1e4)).sum(-1).cpu()
            if LPF is not None:
                LPF[covered:end] = lp[0, lo:hi].exp().half().cpu()
            covered = end
        if opt is not None:
            model.train()
            with torch.autocast('cuda', torch.float16):
                loss = F.cross_entropy(model(prev).float().reshape(-1, V), y.reshape(-1))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    base_bits = float(-(PT.clamp_min(1e-12)).log2().sum())
    print(json.dumps({'adapted_bpb': base_bits / nbytes, 'min': round((time.time() - t0) / 60, 1)}), flush=True)
    # ---------- miners ----------
    Qn = F.normalize(K.float(), dim=-1).half().to(dev)
    tok = torch.as_tensor(te_tok.astype(np.int64)).to(dev)
    prevall = T[:-1].to(dev)
    qidx = torch.nonzero(ENT > a.qent)[:, 0]
    if a.reuse_ret:
        # retrievals made with another ensemble member's states (the decoder runs that model too)
        rr = torch.load(E4 / a.reuse_ret)
        TV = rr['TV']; TI = rr['TI'].long(); Vdb = rr['Vdb'].long(); del rr
        print('reusing retrievals from', a.reuse_ret, flush=True)
    elif a.cpu_store:
        TVq, TIq = topk_outer(Qn[qidx.to(dev)], blocks, a.k, dev)
        del blocks
    else:
        TVq, TIq = topk_outer(Qn[qidx.to(dev)], list(Kdb.split(1_000_000)), a.k, dev)
    if not a.reuse_ret:
        TV = torch.full((nt, a.k), -1e4, dtype=torch.float16); TI = torch.zeros((nt, a.k), dtype=torch.int64)
        TV[qidx] = TVq; TI[qidx] = TIq
    if a.base_ret:
        base = torch.load(E4 / a.base_ret)
        nbase = len(base['Vdb'])
        v2 = torch.cat([base['TV'], TV], 1); i2 = torch.cat([base['TI'].long(), TI + nbase], 1)
        TV, j = v2.float().topk(a.k, dim=-1); TV = TV.half(); TI = i2.gather(1, j)
        Vdb = torch.cat([base['Vdb'].long().to(Vdb.device), Vdb])
        del base, v2, i2
        print('merged with base datastore of', nbase, '-> total', len(Vdb), flush=True)
    if not a.reuse_ret:
        torch.save({'TV': TV, 'TI': TI.int(), 'Vdb': Vdb.cpu().short()}, E4 / f'knn_ret_{a.run}{a.tag}.pt')
    print('knn done', int(len(qidx)), 'queries', round((time.time() - t0) / 60, 1), 'min', flush=True)
    Kdb = None; Vdb = Vdb.to(dev)
    pc_true = torch.zeros(nt); pk_true = torch.zeros(nt); sc = torch.zeros(nt); sk = torch.zeros(nt)
    Q = 2048
    for q0 in range(1, nt, Q):
        q1 = min(nt, q0 + Q)
        ok = allowed_mask(prevall[q0:q1][None], gsize, dev)[0]
        c0 = max(0, q0 - a.S)
        sims = Qn[q0:q1].float() @ Qn[c0:q1].float().T
        sims = sims.masked_fill(torch.arange(c0, q1, device=dev)[None, :] >= torch.arange(q0, q1, device=dev)[:, None], -1e4)
        tv, ti = sims.topk(min(64, sims.shape[1]), dim=-1)
        w = torch.softmax(tv / a.tau_c, -1) * (tv > -1e3)
        pc = torch.zeros(q1 - q0, V, device=dev).scatter_add_(1, tok[c0 + ti], w) * ok
        pc = pc / pc.sum(-1, keepdim=True).clamp_min(1e-9)
        pc_true[q0:q1] = pc.gather(1, tok[q0:q1, None])[:, 0].cpu()
        sc[q0:q1] = tv[:, 0].cpu()
        tvk = TV[q0:q1].to(dev).float(); tik = TI[q0:q1].to(dev)
        wk = torch.softmax(tvk / a.tau_k, -1) * (tvk > -1e3)
        pk = torch.zeros(q1 - q0, V, device=dev).scatter_add_(1, Vdb[tik], wk) * ok
        pk = pk / pk.sum(-1, keepdim=True).clamp_min(1e-9)
        pk_true[q0:q1] = pk.gather(1, tok[q0:q1, None])[:, 0].cpu()
        sk[q0:q1] = tvk[:, 0].cpu()
    NB_E, NB_S = 12, 6
    eb = torch.clamp((ENT / 0.35).long(), 0, NB_E - 1)
    sbk = torch.clamp(((torch.maximum(sk, sc).clamp(-1, 1) + 1) / 2 * NB_S).long(), 0, NB_S - 1)
    bucket = (eb * NB_S + sbk).numpy()
    grid = [(x, y) for x in (0, 0.03, 0.08, 0.15, 0.3, 0.5) for y in (0, 0.03, 0.08, 0.15, 0.3, 0.5) if x + y < 0.9]
    A = np.array([g[0] for g in grid]); Bw = np.array([g[1] for g in grid])
    mix = np.log2((1 - A - Bw)[None] * PT.numpy()[:, None] + A[None] * pc_true.numpy()[:, None] + Bw[None] * pk_true.numpy()[:, None] + 1e-12)
    res = {'run': a.run, 'adapted_bpb': base_bits / nbytes, 'datastore': int(len(Vdb))}
    for name, cols in (('cache', [i for i, g in enumerate(grid) if g[1] == 0]), ('knn', [i for i, g in enumerate(grid) if g[0] == 0]),
                       ('cache_knn', list(range(len(grid))))):
        acc = np.zeros((NB_E * NB_S, len(cols)))
        tot = 0.0
        cols_a = np.array(cols)
        for s0 in range(0, nt, 4096):
            s1 = min(nt, s0 + 4096)
            bk = bucket[s0:s1]
            ch = acc[bk].argmax(1)
            tot += float(-mix[np.arange(s0, s1), cols_a[ch]].sum())
            np.add.at(acc, bk, mix[s0:s1][:, cols])
        res[f'adapted_plus_{name}_bpb'] = tot / nbytes
        print(name, tot / nbytes, flush=True)
        if name == 'cache_knn' and a.save_mix:
            # replay the online choice and write the decoder-replicable mixed distribution
            acc = np.zeros((NB_E * NB_S, len(cols))); wa = np.zeros(nt, np.float32); wb = np.zeros(nt, np.float32)
            for s0 in range(0, nt, 4096):
                s1 = min(nt, s0 + 4096)
                bk = bucket[s0:s1]
                ch = acc[bk].argmax(1)
                wa[s0:s1] = A[cols_a[ch]]; wb[s0:s1] = Bw[cols_a[ch]]
                np.add.at(acc, bk, mix[s0:s1][:, cols])
            out = np.lib.format.open_memmap(str(E4 / f'pmix_tok_{a.run}{a.tag}.npy'), 'w+', np.float16, (nt, V))
            for q0 in range(0, nt, Q):
                q1 = min(nt, q0 + Q)
                ok = allowed_mask(prevall[q0:q1][None], gsize, dev)[0]
                pm = LPF[q0:q1].float().to(dev)
                if q0 == 0:
                    pc = pm.clone(); pk = pm.clone()
                else:
                    c0 = max(0, q0 - a.S)
                    sims = Qn[q0:q1].float() @ Qn[c0:q1].float().T
                    sims = sims.masked_fill(torch.arange(c0, q1, device=dev)[None, :] >= torch.arange(q0, q1, device=dev)[:, None], -1e4)
                    tv, ti = sims.topk(min(64, sims.shape[1]), dim=-1)
                    w = torch.softmax(tv / a.tau_c, -1) * (tv > -1e3)
                    pc = torch.zeros(q1 - q0, V, device=dev).scatter_add_(1, tok[c0 + ti], w) * ok
                    pc = pc / pc.sum(-1, keepdim=True).clamp_min(1e-9)
                    tvk = TV[q0:q1].to(dev).float(); tik = TI[q0:q1].to(dev)
                    wk = torch.softmax(tvk / a.tau_k, -1) * (tvk > -1e3)
                    pk = torch.zeros(q1 - q0, V, device=dev).scatter_add_(1, Vdb[tik], wk) * ok
                    pk = pk / pk.sum(-1, keepdim=True).clamp_min(1e-9)
                la = torch.as_tensor(wa[q0:q1], device=dev)[:, None]; lb = torch.as_tensor(wb[q0:q1], device=dev)[:, None]
                pmx = (1 - la - lb) * pm + la * pc + lb * pk
                out[q0:q1] = (pmx / pmx.sum(-1, keepdim=True).clamp_min(1e-12)).half().cpu().numpy()
            out.flush()
    res['minutes'] = round((time.time() - t0) / 60, 1)
    (E4 / f'full_tok_{a.run}{a.tag}.json').write_text(json.dumps(res, indent=1))
    print('FINAL', json.dumps(res), flush=True)


if __name__ == '__main__':
    main()
