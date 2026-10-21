from pathlib import Path
import sys,json,time
sys.path.insert(0,'/root/r14_backend_probe/lib');import pyppmd
R=Path('/root/r14_backend_probe');rows=[]
for i,o,rev in ((0,8,False),(2,16,True),(3,8,False)):
    label=f'region_{i}_{o}_{rev}';raw=(R/(label+'.raw')).read_bytes();payload=(R/(label+'_H.ppmd')).read_bytes()
    d=pyppmd.Ppmd7Decoder(o,64<<20);out=d.decode(payload,len(raw));calls=1
    initial={'bytes':len(out),'prefix_matches':out==raw[:len(out)],'needs_input':d.needs_input}
    while len(out)<len(raw) and calls<100:
        more=d.decode(b'',len(raw)-len(out));calls+=1
        if not more:break
        out+=more
    rows.append({'case':label,'input_bytes':len(raw),'decoded_bytes':len(out),'exact':out==raw,'initial':initial,'calls':calls,'first_mismatch':next((i for i,(a,b) in enumerate(zip(raw,out)) if a!=b),None)})
m={'status':'PASS_THREE_REAL_DATA_H_BACKEND_INVERSES' if all(r['exact'] for r in rows) else 'FAIL_H_BACKEND_PRESERVED','time':time.time(),'cases':rows,'method':'Ppmd7Decoder.decode with length and draining unconsumed input'}
Path('/kaggle/working/hp_round14/ppmd_h_probe_v1.json').write_text(json.dumps(m,indent=2));print(json.dumps(m))
