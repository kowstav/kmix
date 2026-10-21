"""Independent batch marginal (exact rationals) versus C++ online tree."""
import itertools, json, math, random, subprocess, sys
from fractions import Fraction as F
from pathlib import Path
binary=Path(sys.argv[1]); dest=Path(sys.argv[2])
rng=random.Random(8001)
contexts=[[0,0,0,0,0,0],[1,0,0,0,0,0],[0,2,1,0,1,0],[1,0,0,3,2,3]]
data=[]
for i in range(14):
    ctx=contexts[i%len(contexts)]
    q=[rng.randrange(500,65000) for _ in range(25)]
    y=rng.randrange(2)
    data.append((tuple(ctx),q,y))
pri=[F(1,2)]+[F(1,48)]*24
def local_marginal(rows):
    total=F(0)
    for k in range(25):
        z=pri[k]
        for _,q,y in rows:z*=F(q[k] if y else 65536-q[k],65536)
        total+=z
    return total
def batch_marginal(rows,depth=0):
    if not rows:return F(1)
    local=local_marginal(rows)
    if depth==6:return local
    split=F(1)
    for group in sorted(set(row[0][depth] for row in rows)):
        split*=batch_marginal([row for row in rows if row[0][depth]==group],depth+1)
    return (local+split)/2
expected=[]
for i,(ctx,q,y) in enumerate(data):
    expected.append(float(batch_marginal(data[:i]+[(ctx,q,1)])/batch_marginal(data[:i])))
def invoke(rows):
    payload=str(len(rows))+'\n'+'\n'.join(' '.join(map(str,[*ctx,*q,y])) for ctx,q,y in rows)+'\n'
    result=subprocess.run([str(binary),'gate_trace'],input=payload,text=True,capture_output=True,check=True)
    return [float(x) for x in result.stdout.splitlines()]
actual=invoke(data)
worst=max(abs(a-b) for a,b in zip(actual,expected))
assert len(actual)==len(data) and worst<2e-12,(worst,actual,expected)
# New suffixes and suffix contexts cannot change an already predicted prefix.
changed=data[:7]+[(contexts[3],list(reversed(q)),1-y) for _,q,y in data[7:]]
assert actual[:7]==invoke(changed)[:7]
# Exact identity family on extreme native integers stays equal to p, even
# after different context paths and extreme likelihoods have been observed.
identity=[]
for i,p in enumerate([1,65535,32768,1,2,65534,40000,12345]*4):
    identity.append((tuple(contexts[i%4]),[p]*25,i%2))
got=invoke(identity)
assert max(abs(a-p[1][0]/65536) for a,p in zip(got,identity))<2e-12
result={'status':'PASS','independent_reference':'exact-rational batch marginal over finite tree prunings and leaf candidate priors','sequence_bits':len(data),'max_prediction_error':worst,'prefix_noninterference':True,'extreme_identity':True,'all_tree_probabilities_normalized':all(0<p<1 for p in actual),'limitations':'Does not verify full native encoder/decoder, compiler portability, or WRT preprocessing inverse.'}
dest.write_text(json.dumps(result,indent=2));print(json.dumps(result))
