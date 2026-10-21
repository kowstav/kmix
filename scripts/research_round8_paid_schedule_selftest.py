import itertools,json,math,subprocess,sys
from pathlib import Path
binary=Path(sys.argv[1]);dest=Path(sys.argv[2])
cases=[[[0,5,-4],[0,6,-4],[0,-5,7],[0,-4,8]],[[0,0,-1]]*5,[[0,20,-20]],[[0,2,3],[0,1,6],[0,4,-8]]]
errors=[]
for gains in cases:
    N=len(gains);K=len(gains[0]);best=-math.inf
    # Exhaust every cut placement and every segment's policy assignment.
    for cuts in itertools.product([0,1],repeat=N-1):
        endpoints=[0]+[i+1 for i,c in enumerate(cuts) if c]+[N]
        for labels in itertools.product(range(K),repeat=len(endpoints)-1):
            score=0
            for (lo,hi),c in zip(zip(endpoints,endpoints[1:]),labels):
                score+=sum(gains[i][c] for i in range(lo,hi))-(1 if c==0 else math.log2(2*(K-1)))-(1+2*((hi-lo).bit_length()-1))
            best=max(best,score)
    payload=f'{N} {K}\n'+'\n'.join(' '.join(map(str,row)) for row in gains)+'\n'
    got=json.loads(subprocess.run([str(binary),'dp_trace'],input=payload,text=True,capture_output=True,check=True).stdout)
    errors.append(abs(got['program_net_gain_bits']-best));assert errors[-1]<1e-12
    spans=got['segments'];assert spans[0][0]==0 and spans[-1][1]==N and all(a[1]==b[0] for a,b in zip(spans,spans[1:]))
    assert got['saving_bytes_including_mode']==(max(0,best)-1)/8
result={'status':'PASS','independent_reference':'exhaustive compositions and policy assignments, no DP recurrence reused','cases':len(cases),'max_optimum_error_bits':max(errors),'neutral_mode_and_header_charged':True,'exact_contiguous_coverage':True,'limitations':'Does not establish production coder or full-corpus package parity.'}
dest.write_text(json.dumps(result,indent=2));print(json.dumps(result))
