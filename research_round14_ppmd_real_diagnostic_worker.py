from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import sys,json,zipfile,shutil,mmap,os,struct,time,traceback,hashlib
sys.path.insert(0,'/root/r14_ppmd_diagnostic/lib');sys.path.insert(0,'/root/r14_code_v2')
import pyppmd
from hutter_research.article_order_ppmd import compress,decompress
R=Path('/root/r14_ppmd_real');W=Path('/kaggle/working/hp_round14');PAGES=[]
def case(i):
    os.sched_setaffinity(0,{i});first=(2*i+1)*len(PAGES)//32;pages=[]
    with (R/'original.bin').open('rb') as f:
        for a,b in PAGES[first:first+128]:f.seek(a);pages.append(f.read(b-a))
    result=[]
    for level in (8,16):
        for name,indices in [('original',list(range(128))),('reverse',list(range(127,-1,-1)))]:
            raw=b''.join(pages[i] for i in indices);blob=compress(pages,indices,level);n,o,m,a,b,c=struct.unpack_from('<6I',blob,8);payload=blob[32+a+b:]
            row={'region':i,'order':level,'permutation':name,'input_bytes':len(raw),'payload_bytes':len(payload)}
            for label,fn in [('container',lambda:decompress(blob)==pages),('simple',lambda:pyppmd.decompress(payload,max_order=o,mem_size=m,variant='I')==raw),('bounded',lambda:pyppmd.Ppmd8Decoder(o,m).decode(payload,len(raw))==raw)]:
                try:row[label]={'exact':fn()}
                except Exception as e:row[label]={'error':repr(e)}
            if any(not r.get('exact') for k,r in row.items() if k in ('container','simple','bounded')):
                label=f'region_{i}_{level}_{name}';(R/(label+'.raw')).write_bytes(raw);(R/(label+'.hporder')).write_bytes(blob);row['failure_preserved']=label
            result.append(row)
    return result
M={'status':'PREPARING_REAL_DATA','started':time.time(),'cases':[]}
def save():(W/'ppmd_real_diagnostic_v1.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists();R.mkdir();save()
    with zipfile.ZipFile('/kaggle/working/hp_round7/preserved/data/enwik9.zip') as z:
        n=[r for r in z.infolist() if r.file_size==1000000000];assert len(n)==1
        with z.open(n[0]) as f,(R/'original.bin').open('xb') as g:shutil.copyfileobj(f,g,4<<20)
    with (R/'original.bin').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        p=data.find(b'<page>')
        while p>=0:
            b=data.find(b'</page>',p)
            if b<0:break
            b+=7;PAGES.append((p,b));p=data.find(b'<page>',b)
    assert len(PAGES)==243425
    with ProcessPoolExecutor(4) as pool:
        for rows in pool.map(case,range(4)):M['cases'].extend(rows);save()
    M.update(status='COMPLETE_DIAGNOSTIC',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
