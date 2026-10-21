import gzip,io,struct,unittest
from hutter_research.full_container import decoded_chunks
from hutter_research.constructor_codec import encode

class FullContainer(unittest.TestCase):
    def container(self,payload,length):
        return b'HPFULL13'+struct.pack('<QI',length,1)+struct.pack('<II',length,len(payload))+payload
    def test_decoder_identifies_the_paid_codec_without_external_policy(self):
        raw=b'There is a camel and the camel is there.\x00\xff'
        for payload in (gzip.compress(raw),encode(raw,'coarse_right',4)):
            self.assertEqual(b''.join(decoded_chunks(io.BytesIO(self.container(payload,len(raw))))),raw)
    def test_truncation_length_and_trailing_bytes_are_rejected(self):
        raw=b'abcd';blob=self.container(gzip.compress(raw),len(raw))
        for bad in (blob[:-1],blob+b'x',self.container(gzip.compress(raw),len(raw)+1)):
            with self.assertRaises((ValueError,EOFError)):list(decoded_chunks(io.BytesIO(bad)))
