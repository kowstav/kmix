import unittest,random
from hutter_research.constructor_codec import encode,decode,inspect_sizes,WORDS,ConditionalModel,ConditionalRemainingModel

class ConditionalBagTests(unittest.TestCase):
    def test_every_descendant_recovers_order_case_and_layout(self):
        rng=random.Random(14891)
        raws=[b'',b'\x00\xff there was a camel',b'the the AND the camel; I know now.',
              (' '.join(rng.choice(WORDS+('diamond','camel','Paris')) for _ in range(1600))).encode(),
              b'the '*40000]
        for raw in raws:
            for family in ('markov','right','wrong','left'):
                for beta in (0,1):
                    blob=encode(raw,f'bag_{family}{beta}',4)
                    self.assertEqual(decode(blob),raw)
                    self.assertEqual(50+sum(inspect_sizes(blob).values()),len(blob))
    def test_paid_counts_support_and_post_observation_update(self):
        base=ConditionalModel(3,4);base.select(0);counts=[2,0,1]
        model=ConditionalRemainingModel(counts,base,1)
        self.assertEqual(model.active,[0,2]);self.assertEqual(base.global_counts,[0,0,0])
        model.update(1);self.assertEqual(counts,[2,0,0]);self.assertEqual(base.global_counts,[0,0,1])
    def test_long_run_normalization_remains_positive_and_bounded(self):
        base=ConditionalModel(3,4);base.select(0)
        model=ConditionalRemainingModel([10**8,1,0],base,1)
        self.assertLessEqual(model.tot,32768);self.assertTrue(all(n>0 for n in model.cnt))
