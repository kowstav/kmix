# Adaptive code-length estimates (bytes) for the int4 weights under different contexts.
# Sequential KT-like estimator with count halving, i.e. what a decoder can achieve.
import torch, numpy as np, math, sys
sd = torch.load('/root/hp/src/fx2-cmix-transformer-v1/models/6m-q4-fp32.tch', map_location='cpu')
def bf16(x): return x.to(torch.bfloat16).to(torch.float32)
tens = []
for k, v in sd.items():
    if not k.endswith('.weight'): continue
    sk = k[:-7] + '.quantize_weight.scale'
    if sk not in sd: continue
    W = v.float(); s = bf16(sd[sk].float())
    q = torch.clamp(torch.round(W / s[:, None]), -7, 7).to(torch.int64).numpy() + 7  # 0..14
    tens.append((k, q, s.numpy()))
N = sum(q.size for _, q, _ in tens)
print('weights', N)

def code(ctx_fn, alpha=0.5, limit=1 << 16, scope='global'):
    """ctx_fn(tensor_idx, q, r, c) -> context id (hashable int); adaptive per context counts."""
    total = 0.0
    tables = {}
    for ti, (name, q, s) in enumerate(tens):
        if scope == 'tensor': tables = {}
        R, C = q.shape
        for r in range(R):
            for c in range(C):
                cx = ctx_fn(ti, q, r, c)
                t = tables.get(cx)
                if t is None:
                    t = tables[cx] = np.full(15, alpha); tables[cx + (1 << 40) if isinstance(cx, int) else ('tot', cx)] = None
                    t_tot = None
                sym = q[r, c]
                tot = t.sum()
                total -= math.log2(t[sym] / tot)
                t[sym] += 1
                if tot > limit: t *= 0.5
    return total / 8

# vectorised versions for speed: process tensor by tensor with numpy where possible
def adaptive_bytes(seq_ctx, seq_sym, nctx, alpha=0.4, limit=4096):
    """seq_ctx: int array of contexts (0..nctx-1), seq_sym: symbols 0..14; sequential adaptive cost in bytes"""
    cnt = np.full((nctx, 15), alpha); tot = np.full(nctx, alpha * 15)
    bits = 0.0
    for cx, sy in zip(seq_ctx.tolist(), seq_sym.tolist()):
        bits -= math.log2(cnt[cx, sy] / tot[cx])
        cnt[cx, sy] += 1; tot[cx] += 1
        if tot[cx] > limit:
            cnt[cx] *= 0.5; tot[cx] *= 0.5
    return bits / 8

res = {}
syms = np.concatenate([q.ravel() for _, q, _ in tens])
# 1) global adaptive
res['global'] = adaptive_bytes(np.zeros(len(syms), np.int64), syms, 1, limit=1 << 20)
# 2) per tensor
ctx = np.concatenate([np.full(q.size, i) for i, (_, q, _) in enumerate(tens)])
res['tensor'] = adaptive_bytes(ctx, syms, len(tens), limit=1 << 20)
# 3) per tensor x |prev weight in row| bucket (0..7)
cx = []
for i, (_, q, _) in enumerate(tens):
    prev = np.zeros_like(q); prev[:, 1:] = np.abs(q[:, :-1] - 7)
    cx.append(i * 8 + prev.ravel())
res['tensor_prevabs'] = adaptive_bytes(np.concatenate(cx), syms, len(tens) * 8, limit=1 << 20)
# 4) per tensor x column (input channel)
cx = []; off = 0
for i, (_, q, _) in enumerate(tens):
    R, C = q.shape
    cx.append(off + np.tile(np.arange(C), R)); off += C
res['tensor_col'] = adaptive_bytes(np.concatenate(cx), syms, off, limit=1 << 20)
# 5) per tensor x |weight above| (same column, previous row)
cx = []
for i, (_, q, _) in enumerate(tens):
    up = np.zeros_like(q); up[1:, :] = np.abs(q[:-1, :] - 7)
    cx.append(i * 8 + up.ravel())
res['tensor_upabs'] = adaptive_bytes(np.concatenate(cx), syms, len(tens) * 8, limit=1 << 20)
# 6) per tensor x row-scale bucket (relative to tensor median scale)
cx = []
for i, (_, q, s) in enumerate(tens):
    rel = np.abs(s) / np.median(np.abs(s)); b = np.clip(np.floor(np.log2(rel + 1e-9) * 2) + 4, 0, 7).astype(np.int64)
    cx.append(i * 8 + np.repeat(b, q.shape[1]))
res['tensor_scale'] = adaptive_bytes(np.concatenate(cx), syms, len(tens) * 8, limit=1 << 20)
for k, v in res.items():
    print(f'{k:16s} {v:12.0f} bytes  {v * 8 / N:.4f} bits/w')
