# Transformer probabilities for an arbitrary (WRT-encoded) slice treated as ONE chunk
# (pieces of 2^17 tokens, like the real tail). Priors from a cold-start PPMD run:
#   prefix.cnt/.idx/.val (sparsify output of --save-ppmd-probs on prefix.bin).
# Writes prefix.probs.f16 in --load-transformer-probs format.
# usage: python slicepipe.py prefix
import sys, numpy as np, torch
sys.path.insert(0, '/root/hp/tools'); import tfh
P = sys.argv[1]; V = 205
vocab = np.fromfile('/root/hp/data/vocab.list', dtype=np.uint8)
inv = np.full(256, -1, np.int64); inv[vocab] = np.arange(len(vocab))
raw = np.fromfile(P + '.bin', dtype=np.uint8); tok = inv[raw]; assert (tok >= 0).all()
N = len(tok)
cnt = np.fromfile(P + '.cnt', dtype=np.uint8).astype(np.int64); assert len(cnt) == N, (len(cnt), N)
idx = np.fromfile(P + '.idx', dtype=np.uint8).astype(np.int64); val = np.fromfile(P + '.val', dtype=np.float16).astype(np.float32)
off = np.concatenate([[0], np.cumsum(cnt)])
model = tfh.load_model(); dev = 'cuda'
probs = np.zeros((N, V), np.float16)
with torch.no_grad():
    for (s, e) in tfh.pieces_of(N):
        Pr = np.zeros((e - s, V), np.float32)
        rows = np.repeat(np.arange(e - s), cnt[s:e]); Pr[rows, idx[off[s]:off[e]]] = val[off[s]:off[e]]
        lg = model.compute_logits(torch.from_numpy(tok[s:e]).to(dev)[None], torch.from_numpy(Pr).to(dev)[None],
                                  torch.tensor([[0, e - s]], dtype=torch.int32, device=dev))[0].float()
        probs[s:e - 1] = torch.softmax(lg, -1).to(torch.float16).cpu().numpy()[:-1]
        probs[e - 1] = Pr[e - 1 - s].astype(np.float16)
probs.tofile(P + '.probs.f16')
print('wrote', P, N)
