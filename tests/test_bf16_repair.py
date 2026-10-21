import unittest
import numpy as np
from research_round10_bf16_repair import bf16_bits,promoted_bf16
class BF16(unittest.TestCase):
 def test_half_even_and_sign(self):
  # Exact midpoint between adjacent BF16 values; lower significand odd/even.
  u=np.array([0x3f808000,0x3f818000,0xbf808000,0xbf818000],dtype='<u4')
  self.assertEqual(bf16_bits(u.view('<f4')).tolist(),[0x3f80,0x3f82,0xbf80,0xbf82])
 def test_original_bf16_is_unchanged(self):
  bits=np.arange(65536,dtype='<u2');values=promoted_bf16(bits);finite=np.isfinite(values)
  self.assertTrue(np.array_equal(bits[finite],bf16_bits(values[finite])))
if __name__=='__main__':unittest.main()
