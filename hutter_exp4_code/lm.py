"""Byte-level causal transformer with optional quantisation-aware training (QAT).

bits: 0 = float; 4 = int4 (levels -7..7, absmax scale per row); 3 = int3 (-3..3);
      1.58 = ternary (-1, 0, +1, absmean scale per row, BitNet-style).
All Linear layers in the blocks and the output head are quantised; embeddings are counted at 8 bits.
"""
import math, json, time, argparse
from pathlib import Path
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

ROOT = Path('/kaggle/working/hutter_lab/exp2')


def quant_params(w, bits):
    if bits < 2:  # ternary
        return w.detach().abs().mean(1, keepdim=True).clamp_min(1e-8), 1
    q = (1 << (int(bits) - 1)) - 1
    return w.detach().abs().amax(1, keepdim=True).clamp_min(1e-8) / q, q


class QLinear(nn.Linear):
    qbits = 0

    def qweight(self):
        w = self.weight
        if not self.qbits:
            return w
        s, q = quant_params(w, self.qbits)
        z = (w / s).round().clamp(-q, q) * s
        return w + (z - w).detach()  # straight-through estimator

    def codes(self):
        s, q = quant_params(self.weight, self.qbits)
        return (self.weight.detach() / s).round().clamp(-q, q).to(torch.int8), s

    def forward(self, x):
        return F.linear(x, self.qweight(), self.bias)


