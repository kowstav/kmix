# Cross-article context test (no fine-tuning): evaluate consecutive articles as ONE sequence
# (no state reset at article boundaries) vs the standard per-article reset. Loss is compared
# per position-in-article bucket. Sequences are capped at 2^16 tokens (several articles).
import sys, json, numpy as np, torch
sys.path.insert(0, '/root/hp/tools')
import tfh
data = tfh.Data(); model = tfh.load_model(); dev = 'cuda'
b = data.bounds
start_art = int(sys.argv[1]) if len(sys.argv) > 1 else 1
NTOK = int(sys.argv[2]) if len(sys.argv) > 2 else 2_000_000
SEQ = 1 << 16
# collect groups of consecutive whole articles, each group <= SEQ tokens
groups = []; cur = []; cl = 0; tot = 0; a = start_art
while tot < NTOK and a < data.n_art_avail:
    L = int(b[a + 1] - b[a])
    if L >= SEQ: a += 1; continue
    if cl + L > SEQ: groups.append(cur); cur = []; cl = 0
    cur.append(a); cl += L; tot += L; a += 1
if cur: groups.append(cur)
edges = [0, 1, 4, 16, 64, 256, 1024, 4096, 1 << 30]
acc = {m: np.zeros(len(edges) - 1) for m in ['reset', 'carry']}; cnt = np.zeros(len(edges) - 1)
with torch.no_grad():
    for g in groups:
        ts, Ps, lens = [], [], []
        for a in g:
            t, P = data.article(a); ts.append(t); Ps.append(P); lens.append(len(t))
        toks = np.concatenate(ts); pri = np.concatenate(Ps)
        x = torch.from_numpy(toks).to(dev)[None]; p = torch.from_numpy(pri).to(dev)[None]
        for mode in ['reset', 'carry']:
            cu = np.cumsum([0] + lens) if mode == 'reset' else np.array([0, len(toks)])
            cuq = torch.from_numpy(cu.astype(np.int32)).to(dev)[None]
            lp = torch.log_softmax(model.compute_logits(x, p, cuq)[0].float(), -1)
            tgt = torch.from_numpy(toks[1:]).to(dev)
            l = (-lp[:-1].gather(1, tgt[:, None])[:, 0]).cpu().numpy()
            # attribute losses to (article, position) of the predicted token; skip predictions of
            # each article's first token (in reset mode that is the PPMD's job; compare only shared positions)
            off = 0
            for a, L in zip(g, lens):
                # predicted tokens off+1 .. off+L-1 (positions 1..L-1 within the article)
                seg = l[off:off + L - 1]
                pos = np.arange(1, L)
                for k in range(len(edges) - 1):
                    m = (pos >= edges[k]) & (pos < edges[k + 1])
                    acc[mode][k] += seg[m].sum()
                    if mode == 'reset': cnt[k] += m.sum()
                off += L
for k in range(len(edges) - 1):
    if cnt[k]:
        r, c = acc['reset'][k] / cnt[k], acc['carry'][k] / cnt[k]
        print(f'pos [{edges[k]},{edges[k+1]}) n={int(cnt[k])} reset {r:.4f} carry {c:.4f} rel {100*(c/r-1):+.2f}%')
R, C = acc['reset'].sum() / cnt.sum(), acc['carry'].sum() / cnt.sum()
print(f'ALL n={int(cnt.sum())} reset {R:.5f} carry {C:.5f} rel {100*(C/R-1):+.3f}%')
