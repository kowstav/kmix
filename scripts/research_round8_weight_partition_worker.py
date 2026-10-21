import datetime,hashlib,json,math,os,pathlib,struct,time,traceback
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'weight_partition_v1';D.mkdir(exist_ok=False)
start=time.monotonic();m={'status':'RUNNING','pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deletions':[],'paid_rental_usd':0,'core_training':False};rows=[]
def save(): (D/'manifest.json').write_text(json.dumps(m,indent=2))
save()
try:
    p=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_unpromoted_raw.bin');data=p.read_bytes();assert data[:8]==b'FX2TFW01';pos=8
    def u32():
        global pos
        a=struct.unpack_from('<I',data,pos)[0];pos+=4;return a
    n=u32();m['input']={'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'serialized_tensors':n};save()
    def kt(c):
        N=int(c.sum());K=len(c)
        return (math.lgamma(N+K/2)-math.lgamma(K/2)-sum(math.lgamma(int(v)+.5)-math.lgamma(.5) for v in c))/math.log(2)
    def hist(a,q): return np.bincount((a.reshape(-1).astype(np.int16)+q),minlength=2*q+1)
    def optimal(a,q,axis):
        if a.size<4096 or a.shape[axis]<2:
            c=hist(a,q);return c,kt(c),0,1
        left,right=np.array_split(a,2,axis=axis);lc,ll,ls,lb=optimal(left,q,axis);rc,rl,rs,rb=optimal(right,q,axis);c=lc+rc
        stop=1+kt(c);split=1+ll+rl
        return (c,stop,0,1) if stop<=split else (c,split,1+ls+rs,lb+rb)
    for i in range(n):
        b=u32();name=data[pos:pos+b].decode();pos+=b;code=data[pos];pos+=1;rank=u32();shape=tuple(u32() for _ in range(rank));N=math.prod(shape);width=[1,2,4,4][code]
        a=np.frombuffer(data,dtype=np.int8,count=N,offset=pos).reshape(shape) if code==0 else None;pos+=N*width
        if code!=0:continue
        q=max(abs(int(a.min())),abs(int(a.max())));c=hist(a,q);base=kt(c);nz=c[c>0];entropy=float(-sum(v*math.log2(v/N) for v in nz))
        r={'name':name,'shape':shape,'numel':N,'qmax':q,'entropy_bits':entropy,'homogeneous_KT_bits':base,'matrix':rank==2,'axes':[]}
        if rank==2:
            for axis in [0,1]:
                _,cost,splits,blocks=optimal(a,q,axis);r['axes'].append({'axis':axis,'bits':cost,'splits':splits,'blocks':blocks})
            best=min(r['axes'],key=lambda z:z['bits']);r['chosen_axis']=best['axis'];r['best_priced_bits']=min(base,best['bits'])+2+8
        else:r['best_priced_bits']=base+2+8
        r['partition_gain_over_homogeneous_bits']=base+10-r['best_priced_bits'];rows.append(r)
    assert pos==len(data)
    (D/'tensors.json').write_text(json.dumps(rows,indent=2))
    sums={key:sum(r[key] for r in rows) for key in ['numel','entropy_bits','homogeneous_KT_bits','best_priced_bits','partition_gain_over_homogeneous_bits']}
    m.update(status='COMPLETE',summary=sums,int8_tensors=len(rows),wall_seconds=time.monotonic()-start,claim='DIAGNOSTIC_UNIVERSAL_CODE_COST_NOT_COMPLETE_CONTAINER',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print(json.dumps(m))
except BaseException as e:
    m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
