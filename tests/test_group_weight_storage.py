import unittest
import numpy as np
from hutter_research import weight_storage as w
from hutter_research.group_weight_storage import pack,unpack
class GroupedWeights(unittest.TestCase):
    def test_independent_groups_restore_exact_dtypes(self):
        tensors={'a':(0,np.array([-7,0,3],dtype='i1')),'b':(1,np.array([123,0,65535],dtype='<u2'))}
        blobs=[w.encode({k:v},'nibble','gzip') for k,v in tensors.items()]
        result=unpack(pack(blobs,[],w.tensor_digest(tensors)))
        self.assertEqual(w.tensor_digest(result),w.tensor_digest(tensors))
        with self.assertRaises(ValueError):unpack(pack(blobs+[blobs[0]],[],w.tensor_digest(tensors)))
    def test_regeneration_does_not_require_materialized_tables(self):
        from hutter_research.native_weights import cuda_rope_table
        inv=np.array([1.,.01],dtype='f4');t={'rope.inv_freq':(2,inv),'rope.sin':(2,cuda_rope_table(inv,32,False))}
        schema,_=w.representation(t,'plain',True);deferred=[r for r in schema if r[3].startswith('rope_')]
        blob=pack([w.encode({'rope.inv_freq':t['rope.inv_freq']},'planes','lzma')],deferred,w.tensor_digest(t))
        self.assertEqual(w.tensor_digest(unpack(blob)),w.tensor_digest(t))
        with self.assertRaises(ValueError):unpack(blob+b'\x00')
