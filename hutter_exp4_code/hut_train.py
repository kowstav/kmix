"""Contest-faithful arena: the model is trained on the very file it compresses (all of enwik8, test articles
included), as the Hutter Prize allows, with 4-bit weights so the shipped model has a realistic size.
Reports: bits per byte on the test articles (now seen data), on all of enwik8, and the total including the
model's entropy-coded weight bytes.
"""
import sys, math, json, time, argparse
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
from lm import LM, set_q, evaluate, storage_report

H = Path('/kaggle/working/hutter_lab')
E4 = H / 'exp4'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--d', type=int, default=288)
    ap.add_argument('--layers', type=int, default=6)
    ap.add_argument('--ctx', type=int, default=512)
    ap.add_argument('--bits', type=float, default=4)
    ap.add_argument('--steps', type=int, default=30000)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--lr', type=float, default=1.5e-3)
    ap.add_argument('--qat_start', type=float, default=0.5)
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--full_eval', action='store_true')
    a = ap.parse_args()
    dev = torch.device(f'cuda:{a.gpu}')
    out = E4 / 'runs' / a.name
    out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(0)
    raw = (H / 'data/enwik8').read_bytes()
    data = np.frombuffer(raw, np.uint8)
    tt = torch.as_tensor(data.astype(np.int64))
    test = (H / 'exp2/data/test.bin').read_bytes()
    model = LM(a.d, a.layers, a.ctx).to(dev)
    decay = [p for p in model.parameters() if p.dim() >= 2]
    nodecay = [p for p in model.parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{'params': decay, 'weight_decay': 0.05}, {'params': nodecay, 'weight_decay': 0.0}], lr=a.lr, betas=(0.9, 0.98))
    scaler = torch.amp.GradScaler('cuda')
    sched = lambda s: min(1.0, (s + 1) / 300) * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * min(1.0, s / a.steps))))
    rng = np.random.default_rng(0)
    t0 = time.time()
    hist = []
    for step in range(a.steps):
        if a.bits and step == int(a.qat_start * a.steps):
            set_q(model, a.bits)
        model.train()
        idx = rng.integers(0, len(data) - a.ctx - 1, size=a.batch)
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
        if step % 3000 == 0 or step == a.steps - 1:
            tb, _ = evaluate(model, test[:300_000], a.ctx, dev)
            row = {'step': step, 'epochs': round(step * a.batch * a.ctx / len(data), 2), 'train_bpb': float(loss.detach()) / math.log(2),
                   'test_slice_bpb_seen': tb, 'min': round((time.time() - t0) / 60, 1)}
            hist.append(row)
            print(row, flush=True)
    tb, cost = evaluate(model, test, a.ctx, dev)
    np.save(out / 'test_cost.npy', cost)
    st = storage_report(model, a.bits)
    rep = {'name': a.name, 'bits': a.bits, 'steps': a.steps, 'epochs': a.steps * a.batch * a.ctx / len(data), 'test_bpb_seen': tb,
           **st, 'history': hist, 'train_minutes': round((time.time() - t0) / 60, 1)}
    if a.full_eval:
        fb, _ = evaluate(model, raw, a.ctx, dev, batch=96)
        rep['enwik8_archive_bpb'] = fb
        rep['enwik8_total_bytes'] = fb * len(raw) / 8 + st['stored_bytes_entropy']
        rep['enwik8_total_bpb_incl_model'] = rep['enwik8_total_bytes'] * 8 / len(raw)
    torch.save({'cfg': model.cfg, 'bits': a.bits, 'state': model.state_dict()}, out / 'model.pt')
    (out / 'report.json').write_text(json.dumps(rep, indent=1))
    print('FINAL', json.dumps({k: v for k, v in rep.items() if k != 'history'}), flush=True)


if __name__ == '__main__':
    main()
