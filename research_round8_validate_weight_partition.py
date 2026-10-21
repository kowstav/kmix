"""Check universal marginal and partition optimum against independent enumeration."""
import itertools,json,math
from fractions import Fraction as F
from pathlib import Path
def rational_marginal(sequence,K):
    counts=[0]*K;p=F(1)
    for i,s in enumerate(sequence):p*=F(2*counts[s]+1,2*i+K);counts[s]+=1
    return p
def gamma_marginal(sequence,K):
    counts=[sequence.count(i) for i in range(K)]
    return (math.lgamma(len(sequence)+K/2)-math.lgamma(K/2)-sum(math.lgamma(c+.5)-math.lgamma(.5) for c in counts))/math.log(2)
err=0
for K in [2,3,5]:
    for sequence in [[],[0],[0,1,0,1],[0]*12,list(range(K))*3]:
        exact=-math.log2(float(rational_marginal(sequence,K)));err=max(err,abs(exact-gamma_marginal(sequence,K)))
assert err<1e-11
# Each dyadic tree's complete set of legal stop/split descriptions is
# enumerated as lists of terminal intervals and paid internal decisions.
def descriptions(lo,hi):
    if hi-lo==1:return [([(lo,hi)],0)]
    mid=(lo+hi)//2;out=[([(lo,hi)],1)]
    for (a,ac),(b,bc) in itertools.product(descriptions(lo,mid),descriptions(mid,hi)):
        out.append((a+b,1+ac+bc))
    return out
seq=[0,0,0,0,1,1,1,1];options=descriptions(0,len(seq))
enum=min(flags+sum(-math.log2(float(rational_marginal(seq[lo:hi],2))) for lo,hi in blocks) for blocks,flags in options)
def dp(lo,hi):
    local=gamma_marginal(seq[lo:hi],2)
    if hi-lo==1:return local
    mid=(lo+hi)//2
    return min(1+local,1+dp(lo,mid)+dp(mid,hi))
assert abs(enum-dp(0,len(seq)))<1e-11
out={'status':'PASS','KT_exact_rational_max_error_bits':err,'enumerated_partition_descriptions':len(options),'partition_optimum_error_bits':abs(enum-dp(0,len(seq))),'scope':'Validates mathematical code-cost and finite partition recurrence, not a C3 container encoder/decoder.'}
Path(__file__).with_name('research_round8_weight_partition_selftest.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
