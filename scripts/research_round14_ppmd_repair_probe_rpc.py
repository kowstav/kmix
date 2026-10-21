from pathlib import Path
import sys,json,struct,inspect
sys.path.insert(0,'/root/r14_ppmd_diagnostic/lib');import pyppmd
R=Path('/root/r14_ppmd_real');out=[]
for f in sorted(R.glob('*.raw')):
    raw=f.read_bytes();b=f.with_suffix('.hporder').read_bytes();n,o,m,a,c,d=struct.unpack_from('<6I',b,8);p=b[32+a+c:];r={'case':f.stem}
    for pad in (1,8,32):
        try:r['pad'+str(pad)]=pyppmd.decompress(p+b'\0'*pad,max_order=o,mem_size=m,variant='I')==raw
        except Exception as e:r['pad'+str(pad)]=repr(e)
    for variant in ('H',):
        try:
            p=pyppmd.compress(raw,max_order=o,mem_size=m,variant=variant);x=pyppmd.decompress(p,max_order=o,mem_size=m,variant=variant)
            r[variant]={'exact':x==raw,'bytes':len(p)}
        except Exception as e:r[variant]={'error':repr(e)}
    out.append(r)
print(json.dumps(out));Path('/kaggle/working/hp_round14/ppmd_repair_probe_v1.json').write_text(json.dumps(out,indent=2))
