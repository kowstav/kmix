# Loss impact of storing the non-quantized float32 parameters at reduced precision.
import sys, json, numpy as np, torch
sys.path.insert(0, '/root/hp/tools')
import tfh
data = tfh.Data(); model = tfh.load_model()
base_sd = torch.load(tfh.REPO + '/models/6m-q4-fp32.tch', map_location='cpu')
arts = []; tot = 0
for a in range(0, data.n_art_avail, 7):
    arts.append(a); tot += int(data.bounds[a + 1] - data.bounds[a])
    if tot > 2_000_000: break
def is_float_param(k, sd):
    if 'scale' in k: return False
    if k.endswith('.weight') and (k[:-7] + '.quantize_weight.scale') in sd: return False
    return True
fkeys = [k for k in base_sd if is_float_param(k, base_sd)]
print('float params', sum(base_sd[k].numel() for k in fkeys), [ (k, tuple(base_sd[k].shape)) for k in fkeys[:12]])
def mant_round(x, bits):  # round fp32 mantissa to `bits` bits (round-to-nearest-even via torch for bf16/fp16)
    if bits == 7: return x.to(torch.bfloat16).float()
    if bits == 10: return x.to(torch.float16).float()
    m, e = torch.frexp(x); s = 2.0 ** (bits + 1)
    return torch.ldexp(torch.round(m * s) / s, e)
def loss():
    r = tfh.eval_articles(model, data, arts); t = sum(float(v.sum()) for v in r.values()); n = sum(len(v) for v in r.values())
    return t / n
res = {}
for bits in [None, 10, 7, 5, 4]:
    sd = {k: v.clone() for k, v in base_sd.items()}
    if bits is not None:
        for k in fkeys: sd[k] = mant_round(sd[k].float(), bits)
    model.load_state_dict(sd)
    L = loss(); res[str(bits)] = L
    print(json.dumps(dict(bits=bits, loss=L, rel=(L / res['None'] - 1) * 100 if 'None' in res else 0))); sys.stdout.flush()
