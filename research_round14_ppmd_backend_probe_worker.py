from pathlib import Path
import sys,subprocess,zipfile,shutil,mmap,json,time,traceback,hashlib
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_backend_probe');M={'status':'INSTALLING_ISOLATED_BACKEND','started':time.time(),'cases':[],'deletions':[]}
def save():(W/'ppmd_backend_probe_v2.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists();R.mkdir();save()
    with (W/'ppmd_backend_install_v2.log').open('wb') as f:subprocess.run([sys.executable,'-m','pip','install','--target',str(R/'lib'),'pyppmd==1.3.1'],stdout=f,stderr=subprocess.STDOUT,timeout=180,check=True)
    sys.path.insert(0,str(R/'lib'));import pyppmd
    with zipfile.ZipFile('/kaggle/working/hp_round7/preserved/data/enwik9.zip') as z:
        entries=[e for e in z.infolist() if e.file_size==1000000000];assert len(entries)==1
        with z.open(entries[0]) as f,(R/'original.bin').open('xb') as g:shutil.copyfileobj(f,g,4<<20)
    pages=[]
    with (R/'original.bin').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        p=data.find(b'<page>')
        while p>=0:
            e=data.find(b'</page>',p)
            if e<0:break
            e+=7;pages.append((p,e));p=data.find(b'<page>',e)
        assert len(pages)==243425
        for i,o,reverse in ((0,8,False),(2,16,True),(3,8,False)):
            start=(2*i+1)*len(pages)//32;inds=list(range(start,start+128));inds=inds[::-1] if reverse else inds
            raw=b''.join(data[a:b] for j in inds for a,b in [pages[j]]);label=f'region_{i}_{o}_{reverse}'
            (R/(label+'.raw')).write_bytes(raw)
            for variant in ('I','H'):
                payload=pyppmd.compress(raw,max_order=o,mem_size=64<<20,variant=variant)
                (R/(label+'_'+variant+'.ppmd')).write_bytes(payload)
                row={'region':i,'order':o,'reverse':reverse,'variant':variant,'input_bytes':len(raw),'archive_bytes':len(payload),'payload_sha256':hashlib.sha256(payload).hexdigest(),'tests':[]}
                for pad in ((0,1,8) if variant=='I' else (0,)):
                    try:
                        restored=pyppmd.decompress(payload+b'\0'*pad,max_order=o,mem_size=64<<20,variant=variant)
                        row['tests'].append({'padding':pad,'exact':restored==raw,'decoded_bytes':len(restored)})
                    except Exception as e:row['tests'].append({'padding':pad,'error':repr(e)})
                M['cases'].append(row);save()
    M.update(status='COMPLETE_REPRODUCED_BACKEND_PROBE',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
