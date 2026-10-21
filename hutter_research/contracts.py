"""Units, cost, statistical and causal contracts. No training side effects."""
from dataclasses import dataclass
import math
import numpy as np

@dataclass(frozen=True)
class Asset:
    name: str
    delta_bytes: int
    counted_copies: int
    def __post_init__(self):
        if self.counted_copies < 0:raise ValueError('Negative asset multiplicity')

def conditional_projection(rate_saved_bytes_per_input_byte, corpus_bytes, assets):
    """Scenario only. A cold-slice rate is never silently called stationary."""
    if corpus_bytes <= 0:raise ValueError('Invalid corpus length')
    return rate_saved_bytes_per_input_byte * corpus_bytes - sum(a.delta_bytes*a.counted_copies for a in assets)

def weighted_objective_estimator(piece_weighted_loss_sums, sampling_probabilities,
                                 global_weight_sum):
    """Horvitz-Thompson minibatch estimator for the declared finite-piece loss.

    Sampling with replacement; pieces partition the fixed target positions.
    The target is sum_p sum_t w_t loss_t / global_weight_sum. Context/reset
    conventions must also match that target. Never normalize by batch weights.
    """
    loss=np.asarray(piece_weighted_loss_sums,dtype=np.float64)
    p=np.asarray(sampling_probabilities,dtype=np.float64)
    if (loss.ndim!=1 or p.shape!=loss.shape or not loss.size or np.any((p<=0)|(p>1))
        or not np.isfinite(loss).all() or not np.isfinite(p).all() or np.any(loss<0)
        or not math.isfinite(global_weight_sum) or global_weight_sum<=0):
        raise ValueError('Invalid piece sample, probabilities or normalization')
    return float(np.mean(loss/p)/global_weight_sum)

def mdl_mean_bits(mean_bit_loss, model_rate_bits, corpus_targets, counted_copies=2, rate_lambda=1):
    if (not all(math.isfinite(x) for x in [mean_bit_loss,model_rate_bits,corpus_targets,counted_copies,rate_lambda])
        or mean_bit_loss<0 or model_rate_bits<0 or corpus_targets<=0 or counted_copies<0 or rate_lambda<0):
        raise ValueError('Invalid MDL units')
    return mean_bit_loss + rate_lambda*counted_copies*model_rate_bits/corpus_targets

def binary_entropy(p):
    p=np.asarray(p,dtype=np.float64)
    if not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('Invalid probability')
    a=np.maximum(p,np.finfo(np.float64).tiny);b=np.maximum(1-p,np.finfo(np.float64).tiny)
    return -(p*np.log2(a)+(1-p)*np.log2(b))

def empirical_pair_interaction(gain_a,gain_b,gain_ab):
    """Positive means synergy. No assumption of submodularity/redundancy."""
    return gain_ab-gain_a-gain_b

def stratified_cluster_bootstrap(rows, stratum_weights, seed=10007, draws=10000):
    """Resample independently drawn clusters within each stratum.

    Each row has stratum, cluster, input_bytes, gain_bytes. Adjacent windows
    with shared dependence belong to the same cluster. Requires >=10 clusters
    per stratum for an interval; insufficient evidence is explicit.
    Caller must justify cluster sampling and stratum population weights.
    """
    if draws<1000 or not rows:raise ValueError('Insufficient bootstrap configuration')
    if (any(not math.isfinite(w) or w<0 for w in stratum_weights.values())
        or abs(sum(stratum_weights.values())-1)>1e-10):raise ValueError('Stratum weights must sum to one')
    grouped={}
    for row in rows:
        if (row['stratum'] not in stratum_weights or not math.isfinite(row['input_bytes'])
            or not math.isfinite(row['gain_bytes']) or row['input_bytes']<=0):
            raise ValueError('Invalid window or undeclared stratum')
        key=(row['stratum'],row['cluster']);total=grouped.setdefault(key,[0.,0.])
        total[0]+=row['gain_bytes'];total[1]+=row['input_bytes']
    rates={s:np.array([g/n for (ss,_),(g,n) in grouped.items() if ss==s],dtype=np.float64) for s in stratum_weights}
    for s in stratum_weights:
        exposure=[n for (ss,_),(g,n) in grouped.items() if ss==s]
        if exposure and max(exposure)!=min(exposure):
            raise ValueError('Unequal cluster exposure requires a declared sampling-weighted estimator')
    if any(len(a)<10 for a in rates.values()):
        return {'status':'INSUFFICIENT_INDEPENDENT_CLUSTERS','counts':{s:len(a) for s,a in rates.items()},
                'required_per_stratum':10,
                'limitations':'Do not present a percentile interval from two to nine clusters as a reliable 95% interval.'}
    rng=np.random.default_rng(seed);samples=np.zeros(draws);mean=0.
    for s,weight in stratum_weights.items():
        a=rates[s];samples+=weight*a[rng.integers(len(a),size=(draws,len(a)))].mean(axis=1);mean+=weight*a.mean()
    lower,upper=np.quantile(samples,[.025,.975])
    return {'status':'CONDITIONAL_CLUSTER_BOOTSTRAP_INTERVAL','mean_saved_bytes_per_input_byte':float(mean),
            'lower95':float(lower),'upper95':float(upper),'seed':seed,'draws':draws,'independent_clusters':sum(map(len,rates.values())),
            'limitations':'Valid only for the declared cluster sampling/population; not a full-file observation.'}

def equivalence_interval_pass(lower,upper,margin):
    """A nonsignificant zero-difference t test is not evidence of equivalence."""
    if not all(math.isfinite(x) for x in [lower,upper,margin]) or lower>upper or margin<=0:
        raise ValueError('Invalid equivalence interval')
    return lower > -margin and upper < margin

def holm_decisions(p_values,alpha=.05):
    if not 0<alpha<1 or any(not 0<=p<=1 for p in p_values.values()):raise ValueError('Invalid p value')
    ranked=sorted(p_values.items(),key=lambda v:v[1]);results={k:False for k in p_values};n=len(ranked)
    for i,(name,p) in enumerate(ranked):
        if p>alpha/(n-i):break
        results[name]=True
    return results
