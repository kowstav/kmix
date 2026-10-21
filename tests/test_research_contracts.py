import math,unittest
import numpy as np
from hutter_research.contracts import *

class Contracts(unittest.TestCase):
    def test_cost_amortizes_over_corpus_once(self):
        assets=[Asset('coefficient',16,2)]
        self.assertAlmostEqual(conditional_projection(5.653/1048576,587138826,assets),3133.336402299881)
        self.assertLess(conditional_projection(5.653/1048576,1048576,assets),0)
    def test_unbiased_piece_estimator_not_sample_ratio(self):
        losses=[2.,100.];weights=[1.,10.];p=[.9,.1];den=sum(weights)
        mean=sum(p[i]*weighted_objective_estimator([losses[i]],[p[i]],den) for i in range(2))
        self.assertAlmostEqual(mean,sum(losses)/den)
        self.assertNotAlmostEqual(sum(p[i]*losses[i]/weights[i] for i in range(2)),mean)
    def test_mdl_sum_and_mean_units(self):
        self.assertEqual(mdl_mean_bits(1.,80,100,2,1),2.6)
        self.assertEqual(100*mdl_mean_bits(1.,80,100,2,1),260.)
    def test_realized_path_entropy_is_not_before_symbol(self):
        h0=float(binary_entropy(.5));h1=float(binary_entropy(.01));q=np.array([.25,.25,.005,.495])
        true_entropy=-float((q*np.log2(q)).sum())
        self.assertAlmostEqual(true_entropy,h0+.5*h0+.5*h1)
        self.assertNotAlmostEqual(h0+h0,h0+h1) # same past, different realized next bit
    def test_synergy_can_exceed_sum(self):
        self.assertEqual(empirical_pair_interaction(0,0,1),1) # XOR features
    def test_low_power_test_not_equivalence(self):
        self.assertFalse(equivalence_interval_pass(-10,10,.02))
        self.assertTrue(equivalence_interval_pass(-.01,.01,.02))
    def test_adjacent_single_cluster_cannot_fake_sample_size(self):
        rows=[dict(stratum='early',cluster='one-run',input_bytes=512000,gain_bytes=100) for _ in range(16)]
        self.assertEqual(stratified_cluster_bootstrap(rows,{'early':1.})['status'],'INSUFFICIENT_INDEPENDENT_CLUSTERS')
    def test_holm_stops_after_first_failed_rank(self):
        self.assertEqual(holm_decisions({'a':.01,'b':.04,'c':.045}),{'a':True,'b':False,'c':False})
    def test_two_clusters_do_not_generate_percentile_interval(self):
        rows=[dict(stratum='s',cluster=str(i),input_bytes=100,gain_bytes=i) for i in range(2)]
        result=stratified_cluster_bootstrap(rows,{'s':1.})
        self.assertEqual(result['status'],'INSUFFICIENT_INDEPENDENT_CLUSTERS')
        self.assertNotIn('lower95',result)
    def test_ten_declared_clusters_allow_conditional_interval(self):
        rows=[dict(stratum='s',cluster=str(i),input_bytes=100,gain_bytes=i) for i in range(10)]
        result=stratified_cluster_bootstrap(rows,{'s':1.})
        self.assertEqual(result['independent_clusters'],10)
        self.assertAlmostEqual(result['mean_saved_bytes_per_input_byte'],.045)
    def test_invalid_probability_or_normalization_is_rejected(self):
        with self.assertRaises(ValueError):binary_entropy(float('nan'))
        with self.assertRaises(ValueError):weighted_objective_estimator([1.],[float('nan')],1.)
        with self.assertRaises(ValueError):mdl_mean_bits(1.,80,float('nan'))
    def test_variable_cluster_lengths_cannot_silently_change_estimand(self):
        rows=[dict(stratum='s',cluster='a',input_bytes=100,gain_bytes=10),
              dict(stratum='s',cluster='b',input_bytes=1000,gain_bytes=1)]
        with self.assertRaises(ValueError):stratified_cluster_bootstrap(rows,{'s':1.})

if __name__=='__main__':unittest.main()
