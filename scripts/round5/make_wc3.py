# Build the bf16-float weight container and verify it, plus a baseline re-export.
import sys, os, torch, numpy as np
ROOT = '/root/hp/wc3/repo'
OUT = '/root/hp/wc3'
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import pysrc.export_weights as E
sys.path.insert(0, '/root/hp/tools')
import tfh
import pysrc.weights_compress as C
src = ROOT + '/models/6m-q4-fp32.tch'
sd = torch.load(src, map_location='cpu')
def is_float_param(k):
    if 'scale' in k: return False
    if k.endswith('.weight') and (k[:-7] + '.quantize_weight.scale') in sd: return False
    return sd[k].dtype == torch.float32
fk = [k for k in sd if is_float_param(k)]
print('float params rounded to bf16:', len(fk), sum(sd[k].numel() for k in fk))
sd2 = dict(sd)
for k in fk: sd2[k] = sd[k].to(torch.bfloat16).to(torch.float32)
torch.save(sd2, OUT + '/6m-q4-fp32-bf16f.tch')
for tag, ck in [('orig', src), ('bf16f', OUT + '/6m-q4-fp32-bf16f.tch')]:
    model = tfh.Transformer(tfh.make_config()).to('cuda')
    model.load_state_dict(torch.load(ck, map_location='cuda')); model.eval()
    binf = f'{OUT}/weights_{tag}.bin'
    E.export_weights(model, binf)
    entries = C._entries_from_reference(binf)
    outf = f'{OUT}/weights_{tag}.tfwc2'
    C.write_tensor_file_v2(outf, entries)
    C._verify_equal(dict(E.read_tensor_file(binf)), C._read_compressed(outf))
    print(tag, 'bin', os.path.getsize(binf), '-> compressed', os.path.getsize(outf), 'round-trip verified')