class Block(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.h = h
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.qkv = QLinear(d, 3 * d, bias=False)
        self.proj = QLinear(d, d, bias=False)
        self.up = QLinear(d, 4 * d, bias=False)
        self.down = QLinear(4 * d, d, bias=False)

    def forward(self, x):
        b, t, d = x.shape
        q, k, v = self.qkv(self.n1(x)).view(b, t, 3, self.h, d // self.h).permute(2, 0, 3, 1, 4)
        a = F.scaled_dot_product_attention(q, k, v, is_causal=True).transpose(1, 2).reshape(b, t, d)
        x = x + self.proj(a)
        return x + self.down(F.relu(self.up(self.n2(x))).square())


def pick_heads(d):
    for hd in (64, 72, 56, 48, 80, 96):
        if d % hd == 0:
            return d // hd
    return 1


class LM(nn.Module):
    def __init__(self, d=288, layers=6, ctx=512):
        super().__init__()
        h = pick_heads(d)
        self.cfg = dict(d=d, layers=layers, ctx=ctx, heads=h)
        self.tok = nn.Embedding(256, d)
        self.pos = nn.Embedding(ctx, d)
        self.blocks = nn.ModuleList([Block(d, h) for _ in range(layers)])
        self.norm = nn.LayerNorm(d)
        self.head = QLinear(d, 256, bias=False)

    def forward(self, x):
        h = self.tok(x) + self.pos.weight[: x.shape[1]]
        for b in self.blocks:
            h = b(h)
        return self.head(self.norm(h))


def set_q(model, bits):
    for m in model.modules():
        if isinstance(m, QLinear):
            m.qbits = bits


def storage_report(model, bits):
    """Nominal size and empirical-entropy size of the weights as they would be shipped."""
    qnames = {n + '.weight' for n, m in model.named_modules() if isinstance(m, QLinear)}
    nominal = entropy = 0.0
    qparams = other = 0
    for n, m in model.named_modules():
        if not isinstance(m, QLinear):
            continue
        qparams += m.weight.numel()
        if bits:
            c, s = m.codes()
            c = c.flatten().cpu().numpy().astype(np.int64)
            levels = 3 if bits < 2 else 2 * ((1 << (int(bits) - 1)) - 1) + 1
            cnt = np.bincount(c - c.min()).astype(float)
            p = cnt[cnt > 0] / cnt.sum()
            nominal += c.size * math.log2(levels) + s.numel() * 16
            entropy += c.size * float(-(p * np.log2(p)).sum()) + s.numel() * 16
        else:
            nominal += m.weight.numel() * 16
            entropy += m.weight.numel() * 16
    for n, p in model.named_parameters():
        if n in qnames:
            continue
        other += p.numel()
        bitsper = 8 if n.startswith(('tok', 'pos')) else 16
        nominal += p.numel() * bitsper
        entropy += p.numel() * bitsper
    return dict(params_quantised=qparams, params_other=other,
                stored_bytes_nominal=int(nominal / 8), stored_bytes_entropy=int(entropy / 8))


@torch.no_grad()
def evaluate(model, data, ctx, dev, stride=None, save_probs=None, batch=64):
    """Sliding-window evaluation. Every byte after the first window sees >= ctx - stride bytes of context.
    Returns (bits per byte, per-byte cost in bits)."""
    model.eval()
    stride = stride or ctx // 2
    n = len(data)
    arr = torch.as_tensor(np.frombuffer(data, np.uint8).astype(np.int64))
    cost = np.full(n, 8.0, np.float32)
    probs = np.lib.format.open_memmap(save_probs, 'w+', np.float16, (n, 256)) if save_probs else None
    if probs is not None:
        probs[0] = 1 / 256
    last = max(0, n - ctx - 1)
    starts = sorted(set(list(range(0, last + 1, stride)) + [last]))
    covered = 1  # next target index not yet scored
    for i in range(0, len(starts), batch):
        sb = starts[i:i + batch]
        x = torch.stack([arr[s:s + ctx + 1] for s in sb]).to(dev)
        with torch.autocast('cuda', torch.float16):
            lg = model(x[:, :-1]).float()
        lp = lg.log_softmax(-1)
        c = (-lp.gather(-1, x[:, 1:, None])[..., 0] / math.log(2)).cpu().numpy()
        for j, s in enumerate(sb):
            end = min(s + ctx, n - 1)  # last target index in this window
            if end < covered:
                continue
            lo, hi = covered - s - 1, end - s
            cost[covered:end + 1] = c[j, lo:hi]
            if probs is not None:
                probs[covered:end + 1] = lp[j, lo:hi].exp().half().cpu().numpy()
            covered = end + 1
    if probs is not None:
        probs.flush()
    return float(cost.mean()), cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--d', type=int, default=288)
    ap.add_argument('--layers', type=int, default=6)
    ap.add_argument('--ctx', type=int, default=512)
    ap.add_argument('--bits', type=float, default=0)
    ap.add_argument('--steps', type=int, default=4000)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--lr', type=float, default=1.5e-3)
    ap.add_argument('--qat_start', type=float, default=0.4)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--save_probs', action='store_true')
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()

    out = ROOT / 'runs' / a.name
    out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(a.seed)
    dev = torch.device(f'cuda:{a.gpu}')
    train = np.frombuffer((ROOT / 'data/train.bin').read_bytes(), np.uint8)
    valid = (ROOT / 'data/valid.bin').read_bytes()
    test = (ROOT / 'data/test.bin').read_bytes()
    tt = torch.as_tensor(train.astype(np.int64))

    model = LM(a.d, a.layers, a.ctx).to(dev)
    decay = [p for p in model.parameters() if p.dim() >= 2]
    nodecay = [p for p in model.parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{'params': decay, 'weight_decay': 0.05}, {'params': nodecay, 'weight_decay': 0.0}],
                            lr=a.lr, betas=(0.9, 0.98))
    scaler = torch.amp.GradScaler('cuda')
    warm = 200

    def sched(s):
        return min(1.0, (s + 1) / warm) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(1.0, s / a.steps))))

    rng = np.random.default_rng(a.seed)
    hist = []
    t0 = time.time()
    print(json.dumps({'name': a.name, **model.cfg, 'bits': a.bits,
                      'params': sum(p.numel() for p in model.parameters())}), flush=True)
    for step in range(a.steps):
        if a.bits and step == int(a.qat_start * a.steps):
            set_q(model, a.bits)
            print('QAT on at step', step, flush=True)
        model.train()
        idx = rng.integers(0, len(train) - a.ctx - 1, size=a.batch)
        x = torch.stack([tt[i:i + a.ctx + 1] for i in idx]).to(dev, non_blocking=True)
        for g in opt.param_groups:
            g['lr'] = a.lr * sched(step)
        with torch.autocast('cuda', torch.float16):
            loss = F.cross_entropy(model(x[:, :-1]).float().reshape(-1, 256), x[:, 1:].reshape(-1))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()
        if step % 500 == 0 or step == a.steps - 1:
            vb, _ = evaluate(model, valid[:300_000], a.ctx, dev)
            row = {'step': step, 'train_bpb': float(loss) / math.log(2), 'valid_bpb': vb,
                   'min': round((time.time() - t0) / 60, 2)}
            hist.append(row)
            print(row, flush=True)

    tb, cost = evaluate(model, test, a.ctx, dev, save_probs=str(out / 'test_probs.npy') if a.save_probs else None)
    np.save(out / 'test_cost.npy', cost)
    rep = {'name': a.name, **model.cfg, 'bits': a.bits, 'steps': a.steps, 'tokens_seen': a.steps * a.batch * a.ctx,
           'params': sum(p.numel() for p in model.parameters()), 'test_bpb': tb, 'test_bytes': len(test),
           'train_minutes': round((time.time() - t0) / 60, 1), **storage_report(model, a.bits), 'history': hist,
           'scope': 'held-out enwik8 articles; stricter than the contest, where the model trains on the file it compresses'}
    (out / 'report.json').write_text(json.dumps(rep, indent=2))
    torch.save({'cfg': model.cfg, 'bits': a.bits, 'state': model.state_dict()}, out / 'model.pt')
    print('FINAL', json.dumps({k: v for k, v in rep.items() if k != 'history'}), flush=True)


if __name__ == '__main__':
    main()
