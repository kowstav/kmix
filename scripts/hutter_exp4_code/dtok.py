"""Dictionary-coded transformer: frequent words become two tokens (GROUP, MEMBER); which words share a group is
decided by the code assignment being tested. Everything else stays as bytes.

    schemes: freq | alpha | suffix | anagram | distrib
    vocab  : 256 bytes + 256 group tokens + 256 member tokens  (65,536 dictionary words)
Exact cost in bits per ORIGINAL byte on the held-out test, with the decoder's hard constraints:
    after GROUP g -> only members that exist in g;  after MEMBER -> a non-letter byte;
    after a letter byte -> no GROUP token (words are maximal letter runs).
Same architecture / optimiser / steps as the byte-level baseline (exp2/f288).
"""
import re, math, json, time, argparse, sys, pickle
from pathlib import Path
from collections import Counter
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
from lm import Block, pick_heads

DATA = Path('/kaggle/working/hutter_lab/exp2/data')
E4 = Path('/kaggle/working/hutter_lab/exp4')
W = re.compile(rb'[A-Za-z]+')
G, M = 256, 256
GB, MB = 256, 512          # first group token id, first member token id
V = 768
LETTER = np.zeros(V, bool)
LETTER[[c for c in range(256) if 65 <= c <= 90 or 97 <= c <= 122]] = True


def dictionary(train):
    cnt = Counter(W.findall(train))
    words = [w for w, _ in cnt.most_common(G * M)]
    return words, cnt


