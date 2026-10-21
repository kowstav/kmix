"""Contest-faithful total for a dictionary-coded model trained on all of enwik8:
archive = model-alone code length of every enwik8 token (shipped quantized weights, decoder-known constraints),
plus stored weights (entropy of the codes) plus the dictionary (xz). Miners are not included here.
usage: dtok_full_eval.py --run dtok_distrib_ce_hut_q4 --scheme distrib --bits 4
"""
import sys, json, time, argparse, pickle, lzma, math
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0, '/kaggle/working/hutter_lab/exp4')
sys.path.insert(0, '/kaggle/working/hutter_lab/exp2')
from dtok import TokLM, allowed_mask, V, G, M
from full_tok import ship, ship_bytes
from lm import storage_report, set_q

E4 = Path('/kaggle/working/hutter_lab/exp4')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', required=True)
    ap.add_argument('--scheme', default='distrib')
    ap.add_argument('--bits', type=int, default=4)
    ap.add_argument('--gpu', type=int, default=0)
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
    st = storage_report(model, a.bits)
    st['stored_bytes_entropy_16bit_tables'] = st['stored_bytes_entropy']
    st['stored_bytes_entropy'] = ship_bytes(model, a.bits)
    ship(model, a.bits)
    model.eval()
    dict_bytes = len(lzma.compress(b'\n'.join(words), preset=9 | lzma.PRESET_EXTREME))
    tok = np.load(E4 / f'dtok_{a.scheme}_allenwik8.npy').astype(np.int64)
    nt = len(tok)
    T = torch.as_tensor(np.concatenate([[V], tok]))
    ctx, half = model.cfg['ctx'], model.cfg['ctx'] // 2
    last = max(0, nt - ctx)
    starts = sorted(set(list(range(0, last + 1, half)) + [last]))
    covered = 0
    bits = 0.0
    with torch.no_grad():
        for i0 in range(0, len(starts), 48):
            sb = starts[i0:i0 + 48]
            prev = torch.stack([T[s:s + ctx] for s in sb]).to(dev)
            y = torch.stack([T[s + 1:s + 1 + ctx] for s in sb]).to(dev)
            with torch.autocast('cuda', torch.float16):
                lg = model(prev).float()
            lg = lg.masked_fill(~allowed_mask(prev, gsize, dev), -1e30)
            c = (-lg.log_softmax(-1).gather(-1, y[..., None])[..., 0] / math.log(2))
            for j, s in enumerate(sb):
                end = min(s + ctx, nt)
                if end <= covered:
                    continue
                bits += float(c[j, covered - s:end - s].double().sum())
                covered = end
            if i0 % (48 * 500) == 0:
                print({'windows': i0, 'of': len(starts), 'min': round((time.time() - t0) / 60, 1)}, flush=True)
    n = 100_000_000
    total = bits / 8 + st['stored_bytes_entropy'] + dict_bytes
    rep = {'run': a.run, 'enwik8_tokens': nt, 'enwik8_archive_bpb': bits / n, **st, 'dictionary_bytes_xz': dict_bytes,
           'enwik8_total_bytes': total, 'enwik8_total_bpb_incl_model_and_dict': total * 8 / n,
           'minutes': round((time.time() - t0) / 60, 1)}
    (E4 / 'runs' / a.run / 'full_eval.json').write_text(json.dumps(rep, indent=1))
    print('FINAL', json.dumps(rep), flush=True)


if __name__ == '__main__':
    main()
