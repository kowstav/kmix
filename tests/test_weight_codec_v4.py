import tempfile
from pathlib import Path
import unittest
import numpy as np
from hutter_research import native_weights as w

class CodecV4Properties(unittest.TestCase):
    def test_changed_parameters_require_explicit_format(self):
        with self.assertRaises(ValueError):
            w.write_tensor_file_v3('unused',[],seed_total=64)

    def test_invalid_parameters_rejected(self):
        for seed,limit in [(0,65536),(960,960),(65537,262144),(960,1048577),(True,65536)]:
            with self.assertRaises(ValueError): w.validate_adapt_parameters(seed,limit)

    def test_v4_default_body_is_v3_body(self):
        entries=[('x.q',0,np.array([[-7,0,7,-1,1]]*1000,dtype=np.int8)),
                 ('y.q',0,np.array([[-7,0,7]]*1000,dtype=np.int8)),
                 ('x.scale',1,np.array([0,32768,65535],dtype=np.uint16))]
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'v3',Path(d)/'v4'
            w.write_tensor_file_v3(a,entries)
            w.write_tensor_file_v3(b,entries,format_version=4)
            self.assertEqual(a.read_bytes()[12:],b.read_bytes()[20:])
            self.assertEqual(len(b.read_bytes())-len(a.read_bytes()),8)

    def test_all_parameter_arms_roundtrip_and_rescale(self):
        rng=np.random.default_rng(715)
        entries=[('x.q',0,rng.integers(-7,8,size=(40000,),dtype=np.int8)),
                 ('y.q',0,rng.integers(-7,8,size=(5000,),dtype=np.int8)),
                 ('singleton',0,np.zeros(30000,dtype=np.int8)),
                 ('all_symbols',0,np.arange(-127,128,dtype=np.int8))]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'v4'
            for seed in [64,240,960,3840]:
                for limit in [16384,65536,262144]:
                    w.write_tensor_file_v3(path,entries,seed_total=seed,halve_limit=limit,format_version=4)
                    decoded=w.read_tensor_file_v3(path)
                    for name,code,data in entries:
                        self.assertEqual(decoded[name][0],code)
                        self.assertEqual(decoded[name][1].tobytes(),data.tobytes())

if __name__=='__main__': unittest.main()
