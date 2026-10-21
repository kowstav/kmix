import shutil,unittest
from hutter_research.article_order_native import compress,decompress,graph_orders

@unittest.skipIf(shutil.which('7z') is None,'native 7z absent; remote gate mandatory')
class NativePPMdOrderTests(unittest.TestCase):
    def test_complete_paid_inverse_and_framing(self):
        pages=[b'the camel\x00',bytes(range(256))*40,b'',b'Know now.\xff'*500]
        for level in (8,16):
            for seq in (list(range(4)),[3,0,2,1]):
                b=compress(pages,seq,level);self.assertEqual(decompress(b),pages)
                with self.assertRaises(ValueError):decompress(b+b'\x00')
                with self.assertRaises(ValueError):decompress(b[:-1])
        with self.assertRaises(ValueError):compress(pages,[0,0,2,3])
    def test_empty_stream_and_graph_permutations(self):
        self.assertEqual(decompress(compress([],[])),[])
        pages=[(b'The diamond article shares words '+str(i).encode())*5 for i in range(9)]
        orders,count=graph_orders(pages);self.assertLessEqual(count,4*len(pages))
        for seq in orders.values():self.assertEqual(sorted(seq),list(range(len(pages))))

if __name__=='__main__':unittest.main()
