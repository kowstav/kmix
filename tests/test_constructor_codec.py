import unittest
from hutter_research.constructor_codec import encode,decode,inspect_sizes

class ConstructorCodecProperties(unittest.TestCase):
    def test_coarse_anchor_controls_restore_literals_and_case(self):
        raw=b'There was a camel. Now I know! ARE they on a Diamond?\x00\xff\xe2\x98\x83'
        for mode in ('coarse_right','coarse_wrong','coarse_left'):
            for alpha in (1,4):self.assertEqual(decode(encode(raw,mode,alpha)),raw)
    def test_all_controls_restore_every_byte(self):
        cases=[b'',b'\x00\xff\n',b'the the and the',b'The camel IS tall. Now I know.',
               'There was a camel. Äé日本語; tHe A, camel\r\n'.encode(),
               b'<text>there is a camel\nthere was a diamond and an almond</text>\n',
               b"don't I'M we've: whom? is?",b'the '*40000]
        for raw in cases:
            for mode,alpha in [('unigram',0),('markov',1),('markov',4),('anchors',1),('anchors',4),('wrong_anchors',4),('bag',0)]:
                archive=encode(raw,mode,alpha)
                self.assertEqual(decode(archive),raw,(mode,alpha,raw[:30]))
                self.assertEqual(50+sum(inspect_sizes(archive).values()),len(archive))
    def test_header_and_bag_costs_exist(self):
        archive=encode(b'the the and the','bag')
        sizes=inspect_sizes(archive)
        self.assertGreater(sizes['bag_metadata'],0)
        self.assertGreater(sizes['lexicon'],0)
    def test_invalid_inputs(self):
        for mode,alpha in [('bad',0),('unigram',1),('bag',4),('anchors',9)]:
            with self.assertRaises(ValueError): encode(b'x',mode,alpha)
        with self.assertRaises(ValueError): decode(b'bad')

if __name__=='__main__': unittest.main()
