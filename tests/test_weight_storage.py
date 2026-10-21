import unittest
import numpy as np
from hutter_research.weight_storage import encode,decode,LAYOUTS

class WeightStorage(unittest.TestCase):
    def test_every_layout_preserves_shapes_types_and_values(self):
        tensors={'matrix':(0,np.arange(-7,8,dtype='i1').reshape(3,5)),
                 'float':(2,np.array([[0.,-1.,3.25],[1e-20,8.,-0.]],dtype='f4')),
                 'bf16':(1,np.array([0,65535,1234],dtype='u2')),
                 'empty':(0,np.array([],dtype='i1')),
                 'wide':(0,np.array([-128,127,21],dtype='i1'))}
        for layout in LAYOUTS:
            for codec in ('gzip','lzma'):
                result=decode(encode(tensors,layout,codec))
                for name,(dt,a) in tensors.items():
                    self.assertEqual(result[name][0],dt)
                    self.assertEqual(result[name][1].shape,a.shape)
                    self.assertEqual(result[name][1].tobytes(),a.tobytes(),(layout,name))
    def test_corrupt_payload_is_not_accepted(self):
        blob=bytearray(encode({'x':(0,np.array([1],dtype='i1'))},'plain','gzip'))
        blob[21]^=1
        with self.assertRaises(ValueError):decode(blob)
    def test_exact_regeneration_and_mismatch_fallback(self):
        from hutter_research.native_weights import cuda_rope_table
        inv=np.array([1.,.01,.0001],dtype='f4')
        tensors={'rope.inv_freq':(2,inv),'rope.sin':(2,cuda_rope_table(inv,17,False)),
                 'rope.cos':(2,cuda_rope_table(inv,17,True))}
        for altered in (False,True):
            if altered:tensors['rope.sin'][1][3,1]+=np.float32(.01)
            blob=encode(tensors,'planes','gzip',regenerate=True)
            result=decode(blob)
            for name,(dt,a) in tensors.items():self.assertEqual(result[name][1].tobytes(),a.tobytes())
