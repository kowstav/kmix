# Dump, for tokens of articles in stream order covering [A, B), the int8 quantized input of the
# unembedding (exactly what the C++ head sees), the target token, and position info.
# Output files (prefix): .xq (int8 N x 192), .tgt (uint8 N), .pos (int32 N: position in piece),
#   .row (int64 N: global stream index of the token whose distribution this is = predicted token index)
# usage: python dump_h.py A B prefix
import sys, numpy as np, torch
sys.path.insert(0, '/root/hp/tools')
import tfh
A, B, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
data = tfh.Data(); model = tfh.load_model(); dev = 'cuda'
U = model.unembedding
asc = U.quantize_activation.scale.detach().float().to(torch.bfloat16).float()
b = data.bounds
a0 = int(np.searchsorted(b, A, side='right') - 1); a1 = int(np.searchsorted(b, B - 1, side='right') - 1)
fx = open(out + '.xq', 'wb'); ft = open(out + '.tgt', 'wb'); fp = open(out + '.pos', 'wb'); fr = open(out + '.row', 'wb')
n = 0
with torch.no_grad():
    batch = []; blen = 0
    def flush():
        global batch, blen, n
        if not batch: return
        toks = np.concatenate([x[1] for x in batch]); pri = np.concatenate([x[2] for x in batch])
        cu = np.cumsum([0] + [len(x[1]) for x in batch]).astype(np.int32)
        h = model.compute_last_activation(torch.from_numpy(toks).to(dev)[None], torch.from_numpy(pri).to(dev)[None],
                                          torch.from_numpy(cu).to(dev)[None])[0].float()
        xq = torch.clamp(torch.round(h / asc), -128, 127).to(torch.int8).cpu().numpy()
        for i, (gs, t, _) in enumerate(batch):
            s, e = int(cu[i]), int(cu[i + 1]); L = e - s
            fx.write(xq[s:e - 1].tobytes()); ft.write(t[1:].astype(np.uint8).tobytes())
            fp.write(np.arange(L - 1, dtype=np.int32).tobytes())
            fr.write((gs + 1 + np.arange(L - 1, dtype=np.int64)).tobytes()); n += L - 1
        batch = []; blen = 0
    for a in range(a0, a1 + 1):
        s, e = int(b[a]), int(b[a + 1])
        if e > len(data.cnt): break
        t, P = data.article(a)
        for (ps, pe) in tfh.pieces_of(e - s):
            if pe - ps < 2: continue
            if blen + (pe - ps) > (1 << 17): flush()
            batch.append((s + ps, t[ps:pe], P[ps:pe])); blen += pe - ps
    flush()
for f in (fx, ft, fp, fr): f.close()
# head weights for the C simulator: dequantized unembedding (205x192 f32) and act scale
Wq = U.weight.detach().float(); ws = U.quantize_weight.scale.detach().float().to(torch.bfloat16).float()
Wd = (torch.clamp(torch.round(Wq / ws[:, None]), -7, 7) * ws[:, None]).cpu().numpy().astype(np.float32)
Wd.tofile(out + '.W'); np.array([float(asc)], np.float32).tofile(out + '.asc')
print('dumped', n, 'positions')
