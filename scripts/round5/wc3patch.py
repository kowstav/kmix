# Adds ENC_F32_BF16 (=6) to the FX2TFWC2 weight container: float32 tensors whose values are
# exactly bf16-representable are coded as bf16 bits with their own hi/lo adaptive models and
# expanded back to float32 by the decoder (bit-exact). Patches pysrc/weights_compress.py and
# cpp_infer/src/weights_io_compressed.cpp in the tree given as argv[1].
import sys, os
root = sys.argv[1]

def patch(path, old, new, count=1):
    p = os.path.join(root, path)
    s = open(p, encoding='utf-8').read()
    n = s.count(old)
    assert n == count, f'{path}: anchor found {n} times, expected {count}:\n{old}'
    open(p, 'w', encoding='utf-8').write(s.replace(old, new))

PY = 'pysrc/weights_compress.py'
patch(PY, 'ENC_ROPE_COS = 5  # empty payload: recompute from rope.inv_freq',
      'ENC_ROPE_COS = 5  # empty payload: recompute from rope.inv_freq\n'
      'ENC_F32_BF16 = 6  # DT_F32 with bf16-exact values: bf16 bits, own hi/lo models')
patch(PY, '''        self.plane = [make() for _ in range(4)]
        self._make = make''', '''        self.plane = [make() for _ in range(4)]
        self.f32b_hi = make()
        self.f32b_lo = {}  # hi byte -> byte tree
        self._make = make''')
patch(PY, '''    def bf16_lo_tree(self, hi: int) -> list:''', '''    def f32b_lo_tree(self, hi: int) -> list:
        t = self.f32b_lo.get(hi)
        if t is None:
            t = self.f32b_lo[hi] = self._make()
        return t

    def bf16_lo_tree(self, hi: int) -> list:''')
patch(PY, '''                return ENC_ROPE_SIN if name == "rope.sin" else ENC_ROPE_COS
        return ENC_PLANE4''', '''                return ENC_ROPE_SIN if name == "rope.sin" else ENC_ROPE_COS
        bits = np.ascontiguousarray(array).view(np.uint32).ravel()
        if name != "rope.inv_freq" and len(bits) > 0 and not (bits & 0xFFFF).any():
            return ENC_F32_BF16
        return ENC_PLANE4''')
patch(PY, '''        elif encoding == ENC_PLANE4:
            raw = data.tobytes()''', '''        elif encoding == ENC_F32_BF16:
            for v in (data.view(np.uint32).ravel() >> 16).tolist():
                hi = v >> 8
                enc.encode_tree(models.f32b_hi, 8, hi)
                enc.encode_tree(models.f32b_lo_tree(hi), 8, v & 0xFF)
        elif encoding == ENC_PLANE4:
            raw = data.tobytes()''')
patch(PY, '''        elif encoding == ENC_PLANE4:
            planes = models.plane''', '''        elif encoding == ENC_F32_BF16:
            assert dtype_code == DTYPE_FLOAT32
            vals = np.empty(count, dtype=np.uint32)
            for i in range(count):
                hi = dec.decode_tree(models.f32b_hi, 8)
                lo = dec.decode_tree(models.f32b_lo_tree(hi), 8)
                vals[i] = ((hi << 8) | lo) << 16
            array = vals.view(np.float32).reshape(shape)
        elif encoding == ENC_PLANE4:
            planes = models.plane''')

CC = 'cpp_infer/src/weights_io_compressed.cpp'
patch(CC, '''  ENC_ROPE_COS = 5,''', '''  ENC_ROPE_COS = 5,
  ENC_F32_BF16 = 6,''')
patch(CC, '''  std::vector<uint16_t> bf16_lo;  // hi byte -> byte tree''',
      '''  std::vector<uint16_t> bf16_lo;  // hi byte -> byte tree
  std::vector<uint16_t> f32b_hi;  // byte tree (ENC_F32_BF16)
  std::vector<uint16_t> f32b_lo;  // hi byte -> byte tree''')
patch(CC, '''        bf16_lo(256 * 256, 1024),''', '''        bf16_lo(256 * 256, 1024),
        f32b_hi(256, 1024),
        f32b_lo(256 * 256, 1024),''')
patch(CC, '''      case ENC_PLANE4: {
        if (dtype_size(t.dtype) != 4)''', '''      case ENC_F32_BF16: {
        if (t.dtype != DT_F32) die("%s: %s: ENC_F32_BF16 on dtype %u", path,
                                   name.c_str(), unsigned(t.dtype));
        uint32_t* out = reinterpret_cast<uint32_t*>(t.data.data());
        for (size_t k = 0; k < numel; k++) {
          uint32_t hi = dec.decode_tree(m.f32b_hi.data(), 8);
          uint32_t lo = dec.decode_tree(&m.f32b_lo[hi * 256], 8);
          out[k] = ((hi << 8) | lo) << 16;
        }
        break;
      }
      case ENC_PLANE4: {
        if (dtype_size(t.dtype) != 4)''')
print('wc3 patch applied to', root)
