"""Contest-faithful total WITH the hidden-state cache miner, measured over all of enwik8 (streaming).
archive = code length of every enwik8 token under p = (1 - lam) p_model + lam p_cache, where p_cache comes from the
model's own states over the previous S tokens and lam is chosen online per (entropy x similarity) bucket from
already-coded statistics. Shipped quantized weights; dictionary and weights are added to the total.
"""
import sys, json, time, argparse, pickle, lzma, math
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, '/kaggle/working/hutter_lab/exp4')
sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
from dtok import TokLM, allowed_mask, V, G, M
from full_tok import ship, ship_bytes, forward_states
from lm import set_q

E4 = Path('/kaggle/working/hutter_lab/exp4')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', required=True)
    ap.add_argument('--scheme', default='distrib')
    ap.add_argument('--bits', type=int, default=4)
    ap.add_argument('--S', type=int, default=12000)
    ap.add_argument('--tau', type=float, default=0.03)
    ap.add_argument('--seg', type=int, default=1_000_000)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--limit', type=int, default=0, help='debug: only the first N tokens')
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    t0 = time.time()
    ck = torch.load(E4 / 'runs' / a.run / 'model.pt', map_location='cpu')
    code = pickle.loads((E4 / f'dtok_{a.scheme}.pkl').read_bytes())[0]
    words = [b''] * (G * M)
    for w, (g_, m_) in code.items():
        words[g_ * M + m_] = w
    gsize = np.zeros(G, np.int64)
    for g_, m_ in code.values():
        gsize[g_] = max(gsize[g_], m_ + 1)
    model = TokLM(**{k: ck['cfg'][k] for k in ('d', 'layers', 'ctx')}, charemb=ck['cfg'].get('charemb', False), words=words).to(dev)
    model.load_state_dict(ck['state'])
    set_q(model, a.bits)
    stored = ship_bytes(model, a.bits)
    ship(model, a.bits)
    model.eval()
    dict_bytes = len(lzma.compress(b'\n'.join(words), preset=9 | lzma.PRESET_EXTREME))
    tok = np.load(E4 / f'dtok_{a.scheme}_allenwik8.npy').astype(np.int64)
    if a.limit:
        tok = tok[:a.limit]
    nt = len(tok)
    T = torch.as_tensor(np.concatenate([[V], tok]))
    ctx, half, d = model.cfg['ctx'], model.cfg['ctx'] // 2, model.cfg['d']
    S, SEG = a.S, a.seg
    # rolling buffers: [0:S] = previous S positions, [S:S+n] = current segment
    Kb = torch.zeros(S + SEG, d, dtype=torch.float16, device=dev)
    Yb = torch.zeros(S + SEG, dtype=torch.int64, device=dev)       # token at each position
    Pb = torch.zeros(S + SEG, dtype=torch.int64, device=dev)       # previous token (for constraints)
    PTb = torch.zeros(S + SEG, device=dev); ENb = torch.zeros(S + SEG, device=dev)
    lams = torch.tensor([0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8], device=dev)
    NB_E, NB_S = 12, 8
    acc = torch.zeros(NB_E * NB_S, len(lams), dtype=torch.float64, device=dev)
    state = {'seg0': 0, 'n': 0, 'have_hist': 0, 'bits_model': 0.0, 'bits_mix': 0.0}

    def flush():
        n = state['n']
        if n == 0:
            return
        hist = state['have_hist']
        Qn = F.normalize(Kb[:S + n].float(), dim=-1).half()
        pc_true = torch.zeros(n, device=dev); smax = torch.full((n,), -1.0, device=dev)
        Q = 2048
        for q0 in range(0, n, Q):
            q1 = min(n, q0 + Q)
            lo = max(S - hist, q0)                                   # first usable key (buffer index)
            sims = Qn[S + q0:S + q1].float() @ Qn[lo:S + q1].float().T
            kpos = torch.arange(lo, S + q1, device=dev)[None, :]
            qpos = torch.arange(S + q0, S + q1, device=dev)[:, None]
            sims = sims.masked_fill((kpos >= qpos) | (kpos < qpos - S), -1e4)
            tv, ti = sims.topk(min(64, sims.shape[1]), dim=-1)
            w = torch.softmax(tv / a.tau, -1) * (tv > -1e3)
            pc = torch.zeros(q1 - q0, V, device=dev).scatter_add_(1, Yb[lo + ti], w)
            pc = pc * allowed_mask(Pb[S + q0:S + q1][None], gsize, dev)[0]
            pc = pc / pc.sum(-1, keepdim=True).clamp_min(1e-9)
            pc_true[q0:q1] = pc.gather(1, Yb[S + q0:S + q1, None])[:, 0]
            smax[q0:q1] = torch.where(tv[:, 0] > -1e3, tv[:, 0].float(), torch.full_like(tv[:, 0].float(), -1.0))
        pt = PTb[S:S + n]
        bucket = torch.clamp((ENb[S:S + n] / 0.35).long(), 0, NB_E - 1) * NB_S + torch.clamp(((smax + 1) / 2 * NB_S).long(), 0, NB_S - 1)
        mix = torch.log2((1 - lams)[None] * pt[:, None] + lams[None] * pc_true[:, None] + 1e-12).double()
        state['bits_model'] += float(-pt.clamp_min(1e-12).log2().double().sum())
        for s0 in range(0, n, 4096):
            s1 = min(n, s0 + 4096)
            bk = bucket[s0:s1]
            ch = acc[bk].argmax(1)
            state['bits_mix'] += float(-mix[torch.arange(s0, s1, device=dev), ch].sum())
            acc.index_add_(0, bk, mix[s0:s1])
        # keep the last S positions as history for the next segment
        keep = min(S, S + n)
        for buf in (Kb, Yb, Pb, PTb, ENb):
            buf[:S] = buf[n:n + S].clone()
        state['have_hist'] = min(S, hist + n)
        state['n'] = 0

    last = max(0, nt - ctx)
    starts = sorted(set(list(range(0, last + 1, half)) + [last]))
    covered = 0
    with torch.no_grad():
        for i0 in range(0, len(starts), 48):
            sb = starts[i0:i0 + 48]
            prev = torch.stack([T[s:s + ctx] for s in sb]).to(dev)
            y = torch.stack([T[s + 1:s + 1 + ctx] for s in sb]).to(dev)
            with torch.autocast('cuda', torch.float16):
                h, lg = forward_states(model, prev)
            lg = lg.float().masked_fill(~allowed_mask(prev, gsize, dev), -1e30)
            lp = lg.log_softmax(-1)
            for j, s in enumerate(sb):
                end = min(s + ctx, nt)
                while end > covered:
                    room = SEG - state['n']
                    take = min(end - covered, room)
                    lo = covered - s
                    o = S + state['n']
                    Kb[o:o + take] = h[j, lo:lo + take].half()
                    Yb[o:o + take] = y[j, lo:lo + take]
                    Pb[o:o + take] = prev[j, lo:lo + take]
                    lpj = lp[j, lo:lo + take]
                    PTb[o:o + take] = lpj.gather(-1, y[j, lo:lo + take, None])[:, 0].exp()
                    ENb[o:o + take] = -(lpj.exp() * lpj.clamp_min(-1e4)).sum(-1)
                    state['n'] += take
                    covered += take
                    if state['n'] == SEG:
                        flush()
            if i0 % (48 * 1000) == 0:
                print({'windows': i0, 'of': len(starts), 'covered': covered, 'model_bits': round(state['bits_model']),
                       'mix_bits': round(state['bits_mix']), 'min': round((time.time() - t0) / 60, 1)}, flush=True)
    flush()
    n = 100_000_000 if not a.limit else None
    rep = {'run': a.run, 'tokens': nt, 'S': S, 'tau': a.tau, 'model_bits': state['bits_model'], 'cache_mix_bits': state['bits_mix'],
           'stored_bytes_entropy': stored, 'dictionary_bytes_xz': dict_bytes, 'minutes': round((time.time() - t0) / 60, 1)}
    if n:
        rep['enwik8_archive_bpb_model'] = state['bits_model'] / n
        rep['enwik8_archive_bpb_with_cache'] = state['bits_mix'] / n
        rep['enwik8_total_bytes_with_cache'] = state['bits_mix'] / 8 + stored + dict_bytes
        rep['enwik8_total_bpb_with_cache'] = rep['enwik8_total_bytes_with_cache'] * 8 / n
    (E4 / 'runs' / a.run / ('full_cache.json' if n else 'full_cache_debug.json')).write_text(json.dumps(rep, indent=1))
    print('FINAL', json.dumps(rep), flush=True)


if __name__ == '__main__':
    main()
