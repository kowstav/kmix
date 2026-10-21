import unittest
from hutter_research.article_order_ppmd import compress,decompress,graph_orders
try:import pyppmd
except ImportError:pyppmd=None
@unittest.skipIf(pyppmd is None,'pyppmd not installed; Linux preflight required')
class PPMdOrderTests(unittest.TestCase):
    def test_all_paid_permutations_restore_exactly(self):
        pages=[b'A camel was there.\x00',b'\xff\n',b'',b'a diamond and an almond']
        for order in ([0,1,2,3],[3,0,2,1]):
            for level in (8,16):self.assertEqual(decompress(compress(pages,order,level)),pages)
        with self.assertRaises(ValueError):compress(pages,[0,0,2,3])
    def test_graph_is_a_permutation(self):
        pages=[(b'word repeated article '+str(i).encode())*10 for i in range(12)]
        orders,n=graph_orders(pages);self.assertLessEqual(n,4*len(pages))
        for order in orders.values():self.assertEqual(sorted(order),list(range(len(pages))))
