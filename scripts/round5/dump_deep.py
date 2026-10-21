# Dump for deeper online-adaptation simulation (block 11 MLP down + head):
#   .x12 f32 [N,192] residual stream after block 11 (input of final rms_norm)
#   .hq  u8  [N,768] int8-quantized input of blocks[11].mlp.down (relu^2 output, >=0)
#   plus .tgt/.pos/.row like dump_h, and weights: .Wd (192x768 dequant f32), .hsc (scale), .Wu/.asc
# usage: python dump_deep.py A B prefix
import sys, numpy as np, torch
sys.path.insert(0, '/root/hp/tools')
import tfh
A, B, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
data = tfh.Data(); model = tfh.load_model(); dev = 'cuda'
def bf(x): return x.detach().float().to(torch.bfloat16).float()
down = model.blocks[11].mlp.down
hsc = bf(down.quantize_activation.scale)
cap = {}
h1 = down.register_forward_pre_hook(lambda m, inp: cap.__setitem__('h', inp[0].detach()))
h2 = model.blocks[11].register_forward_hook(lambda m, inp, o: cap.__setitem__('x12', o.detach()))
b = data.bounds
a0 = int(np.searchsorted(b, A, side='right') - 1); a1 = int(np.searchsorted(b, B - 1, side='right') - 1)
f = {k: open(out + '.' + k, 'wb') for k in ['x12', 'hq', 'tgt', 'pos', 'row']}
n = 0
with torch.no_grad():
    batch = []; blen = 0
    def flush():
        global batch, blen, n
        if not batch: return
        toks = np.concatenate([x[1] for x in batch]); pri = np.concatenate([x[2] for x in batch])
        cu = np.cumsum([0] + [len(x[1]) for x in batch]).astype(np.int32)
        model.compute_last_activation(torch.from_numpy(toks).to(dev)[None], torch.from_numpy(pri).to(dev)[None],
                                      torch.from_numpy(cu).to(dev)[None])
        hq = torch.clamp(torch.round(cap['h'][0].float() / hsc), -128, 127).to(torch.uint8).cpu().numpy()
        x12 = cap['x12'][0].float().cpu().numpy()
        for i, (gs, t, _) in enumerate(batch):
            s, e = int(cu[i]), int(cu[i + 1]); L = e - s
            f['x12'].write(x12[s:e - 1].tobytes()); f['hq'].write(hq[s:e - 1].tobytes())
            f['tgt'].write(t[1:].astype(np.uint8).tobytes()); f['pos'].write(np.arange(L - 1, dtype=np.int32).tobytes())
            f['row'].write((gs + 1 + np.arange(L - 1, dtype=np.int64)).tobytes()); n += L - 1
        batch = []; blen = 0
    for a in range(a0, a1 + 1):
        s, e = int(b[a]), int(b[a + 1])
        if e > len(data.cnt): break
        t, P = data.article(a)
        for (ps, pe) in tfh.pieces_of(e - s):
            if pe - ps < 2: continue
            if blen + (pe - ps) > (1 << 16): flush()
            batch.append((s + ps, t[ps:pe], P[ps:pe])); blen += pe - ps
    flush()
for x in f.values(): x.close()
Wq = down.weight.detach().float(); ws = bf(down.quantize_weight.scale)
Wd = (torch.clamp(torch.round(Wq / ws[:, None]), -7, 7) * ws[:, None]).cpu().numpy().astype(np.float32)
Wd.tofile(out + '.Wd'); np.array([float(hsc)], np.float32).tofile(out + '.hsc')
U = model.unembedding
Wq = U.weight.detach().float(); ws = bf(U.quantize_weight.scale)
(torch.clamp(torch.round(Wq / ws[:, None]), -7, 7) * ws[:, None]).cpu().numpy().astype(np.float32).tofile(out + '.Wu')
np.array([float(bf(U.quantize_activation.scale))], np.float32).tofile(out + '.asc')
print('dumped', n)
