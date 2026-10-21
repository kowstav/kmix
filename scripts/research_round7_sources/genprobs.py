# Generate a --load-transformer-probs file (float16, V=205 per row) for tokens [A, B)
# of the post-WRT stream, reproducing predictor.cpp TransformerByteUpdate semantics:
#   row k (k in [A,B)) = distribution for token k+1;
#   if token k is the last token of its piece (article chunk end or 2^17 cut) -> PPMD prior row k
#   else -> transformer softmax output at token k (full in-piece context, as in a full run).
# Also writes the bytes slice (vocab[tok[A:B]]) for the lab compressor.
# usage: python genprobs.py A B out_prefix [ckpt]
import sys, numpy as np, torch
sys.path.insert(0, '/root/hp/tools')
import tfh

A, B, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
ckpt = sys.argv[4] if len(sys.argv) > 4 else tfh.REPO + '/models/6m-q4-fp32.tch'
data = tfh.Data()
vocab = np.fromfile('/root/hp/data/vocab.list', dtype=np.uint8)
assert B <= len(data.cnt), 'priors not yet available for this range'
model = tfh.load_model(ckpt)
dev = 'cuda'
V = 205
probs = np.zeros((B - A, V), dtype=np.float16)
filled = np.zeros(B - A, dtype=bool)
b = data.bounds
a0 = int(np.searchsorted(b, A, side='right') - 1)
a1 = int(np.searchsorted(b, B - 1, side='right') - 1)

def prior_rows(lo, hi):
    """dense prior rows lo..hi-1 as float32"""
    c = np.asarray(data.cnt[lo:hi], dtype=np.int64)
    # entry offset of row lo: article offset + partial sum
    a = int(np.searchsorted(b, lo, side='right') - 1)
    off = int(data.boff[a]) + int(np.asarray(data.cnt[b[a]:lo], dtype=np.int64).sum())
    n = int(c.sum())
    ii = np.asarray(data.idx[off:off + n], dtype=np.int64)
    vv = np.asarray(data.val[off:off + n], dtype=np.float32)
    P = np.zeros((hi - lo, V), np.float32)
    P[np.repeat(np.arange(hi - lo), c), ii] = vv
    return P

with torch.no_grad():
    batch = []; blen = 0
    def flush():
        global batch, blen
        if not batch: return
        toks = np.concatenate([x[1] for x in batch]); pri = np.concatenate([x[2] for x in batch])
        cu = np.cumsum([0] + [len(x[1]) for x in batch]).astype(np.int32)
        lg = model.compute_logits(torch.from_numpy(toks).to(dev)[None], torch.from_numpy(pri).to(dev)[None],
                                  torch.from_numpy(cu).to(dev)[None])[0].float()
        pr = torch.softmax(lg, -1).to(torch.float16).cpu().numpy()
        for i, (gs, t, _) in enumerate(batch):
            s, e = int(cu[i]), int(cu[i + 1])
            # rows gs .. gs+L-2 come from transformer positions 0..L-2
            for_rows = np.arange(gs, gs + (e - s) - 1)
            sel = (for_rows >= A) & (for_rows < B)
            probs[for_rows[sel] - A] = pr[s:e - 1][sel]
            filled[for_rows[sel] - A] = True
        batch = []; blen = 0
    for a in range(a0, a1 + 1):
        s, e = int(b[a]), int(b[a + 1])
        t = np.asarray(data.tok[s:e], dtype=np.int64)
        P = prior_rows(s, e)
        for (ps, pe) in tfh.pieces_of(e - s):
            if pe - ps >= 2 and (s + pe - 2) >= A and (s + ps) < B:
                if blen + (pe - ps) > (1 << 17):
                    flush()
                batch.append((s + ps, t[ps:pe], P[ps:pe])); blen += pe - ps
            # last token of the piece -> PPMD prior row
            k = s + pe - 1
            if A <= k < B:
                probs[k - A] = P[pe - 1].astype(np.float16); filled[k - A] = True
    flush()
assert filled.all(), f'unfilled rows: {(~filled).sum()}'
probs.tofile(out + '.probs.f16')
vocab[np.asarray(data.tok[A:B])].tofile(out + '.bin')
print('wrote', out, B - A)