def distributional_order(words, train, dim=64, seed=0):
    """Words ordered by k-means cluster of their context vectors (SVD of PPMI with +-1 neighbours)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import svds
    idx = {w: i for i, w in enumerate(words)}
    toks = [idx.get(w, -1) for w in W.findall(train[:60_000_000])]
    t = np.array(toks, np.int64)
    rows, cols = [], []
    for off in (-1, 1):
        a = t[max(0, -off):len(t) - max(0, off)]
        b = t[max(0, off):len(t) - max(0, -off)]
        ok = (a >= 0) & (b >= 0)
        rows.append(a[ok]); cols.append(b[ok] + (0 if off < 0 else len(words)))
    r = np.concatenate(rows); c = np.concatenate(cols)
    mat = coo_matrix((np.ones(len(r), np.float32), (r, c)), shape=(len(words), 2 * len(words))).tocsr()
    tot = mat.sum()
    rs = np.asarray(mat.sum(1)).ravel() + 1e-9
    cs = np.asarray(mat.sum(0)).ravel() + 1e-9
    mat = mat.tocoo()
    pmi = np.log(mat.data * tot / (rs[mat.row] * cs[mat.col]))
    keep = pmi > 0
    ppmi = coo_matrix((pmi[keep], (mat.row[keep], mat.col[keep])), shape=mat.shape).tocsr()
    u, s, _ = svds(ppmi, k=dim)
    X = u * np.sqrt(s)
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    # balanced k-means (G clusters of at most M words): greedy capacity-constrained assignment
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(X), G, replace=False)]
    for _ in range(15):
        sim = X @ C.T
        lab = sim.argmax(1)
        C = np.stack([X[lab == k].mean(0) if (lab == k).any() else C[k] for k in range(G)])
        C /= np.linalg.norm(C, axis=1, keepdims=True) + 1e-9
    sim = X @ C.T
    order = np.argsort(-sim.max(1))            # most confident words choose first
    cap = np.zeros(G, int)
    lab = np.zeros(len(X), int)
    for i in order:
        for k in np.argsort(-sim[i]):
            if cap[k] < M:
                lab[i] = k; cap[k] += 1; break
    return [words[i] for i in np.lexsort((np.arange(len(words)), lab))]


def assign(words, scheme, train):
    if scheme == 'freq':
        order = words                                             # most frequent first: group = frequency band
    elif scheme == 'alpha':
        order = sorted(words, key=lambda w: (w.lower(), w))
    elif scheme == 'suffix':
        order = sorted(words, key=lambda w: (w.lower()[::-1], w))
    elif scheme == 'anagram':                                     # same multiset of letters together, then partial overlap
        order = sorted(words, key=lambda w: (bytes(sorted(w.lower())), len(w), w))
    elif scheme == 'distrib':
        order = distributional_order(words, train)
    else:
        raise ValueError(scheme)
    return {w: (i // M, i % M) for i, w in enumerate(order)}


def tokenize(raw, code):
    """-> tokens (uint16), first original byte of each token."""
    toks, orig = [], []
    last = 0
    for m in W.finditer(raw):
        a, b = m.span()
        for k in range(last, a):
            toks.append(raw[k]); orig.append(k)
        cg = code.get(m.group())
        if cg is None:
            for k in range(a, b):
                toks.append(raw[k]); orig.append(k)
        else:
            toks.append(GB + cg[0]); orig.append(a)
            toks.append(MB + cg[1]); orig.append(a)
        last = b
    for k in range(last, len(raw)):
        toks.append(raw[k]); orig.append(k)
    return np.array(toks, np.uint16), np.array(orig, np.int64)


class TokLM(nn.Module):
    def __init__(self, d=288, layers=6, ctx=512, charemb=False, words=None):
        super().__init__()
        h = pick_heads(d)
        self.cfg = dict(d=d, layers=layers, ctx=ctx, heads=h, charemb=charemb)
        self.charemb = charemb
        if charemb:
            # letter algebra: a decoded dictionary word is also fed as sums of letter vectors keyed by
            # position-from-start, position-from-end and no position (anagram invariant)
            L = 24
            lt = np.zeros((G * M, L), np.int64); ln = np.zeros(G * M, np.int64)
            for wi, w in enumerate(words):
                b = w[:L]
                lt[wi, :len(b)] = [1 + (c | 32) - 97 if 65 <= c <= 90 or 97 <= c <= 122 else 27 for c in b]
                ln[wi] = len(b)
            self.register_buffer('wl', torch.as_tensor(lt), persistent=False)
            self.register_buffer('wn', torch.as_tensor(ln), persistent=False)
            self.A = nn.Embedding(28 * L, d)
            self.Bm = nn.Embedding(28 * L, d)
            self.C = nn.Embedding(28, d)
            for e in (self.A, self.Bm, self.C):
                nn.init.normal_(e.weight, std=0.01)
        self.tok = nn.Embedding(V + 1, d)
        self.pos = nn.Embedding(ctx, d)
        self.blocks = nn.ModuleList([Block(d, h) for _ in range(layers)])
        self.norm = nn.LayerNorm(d)
        self.head = nn.Linear(d, V, bias=False)

    def letters(self, prev):
        """Extra input at positions whose input token is a MEMBER right after its GROUP (word now decoded)."""
        g = torch.cat([torch.full_like(prev[:, :1], -1), prev[:, :-1]], 1)
        is_w = (prev >= MB) & (prev < V) & (g >= GB) & (g < MB)
        wi = torch.where(is_w, (g - GB).clamp(0, G - 1) * M + (prev - MB).clamp(0, M - 1), torch.zeros_like(prev))
        lt = self.wl[wi]                                          # [B,T,24] letter ids (0 = pad)
        L = lt.shape[-1]
        pos = torch.arange(L, device=prev.device)
        n = self.wn[wi][..., None]
        rpos = (n - 1 - pos).clamp(0, L - 1)
        valid = (lt > 0)
        e = self.A(lt * L + pos) + self.Bm(lt * L + rpos) + self.C(lt)
        e = (e * valid[..., None]).sum(-2)
        return e * is_w[..., None]

    def forward(self, prev):
        h = self.tok(prev) + self.pos.weight[:prev.shape[1]]
        if self.charemb:
            h = h + self.letters(prev)
        for b in self.blocks:
            h = b(h)
        return self.head(self.norm(h))


def allowed_mask(prev, gsize, dev):
    """Decoder-known constraints for the token after `prev` (tensor of token ids)."""
    B_, T_ = prev.shape
    ok = torch.ones(B_, T_, V, dtype=torch.bool, device=dev)
    is_g = (prev >= GB) & (prev < MB)
    is_m = prev >= MB
    is_letter = torch.as_tensor(LETTER, device=dev)[prev.clamp_max(V - 1)] & (prev < 256)
    memb = torch.arange(M, device=dev)
    # after a group token: only members that exist in that group
    gs = torch.as_tensor(gsize, device=dev)[(prev - GB).clamp(0, G - 1)]
    mem_ok = memb[None, None, :] < gs[..., None]
    ok[..., :MB] &= ~is_g[..., None]
    ok[..., MB:] = torch.where(is_g[..., None], mem_ok, torch.zeros_like(mem_ok))
    # after a member token: a non-letter byte
    lettermask = torch.as_tensor(LETTER, device=dev)
    ok &= ~(is_m[..., None] & (lettermask[None, None, :] | (torch.arange(V, device=dev) >= 256)[None, None, :]))
    # after a letter byte: no group token
    grp = (torch.arange(V, device=dev) >= GB) & (torch.arange(V, device=dev) < MB)
    ok &= ~(is_letter[..., None] & grp[None, None, :])
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scheme', required=True)
    ap.add_argument('--steps', type=int, default=6000)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--ctx', type=int, default=512)
    ap.add_argument('--lr', type=float, default=1.5e-3)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--charemb', action='store_true')
    ap.add_argument('--tag', default='')
    ap.add_argument('--all', action='store_true', help='contest-faithful: train on ALL of enwik8 (test articles included)')
    ap.add_argument('--bits', type=float, default=0)
    ap.add_argument('--qat_start', type=float, default=0.5)
    ap.add_argument('--init', default='', help='warm start from runs/<init>/model.pt')
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    out = E4 / 'runs' / (f'dtok_{a.scheme}' + ('_ce' if a.charemb else '') + a.tag)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    train = (DATA / 'train.bin').read_bytes()
    test = (DATA / 'test.bin').read_bytes()
    cache = E4 / f'dtok_{a.scheme}.pkl'
    if cache.exists():
        code, tr_tok, te_tok, te_orig = pickle.loads(cache.read_bytes())
    else:
        words, _ = dictionary(train)
        code = assign(words, a.scheme, train)
        tr_tok, _ = tokenize(train, code)
        te_tok, te_orig = tokenize(test, code)
        cache.write_bytes(pickle.dumps((code, tr_tok, te_tok, te_orig)))
    if a.all:
        allp = E4 / f'dtok_{a.scheme}_allenwik8.npy'
        if allp.exists():
            tr_tok = np.load(allp)
        else:
            tr_tok, _ = tokenize((Path('/kaggle/working/hutter_lab/data/enwik8')).read_bytes(), code)
            np.save(allp, tr_tok)
    gsize = np.zeros(G, np.int64)
    for g, m in code.values():
        gsize[g] = max(gsize[g], m + 1)
    print(json.dumps({'scheme': a.scheme, 'train_tokens': len(tr_tok), 'tokens_per_byte_train': len(tr_tok) / len(train),
                      'prep_s': round(time.time() - t0)}), flush=True)
    T = torch.as_tensor(tr_tok.astype(np.int64))
    torch.manual_seed(a.seed)
    words_by_index = [None] * (G * M)
    for w, (g_, m_) in code.items():
        words_by_index[g_ * M + m_] = w
    words_by_index = [w if w is not None else b'' for w in words_by_index]
    model = TokLM(ctx=a.ctx, charemb=a.charemb, words=words_by_index).to(dev)
    if a.init:
        model.load_state_dict(torch.load(E4 / 'runs' / a.init / 'model.pt', map_location='cpu')['state'])
    decay = [p for p in model.parameters() if p.dim() >= 2]
    nodecay = [p for p in model.parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{'params': decay, 'weight_decay': 0.05}, {'params': nodecay, 'weight_decay': 0.0}], lr=a.lr, betas=(0.9, 0.98))
    scaler = torch.amp.GradScaler('cuda')
    sched = lambda s: min(1.0, (s + 1) / 200) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(1.0, s / a.steps))))
    rng = np.random.default_rng(a.seed)
    for step in range(a.steps):
        if a.bits and step == int(a.qat_start * a.steps):
            sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
            from lm import set_q
            set_q(model, a.bits)
        idx = rng.integers(1, len(T) - a.ctx - 1, size=a.batch)
        y = torch.stack([T[i:i + a.ctx] for i in idx]).to(dev)
        prev = torch.stack([T[i - 1:i - 1 + a.ctx] for i in idx]).to(dev)
        for g_ in opt.param_groups:
            g_['lr'] = a.lr * sched(step)
        with torch.autocast('cuda', torch.float16):
            loss = F.cross_entropy(model(prev).float().reshape(-1, V), y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()
        if step % 1000 == 0 or step == a.steps - 1:
            print({'step': step, 'train_nats_per_token': round(float(loss.detach()), 4), 'min': round((time.time() - t0) / 60, 1)}, flush=True)
    torch.save({'cfg': model.cfg, 'state': model.state_dict(), 'scheme': a.scheme}, out / 'model.pt')
    # ---- exact evaluation on held-out test ----
    model.eval()
    BOS = V
    Tt = torch.as_tensor(np.concatenate([[BOS], te_tok.astype(np.int64)]))
    nt = len(te_tok)
    cost_tok = np.zeros(nt, np.float32)
    ctx, half = a.ctx, a.ctx // 2
    last = max(0, nt - ctx)
    starts = sorted(set(list(range(0, last + 1, half)) + [last]))
    covered = 0
    with torch.no_grad():
        for i0 in range(0, len(starts), 48):
            sb = starts[i0:i0 + 48]
            prev = torch.stack([Tt[s:s + ctx] for s in sb]).to(dev)
            y = torch.stack([Tt[s + 1:s + 1 + ctx] for s in sb]).to(dev)
            with torch.autocast('cuda', torch.float16):
                lg = model(prev).float()
            lg = lg.masked_fill(~allowed_mask(prev, gsize, dev), -1e30)
            c = (-lg.log_softmax(-1).gather(-1, y[..., None])[..., 0] / math.log(2)).cpu().numpy()
            for j, s in enumerate(sb):
                end = min(s + ctx, nt)
                if end <= covered:
                    continue
                cost_tok[covered:end] = c[j, covered - s:end - s]
                covered = end
    n = len(test)
    cost_byte = np.zeros(n, np.float32)
    np.add.at(cost_byte, te_orig, cost_tok)
    np.save(out / 'test_cost.npy', cost_byte)
    rep = {'scheme': a.scheme, 'all_enwik8': a.all, 'bits': a.bits, 'steps': a.steps, 'params': sum(p.numel() for p in model.parameters()), 'test_bpb': float(cost_byte.mean()),
           'tokens_per_byte_test': nt / n, 'dict_word_share_of_test_tokens': float((te_tok >= GB).mean()),
           'train_minutes': round((time.time() - t0) / 60, 1)}
    if a.bits:
        from lm import storage_report
        rep.update(storage_report(model, a.bits))
    (out / 'report.json').write_text(json.dumps(rep, indent=1))
    print('FINAL', json.dumps(rep), flush=True)


if __name__ == '__main__':
    main()
